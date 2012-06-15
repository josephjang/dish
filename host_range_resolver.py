#! /usr/bin/env python

import sys

#
# 'foo01~foo03,foo05,foo10' resolved to 'foo01 foo02 foo03 foo05 foo10'
#

def parse_hostname(hostname):
    final = len(hostname)
    for index in range(len(hostname)):
        if hostname[index:].isdigit():
            final = index
            break
    return hostname[:final], hostname[final:]

first = True
result = []

for arg in sys.argv[1:]:
    tokens = arg.split(',')
    for token in tokens:
        hosts = token.split('~')
        hosts_len =  len(hosts)
        if first == True:
            first = False
        if hosts_len == 1:
            result.append(hosts[0])
        elif hosts_len == 2:
            # hosts should share non-numeric substring
            prefix0, postfix0 = parse_hostname(hosts[0])
            prefix1, postfix1 = parse_hostname(hosts[1])
            if prefix0 != prefix1:
                print >> sys.stderr, 'invalid host range string'
                sys.exit(1)
            for index in range(int(postfix0), int(postfix1) + 1):
                result.append(prefix0 + str(index))
        else:
            print >> sys.stderr, 'invalid host range string'
            sys.exit(1)

print " ".join(result)

