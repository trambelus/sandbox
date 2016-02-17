#!/usr/bin/env python3

import argparse
import re
import requests
import time

LOGFILE = 'iploc.log'

def log(*msg):
	"""
	Prepends a timestamp and prints a message to the console and LOGFILE
	"""
	output = "%s:\t%s" % (time.strftime("%Y-%m-%d %X"), ' '.join([str(s) for s in msg]))
	print(output)
	with open(LOGFILE, 'a') as f:
		f.write(output + '\n')

def parse():
	parser = argparse.ArgumentParser(description="Geolocates all IP addresses in a file")
	parser.add_argument('infile', help='file to scan')
	parser.add_argument('-outfile', required=False, default='geoloc.txt', help='output file')
	return parser.parse_args()

def geoloc(ip):
	resp_raw = requests.get('http://freegeoip.net/json/{}'.format(ip))
	resp_j = resp_raw.json()
	if resp_j['city']:
		print("{}: {}, {}".format(ip, resp_j['city'], resp_j['country_name']))
	else:
		print("{}: {}".format(ip, resp_j['country_name']))
	return "{} ({}, {})".format(ip, resp_j['city'], resp_j['country_name'])

def scan(lines, outfile):
	ip_pat = re.compile('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
	for line in lines:
		res = re.search(ip_pat, line)

		if res == None:
			repl_line = line
		else:
			ip = res.group(0)
			repl_ip = geoloc(ip)
			repl_line = re.sub(ip_pat, line, repl_ip)

		# with open(outfile, 'a') as f:
		# 	f.write(repl_line)

def main():
	args = parse()
	with open(args.infile, 'r') as f:
		lines = f.readlines()
	ips = scan(lines, args.outfile)

if __name__ == '__main__':
	main()