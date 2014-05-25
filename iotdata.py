#!/usr/bin/env python
 
import os
#import xively
import subprocess
from urllib2 import urlopen, Request
from time import time, mktime, sleep
import time
from datetime import datetime
from json import dumps
#import requests
 
# extract feed_id and api_key from environment variables
FEED_ID = os.environ["FEED_ID"]
API_KEY = os.environ["API_KEY"]
DEBUG = os.environ["DEBUG"] or false
 
# initialize api client
#api = xively.XivelyAPIClient(API_KEY)

class Client (object):
    api_url = "http://api.carriots.com/streams"

    def __init__(self, api_key=None, client_type='json'):
        self.client_type = client_type
        self.api_key = api_key
        self.content_type = "application/vnd.carriots.api.v2+%s" % self.client_type
        self.headers = {'User-Agent': 'Raspberry-Carriots',
                        'Content-Type': self.content_type,
                        'Accept': self.content_type,
                        'Carriots.apikey': self.api_key}
        self.data = None
        self.response = None

    def send(self, data):
        self.data = dumps(data)
        request = Request(Client.api_url, self.data, self.headers)
        self.response = urlopen(request)
        return self.response
 
# function to read 1 minute load average from system uptime command
def read_loadavg():
  if DEBUG:
    print "Reading load average"
  return subprocess.check_output(["awk '{print $1}' /proc/loadavg"], shell=True)
 
# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
  try:
    datastream = feed.datastreams.get("load_avg")
    if DEBUG:
      print "Found existing datastream"
    return datastream
  except:
    if DEBUG:
      print "Creating new datastream"
    datastream = feed.datastreams.create("load_avg", tags="load_01")
    return datastream
 
# main program entry point - runs continuously updating our datastream with the
# current 1 minute load average
def run():
  print "Starting iotdata script"
 
#  feed = api.feeds.get(FEED_ID)
 
#  datastream = get_datastream(feed)
#  datastream.max_value = None
#  datastream.min_value = None
  client_carriots = Client(API_KEY)

  while True:
    timestamp = int(mktime(datetime.utcnow().timetuple()))
    load_avg = read_loadavg()
 
    if DEBUG:
      print "Updating feed with value: %s" % load_avg
      print "Time : %s" % timestamp

    data = {"protocol": "v2", "device": FEED_ID, "at": timestamp, "data": load_avg}
    carriots_response = client_carriots.send(data)
    print carriots_response.read() 
#    datastream.current_value = load_avg
#    datastream.at = datetime.datetime.utcnow()
#    try:
#      datastream.update()
#    except requests.HTTPError as e:
#      print "HTTPError({0}): {1}".format(e.errno, e.strerror)
 
    time.sleep(10)
 
run()

