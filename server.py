import tornado.ioloop
import tornado.web
import random
import time
import sys

from gpapi.googleplay import GooglePlayAPI
from gpapi import config

class MainHandler(tornado.web.RequestHandler):
	def initialize(self, credentials_list, apis):
		self.credentials_list = credentials_list
		self.apis = apis

	def get(self, device=None):
		if device and device not in config.getDevicesCodenames():
			self.write("Error: no such device %s" % device)
			return
		if device is None:
			device = 'bacon'
		email, pwd = random.choice(self.credentials_list)
		need_login = False
		if device in self.apis[email]:
			# check token not expired and return
			api = self.apis[email][device]
			try:
				api.search('drv')
			except Exception:
				need_login = True
		elif device not in self.apis[email] or need_login:
			# need fresh login
			api = GooglePlayAPI(device_codename = device)
			api.login(email, pwd)
			self.apis[email][device] = api
			# wait for login to propagate
			time.sleep(5)
		self.write("%s %s" % (api.authSubToken, hex(api.gsfId)[2:]))

def make_app(credential_file):
	with open(credential_file) as inbuff:
		credentials_list = [tuple(line.split()) for line in inbuff if not line.startswith('#')]
	print("Loaded credentials: ", [line[0] for line in credentials_list])
	apis = dict()
	for cred in credentials_list:
		email, pwd = cred
		apis[email] = dict()
	params = dict(credentials_list=credentials_list, apis=apis)
	return tornado.web.Application([
		(r"/email/gsfid/(.*)", MainHandler, params),
		(r"/.*", MainHandler, params),
	])

if __name__ == "__main__":
	app = make_app(sys.argv[1])
	app.listen(8080)
	tornado.ioloop.IOLoop.current().start()