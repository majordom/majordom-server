# from urllib2 import urlopen, Request
from json import dumps, loads

# 
# headers = {}
# headers['Content-Type'] = 'application/json'
# jdata = dumps(
# 			{'command': 'get_list_ids',
# 			'list': 'devices'})
# answer = urlopen("http://127.0.0.1:8080", jdata, headers)
# 
# print answer

import urllib2
req = urllib2.Request(url='http://127.0.0.1:8080/')
data = dumps(
 			{'command': 'get_list_ids',
 			'list': 'devices'})
req.add_data(data)
req.add_header('Content-Type', 'application/json')
f = urllib2.urlopen(req)
print loads(f.read())[0]