#!/usr/bin/env python

from flask import Flask
import json
import requests

app = Flask(__name__)

hue_ip = "" 
hue_user = ""

strips = ["00:17:88:01:02:17:7c:95-0b","00:17:88:01:02:17:6d:28-0b"]
bulbs = ["00:17:88:01:02:8f:59:85-0b","00:17:88:01:02:55:e2:84-0b","00:17:88:01:02:4d:fa:e5-0b","00:17:88:01:02:25:9f:d8-0b"]

class Light(object):
	def __init__(self,id):
		self._id = id
		self._url = "http://{}/api/{}/lights/{}".format(hue_ip,hue_user,id)
		self._stateUrl = "{}/state".format(self._url)
		self.init(self)

	@staticmethod
	def init(self):
		res = requests.get(self._url)
		if res.status_code == 200:
			data = json.loads(res.text)
		else:
			data = {}
		self._state = data['state']
		self._type = data['type']
		self._uid = data['uniqueid']

	def turnOn(self):
		data = {"on": True}
		res = requests.put(self._stateUrl, data=json.dumps(data))
		if res.status_code == 200:
			return True
		else:
			return False

	def turnOff(self):
		data = {"on": False}
		res = requests.put(self._stateUrl, data=json.dumps(data))
		if res.status_code == 200:
			return True
		else:
			return False

	def state(self):
		# Update the state information
		res = requests.get(self._url)
		if res.status_code == 200:
			self._state = json.loads(res.text)["state"]

		return self._state

	def isOn(self):
		return self.state()["on"]

	def toggle(self):
		# This will check the current state of the light and toggle it to the opposite
		if self.isOn():
			self.turnOff()
		else:
			self.turnOn()


def getLights():
	# This will get a list of all of the lights available and return it
	res = requests.get("http://{}/api/{}/lights".format(hue_ip,hue_user))
	lights = {}
	if res.status_code == 200:
		ls = json.loads(res.text)
		for l in ls.keys():
			light = Light(l)
			lights[light._uid] = light

	return lights



@app.route("/toggle/<string:type>", methods=["GET"])
def toggle(type):
	# This will turn lights on or off
	lights = getLights()

	if type == "bulbs":
		for b in bulbs:
			lights[b].toggle()
	elif type == "strips":
		for s in strips:
			lights[s].toggle()
	else:
		for l in lights.values():
			l.toggle()

	return "Success!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5151)
