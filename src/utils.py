#!/usr/bin/env python3
from difflib import SequenceMatcher

# compare strings


def compare_strings(a, b, cache={}):
    cache_key = (a, b)
    if cache_key in cache:
        return cache[cache_key]
    match_ratio = SequenceMatcher(None, a, b).ratio()
    good_ratio = (1 - 3 / (len(a) + len(b)))
    cache[cache_key] = match_ratio >= good_ratio
    return cache[cache_key]

# join strings


def join_strings(*args, cache={}):
    cache_key = (args,)
    if cache_key in cache:
        return cache[cache_key]
    args = [str(arg) for arg in args if arg != '']
    args = sorted(args, key=len, reverse=True)
    left = ''
    left_padding = 0
    while left_padding < len(args[0]) and all(left_padding < len(arg) and arg[left_padding] == args[0][left_padding] for arg in args):
        left += args[0][left_padding]
        left_padding += 1
    if left == args[0]:
        cache[cache_key] = left
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
    cache[cache_key] = ret
    return ret


def group_similars(*args):
    skip = set()
    groups = list()
    for a in args:
        if a in skip:
            continue
        group = set()
        skip.add(a)
        group.add(a)
        for b in args:
            if b in skip:
                continue
            if compare_strings(a, b):
                skip.add(b)
                group.add(b)
        groups.append(group)
    return groups
