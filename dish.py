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
	hosts = resolveHostRange(args)
	#print hosts
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


