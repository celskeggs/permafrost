import os
import json
import requests

STAGING_PATH = "/home/user/staging"
WEBHOOK_NAME = ".permafrostwebhook"

def load_secret(name, use_json=False):
	home = os.getenv("HOME")
	if not home:
		raise Exception("no $HOME")
	target = os.path.join(home, name)
	if os.stat(target).st_mode & 0o777 != 0o600:
		raise Exception("wrong permissions on file: %s" % target)
	with open(target, "r") as f:
		if use_json:
			return json.load(f)
		else:
			return f.read().strip()

class Notifier:
	def __init__(self):
		self.webhook = load_secret(WEBHOOK_NAME)

	def send(self, message):
		print(message)
		r = requests.post(self.webhook, data=json.dumps({"text": message}))
		if r.status_code != 200:
			raise Exception("could not send to slack: %s" % repr(r.text))

# via https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

