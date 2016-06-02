#!/usr/bin/env python

import json
import requests
import socket
import os
import sys
from flask import Flask
from flask_restful import Resource, Api
import subprocess
import signal
import fcntl
import struct

def usage():
	print "Usage:"
	print "Fogo-Controller [MACHINE NAME] [IP]"
	return

if len(sys.argv) == 2 or len(sys.argv) == 1:
	print "The name of the machine is needed to proceed!"
	usage()
	sys.exit()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

def send_info():
	local_ip = get_ip_address("wlan0")
	print(local_ip)

	from uuid import getnode as get_mac
	mac = get_mac()

	name = sys.argv[1]
	try:
		r = requests.post("http://" + sys.argv[2] + ":3000/fogo_machines/new", data=json.dumps({"name" : name, "ip" : str(local_ip), "mac" : str(mac)}), headers={"content-type": "application/json"})
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
	send_info()
	app = Flask(__name__)
	api = Api(app)

	api.add_resource(Buffer, '/increase_buffer')
	api.add_resource(Decoder, '/run_decoder/<state>')
	api.add_resource(Ptp, '/run_ptp/<state>')

	app.run(host="0.0.0.0", debug=False, use_reloader=False)
else:
	print("This script is not a module!\n\n")
	print("Please visit https://github.com/caiomcg/Fogo-Controller")