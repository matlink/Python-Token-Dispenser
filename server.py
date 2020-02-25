import tornado.ioloop
import tornado.web
import random
import sys

from gpapi.googleplay import GooglePlayAPI

class MainHandler(tornado.web.RequestHandler):
	def initialize(self, credentials_list):
		self.credentials_list = credentials_list

	def get(self, device=None):
		if device is None:
			api = GooglePlayAPI()
		else:
			try:
				api = GooglePlayAPI(device_codename=device)
			except Exception as e:
				self.write("Error: no such device %s" % device)
				return
		email, password = random.choice(self.credentials_list).split()
		api.login(email, password)
		self.write("%s %s" % (api.authSubToken, hex(api.gsfId)[2:]))

def make_app(credential_file):
	with open(credential_file) as inbuff:
		credentials_list = list(inbuff)
	return tornado.web.Application([
		(r"/email/gsfid/(.*)", MainHandler, dict(credentials_list = credentials_list)),
		(r"/.*", MainHandler, dict(credentials_list = credentials_list)),
	])

if __name__ == "__main__":
	app = make_app(sys.argv[1])
	app.listen(8080)
	tornado.ioloop.IOLoop.current().start()