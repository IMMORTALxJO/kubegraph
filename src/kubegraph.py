#!/usr/bin/env python3
from src.kube_connector import KubeConnector
from src.classes.pod_with_hostnames import PodWithHostnames
from src.classes.service import Service
from src.classes.ingress import Ingress
from src.classes.graph import GraphNode, Graph

GraphNode.hidden_schemes = ['k8s-pod', 'k8s-svc', 'k8s-ingress']


class KubeGraph(Graph):

    defaults = {
        "kubeconfig": "~/.kube/config",
        "namespace": False,
        "ignore_substrings": "pass,token,secret,hash,salt,_id,allow",
        "label_selector": ""
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = {}
        self.pods = []
        for (key, value) in self.defaults.items():
            self.options[key] = kwargs[key] if key in kwargs else value
        self.kube_connector = KubeConnector(
            namespace=self.options['namespace'],
            kubeconfig=self.options['kubeconfig'],
            label_selector=self.options['label_selector']
        )

    def collect_services(self):
        for svc_resource in self.kube_connector.get_services():
            svc = Service(self.kube_connector, svc_resource)
            svc.graph_node = GraphNode('k8s-svc', svc.name, None)
            for pod in self.pods:
                if not svc.selector:
                    continue
                if svc.selector.items() <= pod.labels.items():
                    self.add_edge(svc.graph_node, pod.graph_node)

    def collect_ingresses(self):
        for ingress_resource in self.kube_connector.get_ingresses():
            for hostname, rules in Ingress(self.kube_connector, ingress_resource).backends.items():
                for (service_name, service_port) in rules:
                    self.add_edge(
                        GraphNode('k8s-ingress', hostname, None),
                        GraphNode('k8s-ingress', service_name, service_port)
                    )

    def collect_pods(self):
        for pod_resource in self.kube_connector.get_pods():
            pod = PodWithHostnames(self.kube_connector, pod_resource)
            pod.filter(self.options['ignore_substrings'])
            pod.graph_node = GraphNode('k8s-pod', pod.name, None)
            for (scheme, hostname, port) in pod.hostnames:
                self.add_edge(pod.graph_node, GraphNode(scheme, hostname, port))
            self.pods.append(pod)
