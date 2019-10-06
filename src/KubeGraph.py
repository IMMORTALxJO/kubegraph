#!/usr/bin/env python3
from kubernetes import client, config
from src.utils import group_similars, join_strings
from urllib.parse import urlparse
import socket
import re
import json


class KubeGraph:
    defaults = {
        "kubeconfig": "~/.kube/config",
        "namespace": "",
        "ignore_substrings": "pass,token,secret,hash,salt,_id,allow",
        "output_format": "graphviz",
        "hide_pods_in_service": True,
        "label_selector": "",
        "pod_label_selector": "",
        "ingress_label_selector": "",
        "svc_label_selector": ""
    }
    output_formats = ["graphviz", "mermaidjs", "json"]
    schema_to_name_map = {
        "mysql": ("mysql",),
        "pgsql": ("postgre", "pgsql"),
        "mongo": ("mongo", "documentdb",),
        "redis": ("redis",),
        "kafka": ("kafka",),
        "rabbitmq": ("rabbit",),
        "vertica": ("vertica",),
        "memcache": ("memcache",),
        "aerospike": ("aerospike",),
        "smtp": ("smtp",)
    }

    def __init__(self, *args, **kwargs):
        self.graph = {}
        self.services = {}
        self.pods = {}
        self.ingresses = {}
        self.clients = {}
        self.options = {}
        for (key, value) in self.defaults.items():
            if key in kwargs:
                self.options[key] = kwargs[key]
            else:
                self.options[key] = value
        self.options["ignore_substrings"] = set([str.lower(x) for x in str.split(self.options["ignore_substrings"], ',')])
        if self.options["namespace"] == "":
            self.options["namespace"] = False
        if self.options["label_selector"] != "":
            self.options["pod_label_selector"] = self.options["label_selector"]
            self.options["svc_label_selector"] = self.options["label_selector"]
            self.options["ingress_label_selector"] = self.options["label_selector"]

    def init_client(self):
        config.load_kube_config(config_file=self.options["kubeconfig"])
        self.clients['v1'] = client.CoreV1Api()
        self.clients['v1beta1'] = client.ExtensionsV1beta1Api()

    def collect_services(self):
        if self.options["namespace"]:
            svcs_list = self.clients['v1'].list_namespaced_service(
                self.options["namespace"], label_selector=self.options["svc_label_selector"], watch=False).items
        else:
            svcs_list = self.clients['v1'].list_service_for_all_namespaces(label_selector=self.options["svc_label_selector"], watch=False).items
        for service in svcs_list:
            if service.metadata.name == 'kubernetes':
                continue
            label_selector = []
            if not service.spec.selector:
                continue
            for k in service.spec.selector:
                label_selector.append('%s=%s' % (k, service.spec.selector[k]))
            label_selector = str.join(',', label_selector)
            pods = set()
            for pod in self.clients['v1'].list_namespaced_pod(service.metadata.namespace, label_selector=label_selector, watch=False).items:
                pods.add(pod.metadata.name)
            service_name = '%s.%s' % (service.metadata.name, service.metadata.namespace)
            svc = {
                "service_name": service_name,
                "pods": pods
            }
            self.services[service_name] = svc
            self.services['%s.svc' % service_name] = svc
            self.services['%s.svc.cluster' % service_name] = svc
            self.services['%s.svc.cluster.local' % service_name] = svc

    def collect_pods(self):
        def get_config_map_vars(namespace, configmap, cache={}):
            cache_key = '%s/%s' % (namespace, configmap)
            if cache_key in cache:
                return cache[cache_key]
            config = self.clients['v1'].list_namespaced_config_map(namespace, field_selector='metadata.name=%s' % configmap, watch=False).items[0]
            cache[cache_key] = config.data
            return cache[cache_key]
        if self.options["namespace"]:
            pods_list = self.clients['v1'].list_namespaced_pod(self.options["namespace"], label_selector=self.options["pod_label_selector"], watch=False).items
        else:
            pods_list = self.clients['v1'].list_pod_for_all_namespaces(label_selector=self.options["pod_label_selector"], watch=False).items
        for pod in pods_list:
            pod_env = {}
            for container in pod.spec.containers:
                # spec:
                #  containers:
                #  - env:
                #    - name: VAR
                #      value: VAL
                #    - name: VAR2
                #      valueFrom:
                #        configMapKeyRef:
                #          name: config
                #          key: config.key
                if container.env:
                    for var in container.env:
                        if var.value_from:
                            if var.value_from.config_map_key_ref:
                                config_map = get_config_map_vars(pod.metadata.namespace, var.value_from.config_map_key_ref.name)
                                if var.value_from.config_map_key_ref.key in config_map:
                                    pod_env[var.name] = config_map[var.value_from.config_map_key_ref.key]
                            continue
                        pod_env[var.name] = var.value
                # spec:
                #  containers:
                #  - envFrom:
                #    - configMapRef:
                #        name: configmap
                if container.env_from:
                    for var in container.env_from:
                        if var.config_map_ref:
                            for name, value in get_config_map_vars(pod.metadata.namespace, var.config_map_ref.name).items():
                                pod_env[name] = value
                # TODO: last change - exec `env` inside a pod if len(pod_envs) == 0
            pod.env = [(name, value) for (name, value) in pod_env.items() if self.filter_ignored_string(str.lower(name))]
            self.pods[pod.metadata.name] = pod

    def collect_ingresses(self):
        if self.options["namespace"]:
            ingresses_list = self.clients['v1beta1'].list_namespaced_ingress(
                self.options["namespace"], label_selector=self.options["ingress_label_selector"], watch=False).items
        else:
            ingresses_list = self.clients['v1beta1'].list_ingress_for_all_namespaces(label_selector=self.options["ingress_label_selector"], watch=False).items
        for ingress in ingresses_list:
            for rule in ingress.spec.rules:
                services = set()
                for path in rule.http.paths:
                    services.add('%s.%s' % (path.backend.service_name, ingress.metadata.namespace))
                self.ingresses[rule.host] = services

    def filter_ignored_string(self, value):
        for stop_substring in self.options["ignore_substrings"]:
            if stop_substring in value:
                return False
        return True

    def is_string_address(self, namespace, value, cache={}):
        if value in cache:
            return cache[value]
        parsed_hostname = False
        if value in self.services:  # mysqlserver
            parsed_hostname = value
        elif ('%s.%s' % (value, namespace)) in self.services:  # mysqlserver.default
            parsed_hostname = value
        elif '://' in value:  # https://api-server
            parsed_hostname = urlparse(value).hostname
        elif re.compile(r"[^:]*:\d+").match(value):  # kafka:8200
            parsed_hostname = urlparse('tcp://%s' % value).hostname
        elif '.' in value:  # google.com
            try:
                socket.gethostbyname(value)
                parsed_hostname = urlparse('http://%s' % value).hostname
            except Exception:
                pass
        if parsed_hostname and parsed_hostname not in ('0.0.0.0', '127.0.0.1'):
            if '%s.%s' % (parsed_hostname, namespace) in self.services:
                parsed_hostname = '%s.%s' % (parsed_hostname, namespace)
            cache[value] = parsed_hostname
        else:
            cache[value] = False
        return cache[value]

    def get_schema_from_name(self, env_name):
        low_name = str.lower(env_name)
        for schema, keys in self.schema_to_name_map.items():
            for key in keys:
                if key in low_name:
                    return '%s://' % schema
        return ""

    def generate_graph(self):
        for pod_name, pod in self.pods.items():
            env_hostnames = set()
            for (name, value) in pod.env:
                for candidate in value.split(','):
                    parsed_address = self.is_string_address(pod.metadata.namespace, candidate)
                    if parsed_address:
                        schema = self.get_schema_from_name(name)
                        env_hostnames.add('%s%s' % (schema, parsed_address))
            groupped_values = [join_strings(*sim_group) for sim_group in group_similars(*env_hostnames)]
            if len(groupped_values) > 0:
                self.graph[pod_name] = groupped_values
        for (_, svc) in self.services.items():
            service_name = svc['service_name']
            if self.options['hide_pods_in_service']:
                for pod in svc['pods']:
                    if pod in self.graph:
                        self.graph[service_name] = self.graph[pod]
                        del self.graph[pod]
            else:
                self.graph[service_name] = svc['pods']

        for (domain, services) in self.ingresses.items():
            for service in services:
                self.graph[domain] = [service]

    def output(self):
        if self.options['output_format'] == 'graphviz':
            print("### http://www.webgraphviz.com/\ndigraph g{\nrankdir=LR;")
            for (edge, targets) in self.graph.items():
                for target in targets:
                    if target != edge:
                        print('"%s" -> "%s"' % (edge, target))
            print('}')
        elif self.options['output_format'] == 'json':
            print(json.dumps(self.graph, indent=4, sort_keys=True))
        elif self.options['output_format'] == 'mermaidjs':
            print("### https://mermaidjs.github.io/mermaid-live-editor/\ngraph LR")
            for (edge, targets) in self.graph.items():
                for target in targets:
                    if target != edge:
                        print('%s("%s") --> %s("%s")' % (str(hash(edge)), edge, str(hash(target)), target))
