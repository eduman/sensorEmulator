#!/usr/bin/env python

import sys

from commons.myMqtt import EventTopics
from commons.myMqtt.MQTTClient import MyMQTTClass
import logging
import os
import signal
import sys
import json
import time
from commons import ConfigurationConstants
import ConfigParser
from CSVScanner import CSVScanner 
import threading
from Configurator import Configurator



logLevel = logging.DEBUG 
#logLevel = logging.INFO

class Publisher(object):
	def __init__(self, publisherName):

		self.brokerUri = "seemp.polito.it"
		self.brokerPort = 1883
		
		self.buildingThreadList = []

		self.publisherName = publisherName
		self.configPath = "conf/%s.conf" % (self.publisherName)
		self.csvFolder = "csv/"
		logPath = "log/%s.log" % (self.publisherName)




		if not os.path.exists(logPath):
			try:
				os.makedirs(os.path.dirname(logPath))
			except Exception, e:
				pass

		if not os.path.exists(self.configPath):
			try:
				self.makeDefaultConfigFile()
			except Exception, e:
				pass

		self.logger = logging.getLogger(self.publisherName)
		self.logger.setLevel(logLevel)
		hdlr = logging.FileHandler(logPath)
		formatter = logging.Formatter(self.publisherName + ": " + "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr)
		
		consoleHandler = logging.StreamHandler()
		consoleHandler.setFormatter(formatter)
		self.logger.addHandler(consoleHandler)

		self.configurator = Configurator(self.logger)
		self.subscribedEventList = []


		for sig in (signal.SIGABRT, signal.SIGILL, signal.SIGINT, signal.SIGSEGV, signal.SIGTERM):
			signal.signal(sig, self.signal_handler)


	def signal_handler(self, signal, frame):
		self.stop()

	def makeDefaultConfigFile(self):
		try:
			os.makedirs(os.path.dirname(self.configPath))
		except Exception, e:
			pass

		f = open(self.configPath, "w+")
		section = ConfigurationConstants.getGeneralSettings()

		config = ConfigParser.SafeConfigParser()
		config.add_section(section)
		
		key = ConfigurationConstants.getMessageBroker()
		config.set(section, key, ConfigurationConstants.getDefaultMessageBrokerValue())
		
		key = ConfigurationConstants.getSamplingTime()
		config.set(section, key, str(ConfigurationConstants.getDefaultSampligTimeValue()))

		section = ConfigurationConstants.getRuleSettings()
		config.add_section(section)

		config.write(f)


	def setConfigValues(self):
		config = ConfigParser.SafeConfigParser()
		config.read(self.configPath)

		try:
			section = ConfigurationConstants.getGeneralSettings()

			#self.configurator.add_section(section)
			#value = config.get(section, ConfigurationConstants.getMessageBroker())
			#self.configurator.set(section, ConfigurationConstants.getMessageBroker(), value)

			try:
				brokerFull = config.get(section, ConfigurationConstants.getMessageBroker())
				self.configurator.set(section, ConfigurationConstants.getMessageBroker(), brokerFull)
				self.brokerUri, self.brokerPort = ''.join(brokerFull.split()).split(':')
			except Exception, e:
				self.brokerUri, self.brokerPort = ''.join(ConfigurationConstants.getDefaultMessageBrokerValue().split()).split(':')
				self.logger.error("Error on Publisher.setConfigValues(): setting default message broker = %s" % (ConfigurationConstants.getDefaultMessageBrokerValue()))


			self.mqtt = MyMQTTClass(self.publisherName, self.logger, None)
			self.mqtt.connect(self.brokerUri, self.brokerPort)
		
			try:
				samplingTime = int (config.get(section, ConfigurationConstants.getSamplingTime()))
			except ValueError, e:
				self.logger.error("Error on Publisher.setConfigValues(). \"samplingtime is not an integer:\" %s" % (e))
				samplingTime = ConfigurationConstants.getDefaultSampligTimeValue()

			self.configurator.set(section, ConfigurationConstants.getSamplingTime(), samplingTime)

			section = ConfigurationConstants.getRuleSettings()
			self.configurator.add_section(section)
			for key, value in config.items(ConfigurationConstants.getRuleSettings()):
				self.configurator.set(section, key, value)

		except Exception, e:
			self.logger.error("Error on Publisher.setConfigValues(): %s" % (e))



	def loop(self):
		while (True):
			time.sleep(1.0)

	def start (self):
		try:
			self.setConfigValues()
			if os.path.exists(self.csvFolder):
				for file in os.listdir(self.csvFolder):
					if file.endswith(".csv"):
						pass
						buiding = CSVScanner(os.path.splitext(file)[0], self.logger, self.csvFolder, self.configurator, self.mqtt)
						self.buildingThreadList.append(buiding)
						buiding.start()

				self.loop()
			else:
				self.logger.error("Error: CSV folder does not exist. Exiting...")
				self.stop()

		except Exception, e:
			self.logger.error("Error on Publisher.start(): %s. Exiting..." % (e))
			self.stop()

	

	def stop (self):
		self.logger.info("Stopping %s" % (self.publisherName))

		for building in self.buildingThreadList:
			building.stop()

		self.writeConfigurator()

		if hasattr (self, "mqtt"):
			try:
				self.mqtt.disconnect()
			except Exception, e:
				self.logger.error("Error on stop() for buildingID = %s: %s" % (self.buildingID, e))

		sys.exit(0)

	def writeConfigurator(self):

		try:
			os.makedirs(os.path.dirname(self.configPath))
		except Exception, e:
			pass

		

		try:
			config = ConfigParser.SafeConfigParser()
			for section in self.configurator.getSections():
				config.add_section(section)
				for key in self.configurator.getOptions(section):
					value = self.configurator.get(section, key)
					config.set(section, key, str(value))


			f = open(self.configPath, "w+")
			config.write(f)
		except Exception, e:
			self.logger.error("Error on Publisher.writeConfigurator(): %s" % (e))




if __name__ == "__main__":
	s = Publisher ("sensorEmulatorDH")
	s.start()