#!/usr/bin/env python3
from kubernetes import client, config


class KubeConnector:
    clients = False
    opt_namespace = False
    opt_kubeconfig = "~/.kube/config"
    opt_label_selector = ""

    def __init__(self, **kwargs):
        if not self.clients:
            self.opt_namespace = kwargs.get("namespace", self.opt_namespace)
            self.opt_kubeconfig = kwargs.get("kubeconfig", self.opt_kubeconfig)
            self.opt_label_selector = kwargs.get("label_selector", self.opt_label_selector)
            config.load_kube_config(config_file=self.opt_kubeconfig)
            self.clients = {
                "v1": client.CoreV1Api(),
                "v1beta1": client.ExtensionsV1beta1Api()
            }

    def __get_resource(self, kind, client_version='v1'):
        opts = {
            "watch": False,
            "label_selector": self.opt_label_selector
        }
        if self.opt_namespace:
            return getattr(self.clients[client_version], "list_namespaced_%s" % kind)(self.opt_namespace, **opts).items
        return getattr(self.clients[client_version], "list_%s_for_all_namespaces" % kind)(**opts).items

    def get_pods(self):
        return self.__get_resource('pod')

    def get_services(self):
        return self.__get_resource('service')

    def get_ingresses(self):
        return self.__get_resource('ingress', client_version='v1beta1')

    __get_configmap_data_by_name_cache = {}

    def get_namespaced_configmap_data(self, namespace, configmap_name):
        cache_key = "%s.%s" % (namespace, configmap_name)
        if cache_key not in self.__get_configmap_data_by_name_cache:
            self.__get_configmap_data_by_name_cache[cache_key] = self.clients['v1'].list_namespaced_config_map(
                namespace, field_selector='metadata.name=%s' % configmap_name, watch=False).items[0].data
        return self.__get_configmap_data_by_name_cache[cache_key]
