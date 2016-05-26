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

def usage():
	print "Usage:"
	print "Fogo-Controller [MACHINE NAME] [IP]"
	return

if len(sys.argv) == 2 or len(sys.argv) == 1:
	print "The name of the machine is needed to proceed!"
	usage()
	sys.exit()

def send_info():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8",80))
	local_ip = s.getsockname()[0]
	s.close()

	from uuid import getnode as get_mac
	mac = get_mac()

	name = sys.argv[1]
	r = requests.post("http://" + sys.argv[2] + ":3000/fogo_machines/new", data=json.dumps({"name" : name, "ip" : str(local_ip), "mac" : str(mac)}), headers={"content-type": "application/json"})
	print r.status_code
	return

def killProcess():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        if "fogo_decoder_video" in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)       

app = Flask(__name__)
api = Api(app)

class Decoder(Resource):
    running = False	    
    def get(self):
        if not running:
    	    subprocess.call("~/FOGO-2015/Debug/run_decoder.sh")
        else:
            
         
        return {'response': 'decoder_ok'}
class Buffer(Resource):
    def get(self):
    	os.system("sudo sysctl -w net.core.rmem_max=5000000000000000000")
        return {'response': 'buffer_ok'}
class Sender(Resource):
    def get(self):
        return {'response': 'sender_ok'}

api.add_resource(Buffer, '/increase_buffer')
api.add_resource(Decoder, '/run_decoder')
api.add_resource(Sender, '/sender')

send_info()
if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=False, use_reloader=False)

