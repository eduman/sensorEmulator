#!/usr/bin/env python

import threading
import os


class Configurator ():

	def __init__(self, logger):
		self.__lock = threading.Lock()
		self.logger = logger
		self.__config = {}
		
		


	def add_section(self, section):
		self.__lock.acquire()
		if section not in self.__config.keys():
			self.__config[section] = {}
		self.__lock.release()

	def set(self, section, key, value):
		self.__lock.acquire()

		if section in self.__config.keys():
			settings = self.__config[section]
		else:
			settings = {}

		settings[key] = value
		self.__config[section] = settings
		self.__lock.release()


	def get (self, section, key):
#		self.__lock.acquire()

		if section not in self.__config.keys():
			raise Exception ("Section '%s' does not exist" % (section))

		if key not in self.__config[section].keys():
			raise Exception ("Option '%s' does not exist in section '%s'" % (key, section))

		value = self.__config[section][key]
#		self.__lock.release()
		
		return value

	def getSections(self):
#		self.__lock.acquire()
		result = self.__config.keys()
#		self.__lock.release()
		return result

	def getOptions (self, section):
#		self.__lock.acquire()

		if section not in self.__config.keys():
			raise Exception ("Section '%s' is does not exist" % (section))

		result = self.__config[section].keys()
#		self.__lock.release()
		return result 



