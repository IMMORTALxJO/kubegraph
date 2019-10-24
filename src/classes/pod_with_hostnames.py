#!/usr/bin/env python3
from src.utils import extract_hostnames_from_string, get_scheme_from_string, get_scheme_from_port, get_port_from_scheme, get_port_from_environment_vars
from src.classes.pod import Pod


class PodWithHostnames(Pod):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env_to_hostnames = {}
        self.hostnames = []
        self.__extract_hostnames()
        self.__update_hostnames()

    def filter(self, filter_rules) -> object:
        super().filter(filter_rules)
        self.env_to_hostnames = {
            env_name: hostnames
            for env_name, hostnames in self.env_to_hostnames.items()
            if env_name in self.env
        }
        self.__update_hostnames()

    def __extract_hostnames(self):
        env_to_hostnames = {}
        for env_name, env_value in self.env.items():
            enriched_hostnames = []
            extracted_hostnames = extract_hostnames_from_string(env_value)
            for (scheme, hostname, port) in extracted_hostnames:
                if not scheme:
                    scheme = get_scheme_from_string(env_name)
                if not scheme:
                    scheme = get_scheme_from_string(hostname)
                if not port:
                    port = get_port_from_environment_vars(env_name, self.env)
                if not scheme and port:
                    scheme = get_scheme_from_port(port)
                if not port and scheme:
                    port = get_port_from_scheme(scheme)
                enriched_hostnames.append((scheme, hostname, port))
            env_to_hostnames[env_name] = enriched_hostnames
        self.env_to_hostnames = env_to_hostnames

    def __update_hostnames(self):
        hostnames = []
        for env_hostnames in self.env_to_hostnames.values():
            hostnames += env_hostnames
        self.hostnames = list(set(hostnames))

    def __len__(self):
        return len(self.hostnames)
