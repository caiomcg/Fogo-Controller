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

from flask import Flask
from flask_restful import Resource, Api

def usage():
	print("NAME")
	print("        Fogo-Controller - A simple Python HTTP Restful server for the Fogo Controller Android and iOS APP.")
	print("SYNOPSIS")
	print("        Fogo-Controller <MACHINE NAME> <SERVER IP> [OPTIONS]")
	print("DESCRIPTION")
	print("        Initiate a HTTP Rest server and wait for commands to control the Fogo Suite.")
	print("        -m or --machine=NAME")
	print("            The machine name displayed by the mobile application")
	print("        -i or --ip=IP")
	print("            The server ip to communticate with.")
	print("        -n or --network=INTERFACE")
	print("            The used network interface(eth0 is default")
	print("EXIT STATUS")
	print("        0 - If ok")
	print("        1 - If failed")
	print("USE EXAMPLE")
	print("        Fogo-Controller.py --machine=Fogo1 --ip=192.168.0.2 --network=eth1")
	return

def parse_arguments():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'm:i:n:', ['machine=', 'ip=', 'network='])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	information = {}
	information.update({"network" : "eth0"})

	for opt, arg in opts:
	    if opt in ('-m', '--machine'):
	        information["machine"] = arg
	    elif opt in ('-i', '--ip'):
	        information["ip"] = arg
	    elif opt in ('-n', '--network'):
	        information["network"] = arg
	    else:
	        usage()
	        sys.exit(1)

	if len(information) != 3:
		usage()
		sys.exit(1)
	return information 

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

def send_info(network, machine_name, ip_address):
	local_ip = get_ip_address(network)
	print(local_ip)

	from uuid import getnode as get_mac
	mac = get_mac()

	name = machine_name
	try:
		r = requests.post("http://" + ip_address + ":3000/fogo_machines/new", data=json.dumps({"name" : name, "ip" : str(local_ip), "mac" : str(mac)}), headers={"content-type": "application/json"}, timeout=3.0)
	except:
		print("Communication to server failed. Is it running?")
		sys.exit(1)
	print r.status_code
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
	send_info(information["network"], information["machine"], information["ip"])

	app = Flask(__name__)
	api = Api(app)

	api.add_resource(Buffer, '/increase_buffer')
	api.add_resource(Decoder, '/run_decoder/<state>')
	api.add_resource(Ptp, '/run_ptp/<state>')

	app.run(host="0.0.0.0", debug=False, use_reloader=False)
else:
	print("This script is not a module!\n\n")
	print("Please visit https://github.com/caiomcg/Fogo-Controller")