#!/usr/bin/env python3
from src.utils import group_similars, join_strings


class Inventory:

    system_schemes = set()

    def __init__(self, *args, **kwargs):
        self.hostnames = {}
        self.__connections = {}
        self.edges = set()
        self.nodes = set()
        self.groups = set()

    def add_host(self, hostname, scheme=None):
        if hostname not in self.hostnames or scheme and scheme in self.system_schemes:
            self.hostnames[hostname] = scheme

    def get_host(self, hostname):
        if hostname not in self.hostnames:
            return None
        if not self.hostnames[hostname] or self.hostnames[hostname] in self.system_schemes:
            return hostname
        return '%s://%s' % (self.hostnames[hostname], hostname)

    def add_edge(self, src, dst, scheme, group=None):
        connect = (src, dst, scheme)
        if connect in self.edges:
            return
        if src not in self.__connections:
            self.__connections[src] = set()
        if dst not in self.__connections:
            self.__connections[dst] = set()
        if group:
            self.groups.add(group)
        self.add_host(dst, scheme)
        self.add_host(src)
        self.edges.add(connect)
        self.__connections[src].add(dst)
        self.__connections[dst].add(src)

    @property
    def json(self):
        edges = {}
        result = {}
        for (src, dst, _) in self.edges:
            if src not in edges:
                edges[src] = []
            edges[src].append(dst)

        for src, hostnames in edges.items():
            groupped_hostnames = []
            for group in group_similars(hostnames):
                if len(group) > 1 and all(
                    group in group_similars(self.__connections[item])
                    for x in group
                    for item in self.__connections[x]
                ):
                    groupped_hostnames += [join_strings([self.get_host(x) for x in group])]
                else:
                    groupped_hostnames += [self.get_host(x) for x in group]
            groupped_hostnames = [x for x in groupped_hostnames if x != src]
            if groupped_hostnames:
                result[self.get_host(src)] = sorted(groupped_hostnames)
        return result
