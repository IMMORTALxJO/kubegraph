#!/usr/bin/env python3
from src.utils import group_similars, join_strings


class Graph:

    def __init__(self, *args, **kwargs):
        self.nodes = set()
        self.edges = set()
        self.group_similars = True
        self.connections = {}

    def add_edge(self, src, dst):
        if src not in self.connections:
            self.connections[src] = set()
        self.nodes.add(src)
        GraphNode.hidden_schemes_for_hostnames.add(src.hostname)
        self.connections[src].add(dst)
        self.edges.add((src, dst))

    def __iter__(self):
        self.__iter = (x for x in self.edges)
        return self

    def __next__(self):
        return self.__iter.__next__()

    @property
    def json(self):
        result = {}
        for node in self.nodes:
            hostnames = []
            if self.group_similars:
                for group in group_similars(self.connections[node]):
                    if len(group) > 1 and all(
                            group in group_similars(self.connections[x])
                            for x in self.nodes
                            if self.connections[x] <= self.connections[node] or self.connections[node] <= self.connections[x]
                    ):
                        hostnames += [join_strings(group)]
                    else:
                        hostnames += [str(x) for x in group]
            else:
                hostnames += [str(x) for x in self.connections[node]]
            result[str(node)] = sorted(hostnames)
        return result


class GraphNode:

    hidden_schemes = []
    hidden_schemes_for_hostnames = set()

    def __init__(self, scheme, hostname, port):
        self.scheme = scheme
        self.hostname = hostname
        self.port = str(port)

    @property
    def __key(self):
        return (self.scheme, self.hostname, self.port)

    def __str__(self):
        result = ''
        if self.scheme and self.scheme not in self.hidden_schemes and self.hostname not in self.hidden_schemes_for_hostnames:
            result += '%s://' % self.scheme
        result += self.hostname
        return result

    def __hash__(self):
        return hash(self.__key)

    def __eq__(self, candidate):
        if isinstance(candidate, GraphNode):
            return self.__hash__() == candidate.__hash__()
        return NotImplemented
