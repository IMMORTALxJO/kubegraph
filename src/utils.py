#!/usr/bin/env python3
from difflib import SequenceMatcher

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


def join_strings(*args):
    """
    Join strings:
    kafka-1.test, kafka-2.test => kafka-{1,2}.test
    """
    cache_key = (args,)
    if cache_key in JOIN_STRINGS_CACHE:
        return JOIN_STRINGS_CACHE[cache_key]
    args = [str(arg) for arg in args if arg != '']
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


def group_similars(*args):
    """
    Join simillar strings:
    kafka-1.test, mongodb-1, kafka-2.test, mongodb-2 => [ {kafka-1.test, kafka-2.test}, {mognodb-1, mongodb-2} ]
    """
    skip = set()
    groups = []
    for arg in args:
        if arg in skip:
            continue
        group = set()
        skip.add(arg)
        group.add(arg)
        for barg in args:
            if barg in skip:
                continue
            if compare_strings(arg, barg):
                skip.add(barg)
                group.add(barg)
        groups.append(group)
    return groups
