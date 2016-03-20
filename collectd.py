#!/usr/bin/env python

from collections import defaultdict
from Queue import Queue
import functools
import json
import sys
import time

class Config(object):
	__slots__ = ("children", "key", "values")

	def __init__(self, json_conf=None):
		if json_conf is None:
			self.children = []
			self.key = None
			self.values = []
		else:
			self.children = [Config(child) for child in json_conf["children"]]
			self.key = json_conf["key"]
			self.values = json_conf["values"]

	def __repr__(self):
		return "<collectd.Config(key=%s, values=%s)>" % (self.key, ",".join(map(str, self.values)))

_log_queue = Queue()

def debug(message):
	_log_queue.put(("debug", message))

def error(message):
	_log_queue.put(("error", message))

def info(message):
	_log_queue.put(("info", message))

def warn(message):
	_log_queue.put(("warn", message))

_value_queue = Queue()

class Values(object):
	__slots__ = ("dispatch", "plugin", "plugin_instance", "type", "type_instance", "values")

	def __init__(self):
		self.plugin = None
		self.plugin_instance = None
		self.type = None
		self.type_instance = None
		self.values = []

	def __repr__(self):
		return "<collectd.Values %s/%s=%s>" % (self.plugin_name, self.type_name, ",".join(map(str, self.values)))

	def dispatch(self):
		_value_queue.put(self)

	@property
	def plugin_name(self):
		if self.plugin_instance is None:
			return self.plugin
		else:
			return "%s-%s" % (self.plugin, self.plugin_instance)

	@property
	def type_name(self):
		if self.type_instance is None:
			return self.type
		else:
			return "%s-%s" % (self.type, self.type_instance)

__callbacks = defaultdict(list)

def __register_callback(name, fn):
	if not hasattr(fn, "__call__"):
		raise ValueError("Callback not a callable value.")
	__callbacks[name].append(fn)

def run_callbacks(name, *args, **kwargs):
	for cb_fn in __callbacks[name]:
		cb_fn(*args, **kwargs)

__module_ref = sys.modules[__name__]
for cb_name in ["config", "info", "read", "shutdown", "write", "flush", "log", "notification"]:
	setattr(__module_ref, "register_%s" % cb_name, functools.partial(__register_callback, cb_name))

Interval = 10

def __default_log(log):
	print log

def __default_write(value):
	print value

def main_app(config_json):
	config = Config(config_json)
	run_callbacks("config", config)

	if not __callbacks["log"]:
		register_log(__default_log)
	if not __callbacks["write"]:
		register_write(__default_write)

	while True:
		run_callbacks("read")
		while not _log_queue.empty():
			run_callbacks("log", _log_queue.get())
		while not _value_queue.empty():
			run_callbacks("write", _value_queue.get())
		time.sleep(Interval)

	for shutdown_cb in __callbacks["shutdown"]:
		shutdown_cb()
