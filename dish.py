#!/usr/bin/env python

import subprocess
import sys
import os
import time
import threading
from optparse import OptionParser

rsh = "/usr/kerberos/bin/rsh"
#rsh = "/usr/bin/rsh"

hostRangeResolver = "./host_range_resolver.py"


class Reader(threading.Thread):
	def __init__(self, hostname, stream):
		super(Reader, self).__init__()
		self.hostname = hostname
		self.stream = stream

	def run(self):
		while True:
			line = self.stream.readline()
			if not line:
				break
			print self.hostname, line.rstrip()

def executeRemoteCommand(host, command):
	popen = subprocess.Popen([rsh, host, command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return popen

def waitForTermination(popens):
	newPopens = []
	for popen in popens:
		if popen.poll() == None:
			popens.append(popen)
		else:
			print "pid %d returned %d" % (popen.pid, popen.returncode)
	return newPopens

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

def resolve_host_range(args):
    first = True
    result = []
    
    for arg in args:
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
                    # TODO: exception
                    print >> sys.stderr, 'invalid host range string'
                    sys.exit(1)
                for index in range(int(postfix0), int(postfix1) + 1):
                    result.append(prefix0 + str(index))
            else:
                # TODO: exception
                print >> sys.stderr, 'invalid host range string'
                sys.exit(1)

    return result

def resolveHostRange(args):
	newArgs = []
	newArgs.append(hostRangeResolver)
	newArgs.extend(args)
	#processHandle = subprocess.Popen(newArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	processHandle = subprocess.Popen(newArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(out, err) = processHandle.communicate()
	return out.split()

if(__name__ == "__main__"):
	usage = "%prog hostname command"
	optParser = OptionParser(usage)
	optParser.add_option("-c", dest="command", help="command to execute on remote machines", default="ls")
	(options, args) = optParser.parse_args()
	hosts = resolve_host_range(args)
	#print hosts
	#sys.exit(1)
	popens = []
	timeStart = time.time()
	for host in hosts:
		popen = executeRemoteCommand(host, options.command)
		popens.append(popen)
		stdoutReader = Reader(host, popen.stdout)
		stdoutReader.start()
		stderrReader = Reader(host, popen.stderr)
		stderrReader.start()
	while len(popens) > 0:
		popens = waitForTermination(popens)
		time.sleep(0.1)
	print "elapsed %.3f ms" % ((time.time() - timeStart) * 1000)


