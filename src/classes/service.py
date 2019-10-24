#!/usr/bin/env python3


class Service:

    def __init__(self, kube_connector, resource):
        self.__resource = resource
        self.__kube_connector = kube_connector
        self.__extract_meta()

    def __extract_meta(self):
        self.namespace = self.__resource.metadata.namespace
        self.name = self.__resource.metadata.name
        self.selector = self.__resource.spec.selector
        self.labels = self.__resource.metadata.labels if self.__resource.metadata.labels else {}
