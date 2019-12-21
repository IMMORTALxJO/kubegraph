#!/usr/bin/env python3
from src.utils import is_string_ignored


class Pod:

    def __init__(self, kube_connector, resource):
        self.env = {}
        self.__resource = resource
        self.__kube_connector = kube_connector
        self.__extract_meta()
        self.__extract_environments()

    def __extract_meta(self):
        self.namespace = self.__resource.metadata.namespace
        self.name = self.__resource.metadata.name
        self.labels = self.__resource.metadata.labels if self.__resource.metadata.labels else {}

    def __extract_environments(self):
        # https://kubernetes.io/docs/tasks/inject-data-application/define-environment-variable-container/#define-an-environment-variable-for-a-container
        result = {}
        for container in self.__resource.spec.containers:
            # spec:
            #   containers:
            if container.env:
                #  env:
                for var in container.env:
                    if var.value_from:
                        #    - name: VAR2
                        #      valueFrom:
                        if var.value_from.config_map_key_ref:
                            #        configMapKeyRef:
                            #          name: config
                            #          key: keyname
                            configmap_data = self.__kube_connector.get_namespaced_configmap_data(self.namespace, var.value_from.config_map_key_ref.name)
                            if var.value_from.config_map_key_ref.key in configmap_data:
                                result[var.name] = configmap_data[var.value_from.config_map_key_ref.key]
                    else:
                        #    - name: VAR
                        #      value: VAL
                        result[var.name] = var.value
            if container.env_from:
                #  - envFrom:
                #    - configMapRef:
                #        name: configmap
                for var in container.env_from:
                    if var.config_map_ref:
                        configmap_data = self.__kube_connector.get_namespaced_configmap_data(self.namespace, var.config_map_ref.name)
                        result.update(configmap_data)
        self.env = result

    def filter_envs(self, filter_rules):
        self.env = {
            env_name: env_value
            for env_name, env_value in self.env.items()
            if not is_string_ignored(env_name, filter_rules)
        }

    def __len__(self):
        return len(self.env)
