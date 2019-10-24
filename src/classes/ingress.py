#!/usr/bin/env python3


class Ingress:

    def __init__(self, kube_connector, resource):
        self.__resource = resource
        self.__kube_connector = kube_connector
        self.__extract_meta()
        self.__extract_backends()

    def __extract_meta(self):
        self.name = self.__resource.metadata.name
        self.namespace = self.__resource.metadata.namespace

    def __extract_backends(self):
        backends = {}
        for rule in self.__resource.spec.rules:
            if rule.host not in backends:
                backends[rule.host] = []
            for path in rule.http.paths:
                backends[rule.host].append((
                    path.backend.service_name,
                    path.backend.service_port
                ))
        self.backends = backends
