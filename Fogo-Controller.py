#!/usr/bin/env python

import json
import getopt
import requests
import socket
import os
import sys

import subprocess
import signal
import fcntl
import struct

from uuid import getnode as get_mac
from flask import Flask
from flask_restful import Resource, Api

class bcolors:
    HEADER = '\033[1;37m'
    EXAMPLE = '\033[0;35m'
    ERROR = '\033[1;31m'
    VERBOSE = '\033[1;35m'
    ENDC = '\033[0m'

def usage():
	print(bcolors.HEADER + "NAME" + bcolors.ENDC)
	print("        Fogo-Controller - A simple Python HTTP Restful server for the Fogo Controller Android and iOS APP.")
	print(bcolors.HEADER + "SYNOPSIS" + bcolors.ENDC)
	print("        Fogo-Controller <MACHINE NAME> <SERVER IP> [OPTIONS]")
	print(bcolors.HEADER + "DESCRIPTION" + bcolors.ENDC)
	print("        Initiate a HTTP Rest server and wait for commands to control the Fogo Suite.")
	print("        -m or --machine=NAME")
	print("            The machine name displayed by the mobile application")
	print("        -i or --ip=IP")
	print("            The server ip to communticate with.")
	print("        -n or --network=INTERFACE")
	print("            The used network interface(eth0 is default)")
	print("        -v or --verbose")
	print("            Active verbosity")
	print(bcolors.HEADER + "EXIT STATUS" + bcolors.ENDC)
	print("        0 - If ok")
	print("        1 - If failed")
	print(bcolors.HEADER + "USE EXAMPLE" + bcolors.ENDC)
	print(bcolors.EXAMPLE + "        Fogo-Controller.py --machine=Fogo1 --ip=192.168.0.2 --network=eth1" + bcolors.ENDC)
	return

def valid_dict(dict):
	valid = ["network", "machine", "ip"]

	for key in dict:
		if key != "verbose":
			valid.remove(key)
	if len(valid) == 0:
		return True
	else:
		return False

def parse_arguments():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'vm:i:n:', ['machine=', 'ip=', 'network=', 'verbose'])
	except getopt.GetoptError:
		usage()
		sys.exit(1)

	information = {}
	information.update({"network" : "eth0"})

	for opt, arg in opts:
	    if opt in ('-m', '--machine'):
	        information["machine"] = arg
	    elif opt in ('-i', '--ip'):
	        information["ip"] = arg
	    elif opt in ('-n', '--network'):
	        information["network"] = arg
	    elif opt in ('-v', '--verbose'):
	        information["verbose"] = "on"
	    else:
	        usage()
	        sys.exit(1)

	if not valid_dict(information):
		usage()
		sys.exit(1)
	return information 

def verbose(text, active):
	if active:
		print(bcolors.VERBOSE + "--" +text + bcolors.ENDC)
	return

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

def send_info(network, machine_name, ip_address):
	local_ip = get_ip_address(network)

	mac = get_mac()

	name = machine_name
	try:
		r = requests.post("http://" + ip_address + ":3000/fogo_machines/new", data=json.dumps({"name" : name, "ip" : str(local_ip), "mac" : str(mac)}), headers={"content-type": "application/json"}, timeout=3.0)
	except:
		print(bcolors.ERROR + "Communication to server failed. Is it running?" + bcolors.ENDC)
		sys.exit(1)
	return

def terminate(name):
    try:
        subprocess.call("killall -9 " + name, shell=True)
    except:
        print "already killed"
    return

class Decoder(Resource):	    
    def get(self, state):
	if state == "on":
	    p = subprocess.Popen(["~/FOGO-2015/Debug/run_decoder.sh"], stdout=subprocess.PIPE, shell=True)
	else:
	    terminate("fogo_decoder_video")
        
        return {'response': 'decoder_ok'}
class Buffer(Resource):
    def get(self):
    	os.system("sudo sysctl -w net.core.rmem_max=5000000000000000000")
        return {'response': 'buffer_ok'}
class Ptp(Resource):
    def get(self, state):
	if state == "on":
		p = subprocess.Popen(["ptpd2 -i eth0 -s"], stdout=subprocess.PIPE, shell=True)
	else:
		terminate("ptpd2")
        return {'response': 'sender_ok'}


if __name__ == '__main__':
	information = parse_arguments()
	active_verbose = information.has_key("verbose")

	verbose("Arguments successfuly parsed", active_verbose)
	
	send_info(information["network"], information["machine"], information["ip"])
	
	verbose("Sending local information to server", active_verbose)
	
	print(bcolors.HEADER + "Fogo-Controller is now running." +bcolors.ENDC)
	app = Flask(__name__)
	api = Api(app)
	
	verbose("Preparing server", active_verbose)

	api.add_resource(Buffer, '/increase_buffer')
	api.add_resource(Decoder, '/run_decoder/<state>')
	api.add_resource(Ptp, '/run_ptp/<state>')

	verbose("Starting server", active_verbose)

	app.run(host="0.0.0.0", debug=False, use_reloader=False)
else:
	print("This script is not a module!\n\n")
	print("Please visit https://github.com/caiomcg/Fogo-Controller")