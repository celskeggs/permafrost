#!/usr/bin/env python3
import os
import json
import requests

WEBHOOK_PATH="/home/user/.permafrostwebhook"

def check_incoming(source, dest):
	print("checking incoming files...")
	errors = []
	counts = {}
	for svm in os.listdir(source):
		svmpath = os.path.join(source, svm)
		dvmpath = os.path.join(dest, svm)
		count, octets = 0, 0
		for f in os.listdir(svmpath):
			fpath = os.path.join(svmpath, f)
			dpath = os.path.join(dvmpath, f)
			if os.path.isdir(fpath):
				errors.append("skipping directory %s" % repr(fpath))
				continue
			if os.path.exists(dpath):
				errors.append("skipping duplicate file %s" % repr(fpath))
				continue
			size = os.stat(fpath).st_size
			if size == 0:
				errors.append("skipping zero-sized file %s" % repr(fpath))
				continue
			if not os.path.isdir(os.path.dirname(dpath)):
				os.makedirs(os.path.dirname(dpath))
			os.rename(fpath, dpath)
			count += 1
			octets += size
		if not count:
			continue
		counts[svm] = (count, octets)
	return errors, counts

def get_webhook():
        with open(WEBHOOK_PATH, "r") as f:
                return f.read().strip()

def notify(message, webhook):
	print(message)
	r = requests.post(webhook, data=json.dumps({"text": message}))
	print("slack", r.text, r.status_code)

# via https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def main():
	webhook = get_webhook()
	errors, counts = check_incoming("/home/user/QubesIncoming", "/home/user/staging")
	lines = []
	if errors:
		lines += ["encountered %d errors:" % len(errors)]
		for err in errors:
			lines += [" * %s" % err]
	if counts:
		tcount = sum(count for count, size in counts.values())
		tsize = sum(size for count, size in counts.values())
		lines += ["accepted %d files from %d VMs (%s)" % (tcount, len(counts), sizeof_fmt(tsize))]
		for vm, (count, size) in sorted(counts.items()):
			lines += [" * %s: %d (%s)" % (repr(vm), count, sizeof_fmt(tsize))]
	if lines:
		notify("\n".join(lines), webhook)

if __name__ == "__main__":
	main()
