import json
import os
import subprocess

import boto3
import requests

STAGING_PATH = "/home/user/staging"
UNSTAGING_PATH = "/home/user/unstaging"
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

def connect_bucket():
	j = load_secret(".permafrostremote", use_json=True)
	if type(j) != dict:
		raise Exception("invalid format of remote config")
	if {k: type(v) for k, v in j.items()} != {"key": str, "secret": str, "url": str, "bucket": str}:
		raise Exception("invalid format of remote config")
	session = boto3.session.Session(region_name='nyc3', aws_access_key_id=j["key"], aws_secret_access_key=j["secret"])
	s3 = session.resource("s3", endpoint_url=j["url"])
	return s3.Bucket(j["bucket"])

def qvm_copy(path, target_vm):
	print("copying file", path, "to vm", target_vm)
	nenv = dict(os.environ)
	nenv["PROGRESS_TYPE"] = "none"
	subprocess.check_call(["/usr/lib/qubes/qrexec-client-vm", target_vm, "qubes.Filecopy", "/usr/lib/qubes/qfile-agent", path], env=nenv)

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

