#!/usr/bin/env python3
from difflib import SequenceMatcher
from urllib.parse import urlparse
from src.scheme_mappings import PORTS_TO_SCHEMES, SCHEMES_TO_PORTS, NAMES_TO_SCHEMES
import socket
import re

# compare strings


COMPARE_STRINGS_CACHE = {}


def compare_strings(first, second):
    """
    Check if strings are simillar:
    kafka-1.test, kafka-2.test => true
    kafka-1.test, mongodb-2.test => false
    """
    cache_key = (first, second)
    if cache_key in COMPARE_STRINGS_CACHE:
        return COMPARE_STRINGS_CACHE[cache_key]
    match_ratio = SequenceMatcher(None, first, second).ratio()
    good_ratio = (1 - 3 / (len(first) + len(second)))
    COMPARE_STRINGS_CACHE[cache_key] = match_ratio >= good_ratio
    return COMPARE_STRINGS_CACHE[cache_key]


JOIN_STRINGS_CACHE = {}


def join_strings(strings):
    """
    Join strings:
    kafka-1.test, kafka-2.test => kafka-{1,2}.test
    """
    cache_key = tuple(strings)
    if cache_key in JOIN_STRINGS_CACHE:
        return JOIN_STRINGS_CACHE[cache_key]
    args = [str(arg) for arg in strings if arg != '']
    args = sorted(args, key=len, reverse=True)
    left = ''
    left_padding = 0
    while left_padding < len(args[0]) and all(left_padding < len(arg) and arg[left_padding] == args[0][left_padding] for arg in args):
        left += args[0][left_padding]
        left_padding += 1
    if left == args[0]:
        JOIN_STRINGS_CACHE[cache_key] = left
        return left
    right = ''
    right_padding = -1
    while all(arg[right_padding] == args[0][right_padding] for arg in args):
        right = args[0][right_padding] + right
        right_padding -= 1
    right_padding += 1
    diff = [arg[left_padding:(len(arg) + right_padding)] for arg in args]
    diff = sorted((set(diff)))
    ret = '%s{%s}%s' % (left, str.join(',', diff), right)
    JOIN_STRINGS_CACHE[cache_key] = ret
    return ret


def group_similars(strings):
    """
    Join simillar strings:
    kafka-1.test, mongodb-1, kafka-2.test, mongodb-2 => [ {kafka-1.test, kafka-2.test}, {mognodb-1, mongodb-2} ]
    """
    skip = set()
    groups = []
    for a in strings:
        if a in skip:
            continue
        group = set()
        skip.add(a)
        group.add(a)
        for b in strings:
            if b in skip:
                continue
            if compare_strings(str(a), str(b)):
                skip.add(b)
                group.add(b)
        groups.append(group)
    return groups


def is_string_ignored(string, ignored_substrings=""):
    """Check if string contains substrings"""
    lstr = str.lower(string)
    return not all(str.lower(x) not in lstr for x in ignored_substrings.split(",") if len(x) > 0)


def extract_hostnames_from_string(value):
    """
    Detect if string is looking like address and return list of sets of ( scheme, hostname, port ) :
        "http://example.com" -> ("http", "example.com", False)
        "example.com" -> (False, "example.com", False)
        "mysqlserver.default" ( service ) -> (False, "mysqlserver.default", False )
        "mysqlserver" ( service )  -> (False, "mysqlserver.default", False )
    """
    results = []
    for candidate in value.split(","):
        result = False
        if '://' in candidate:  # https://api-server
            result = urlparse(candidate)
        elif re.compile(r"[^:]*:\d+").match(candidate):  # kafka:8200
            result = urlparse('unknown://%s' % candidate)
        elif '.' in candidate:  # google.com
            try:
                socket.gethostbyname(candidate)
                result = urlparse('unknown://%s' % candidate)
            except Exception:
                pass
        if not result or not result.hostname or result.hostname in ('0.0.0.0', '127.0.0.1'):
            continue
        scheme = result.scheme if result.scheme != 'unknown' else None
        results.append((scheme, result.hostname, result.port))
    return results


def get_scheme_from_string(value):
    """
    Return scheme based on string substrings
        MYSQL_HOST -> mysql
    """
    low_value = str.lower(value)
    for schema, keys in NAMES_TO_SCHEMES.items():
        for key in keys:
            if key in low_value:
                return schema
    return None


def get_scheme_from_port(num):
    """
    Return scheme based on port
        3306 -> mysql
    """
    if str(num) in PORTS_TO_SCHEMES:
        return PORTS_TO_SCHEMES[str(num)]
    return None


def get_port_from_scheme(scheme):
    """
    Return scheme based on port
        mysql -> 3306
    """
    if scheme in SCHEMES_TO_PORTS:
        return SCHEMES_TO_PORTS[scheme]
    return None


def get_port_from_environment_vars(env_name, pod_envs):
    """Return port based on pod environment variables"""
    def get_prefix(string):
        return str.join('_', string.split('_')[:-1])
    prefix = get_prefix(env_name)
    for (key, value) in pod_envs.items():
        if key.split('_')[-1:][0].lower() == 'port' and prefix == get_prefix(key):
            return value
    return None
