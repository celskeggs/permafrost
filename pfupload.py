#!/usr/bin/env python3
import os

import requests

import util

def upload_all(local_path):
	if not os.path.isdir(local_path):
		raise Exception("nonexistent staging directory")
	bucket = util.connect_bucket()
	uploaded = {obj.key: obj.size for obj in bucket.objects.all()}
	total_count, total_size = 0, 0
	for path, folders, files in os.walk(local_path):
		for f in files:
			lpath = os.path.join(path, f)
			rpath = os.path.relpath(lpath, local_path)
			local_size = os.stat(lpath).st_size
			if rpath in uploaded:
				if local_size != uploaded[rpath]:
					raise Exception("expected previously uploaded file %s to be of size %d, not %d" % (rpath, local_size, uploaded[rpath]))
				continue
			print("uploading", lpath, "to", rpath)
			bucket.upload_file(lpath, rpath)
			total_count += 1
			total_size += local_size
	bucket_size = total_size + sum(uploaded.values())
	return total_count, total_size, bucket_size

def main():
	notify = util.Notifier()
	total_count, total_size, bucket_size = upload_all(util.STAGING_PATH)
	if total_count:
		notify.send("uploaded %d files of total size %s; new bucket size is %s" % (total_count, util.sizeof_fmt(total_size), util.sizeof_fmt(bucket_size)))
	else:
		print("nothing to do")

if __name__ == "__main__":
	main()

