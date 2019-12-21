#!/usr/bin/env python3
from src.kube_connector import KubeConnector
from src.classes.pod_with_hostnames import PodWithHostnames
from src.classes.service import Service
from src.classes.ingress import Ingress
from src.classes.inventory import Inventory

Inventory.system_schemes = set(['pod', 'ingress', 'svc'])


class KubeGraph(Inventory):
    defaults = {
        "kubeconfig": "~/.kube/config",
        "namespace": False,
        "ignore_substrings": "pass,token,secret,hash,salt,_id,allow",
        "selector": ""
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = {}
        self.pods = []
        self.svcs = []
        for (key, value) in self.defaults.items():
            self.options[key] = kwargs[key] if key in kwargs else value
        self.kube_connector = KubeConnector(
            namespace=self.options['namespace'],
            kubeconfig=self.options['kubeconfig'],
            selector=self.options['selector']
        )

    def collect_services(self):
        for svc_resource in self.kube_connector.get_services():
            svc = Service(self.kube_connector, svc_resource)
            for pod in self.pods:
                if not svc.selector:
                    continue
                if svc.selector.items() <= pod.labels.items():
                    self.add_edge(svc.name, pod.name, 'pod', group=svc.namespace)
            self.svcs.append(svc)

    def collect_ingresses(self):
        for ingress_resource in self.kube_connector.get_ingresses():
            ingress = Ingress(self.kube_connector, ingress_resource)
            for domain, rules in ingress.backends.items():
                for (service_name, _) in rules:
                    self.add_edge(domain, service_name, 'svc', group=ingress.namespace)

    def collect_pods(self):
        for pod_resource in self.kube_connector.get_pods():
            pod = PodWithHostnames(self.kube_connector, pod_resource)
            pod.filter_envs(self.options['ignore_substrings'])
            for (scheme, hostname, _) in pod.hostnames:
                self.add_edge(pod.name, hostname, scheme, group=pod.namespace)
            self.pods.append(pod)
