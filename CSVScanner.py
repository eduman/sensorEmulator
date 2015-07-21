#!/usr/bin/env python

import sys

from commons.myMqtt import EventTopics
from commons.myMqtt import MQTTPayload
from commons.myMqtt.MQTTClient import MyMQTTClass
import logging
import os
import sys
import time
import datetime
from commons import ConfigurationConstants
from pandas import *
from math import isnan
import threading
from Configurator import Configurator


class CSVScanner(threading.Thread):
	def __init__(self, buildingID, logger, csvPath, configurator, mqtt):
		super(CSVScanner, self).__init__()
		self.buildingID = buildingID.lower()
		self.logger = logger
		self.isLoop = True
		self.configurator = configurator
		self.csvPath = csvPath
		self.samplingTime = ConfigurationConstants.getDefaultSampligTimeValue()
		self.mqtt = mqtt


	def run(self):
		
		
		section = ConfigurationConstants.getGeneralSettings()
		try:
			self.samplingTime = int(self.configurator.get(section, ConfigurationConstants.getSamplingTime()))
		except Exception, e:
			self.samplingTime = ConfigurationConstants.getDefaultSampligTimeValue()
			self.logger.error("Error on buildingID = %s: setting default samplingTime = %d" % (self.buildingID, ConfigurationConstants.getDefaultSampligTimeValue()))		


		section = ConfigurationConstants.getRuleSettings()

		try:
			self.index = int(self.configurator.get(section, self.buildingID))
			self.logger.debug("buildingID = %s: setting index = %d" % (self.buildingID, self.index))
		except Exception, e:
			self.logger.warning("Warning on buildingID = %s: setting default index = 0. %s" % (self.buildingID, e))
			self.index = 0

		fileName = (self.csvPath + "/%s.csv" % (self.buildingID))
		try:
			dataset = read_csv(fileName, sep=",")


			while self.isLoop:
				# TODO: header csv in CSVHeader.py 
				while (isnan(dataset['P'][self.index]) or isnan(dataset['T_ex'][self.index])):
					self.index += 1

				topic = EventTopics.getMeasurementEvent(self.buildingID)
				fakeDate = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
				events = MQTTPayload.getSingleEvent(dataset['P'][self.index], "Power", dataset['Date'][self.index], fakeDate)
				events += "," + MQTTPayload.getSingleEvent(dataset['T_ex'][self.index], "External Temperature", dataset['Date'][self.index], fakeDate)
				payload = MQTTPayload.getMQTTPayload(topic, self.buildingID, self.buildingID, events)

				self.mqtt.syncPublish(topic, payload)
				self.logger.debug ("sending: %s", payload)

				if self.index < len (dataset):
					self.index += 1
				else:
					self.index = 0

				self.configurator.set(section, self.buildingID, self.index )
				time.sleep(self.samplingTime)

		except IOError, e:
			self.logger.error("IOError on buildingID = %s: %s" % (self.buildingID, e))
			self.stop()

		except Exception, e:
			self.logger.error("Error on buildingID = %s: %s" % (self.buildingID, e))
			self.stop()

	def stop(self):
		self.isLoop = False
	
		if self.isAlive():
			try:
				self.logger.debug ("Stopping building %s.", self.buildingID)
				self._Thread__stop()
			except Exception, e:
				self.logger.error("Error on buildingID = %s. The thread could not be terminated: %s" % (self.buildingID, e))

