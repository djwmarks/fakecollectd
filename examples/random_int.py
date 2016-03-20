#!/usr/bin/env python

import collectd
import random

_min, _max = None, None

def config_cb(conf):
	global _min, _max
	for entry in conf.children:
		if entry.key == "Minimum":
			_min = entry.values[0]
		if entry.key == "Maximum":
			_max = entry.values[0]

def read_cb():
	v = collectd.Values()
	v.plugin = "random_int"
	v.type = "absolute"
	v.type_instance = "value"
	v.values = [random.randrange(_min, _max)]
	v.dispatch()

collectd.register_config(config_cb)
collectd.register_read(read_cb)
