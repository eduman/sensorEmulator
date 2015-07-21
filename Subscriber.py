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



logLevel = logging.DEBUG
#logLevel = logging.INFO



class Subscriber(object):
	def __init__(self, subscriberName):

		self.brokerUri = "seemp.polito.it"
		self.brokerPort = 1883

		self.subscriberName = subscriberName
		self.configPath = "conf/%s.conf" % (self.subscriberName)
		logPath = "log/%s.log" % (self.subscriberName)


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

		self.logger = logging.getLogger(self.subscriberName)
		self.logger.setLevel(logLevel)
		hdlr = logging.FileHandler(logPath)
		formatter = logging.Formatter(self.subscriberName + ": " + "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr)
		
		consoleHandler = logging.StreamHandler()
		consoleHandler.setFormatter(formatter)
		self.logger.addHandler(consoleHandler)

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
		config.set(section, key, "seemp.polito.it:1883")
		
		#key = ConfigurationConstants.getFullBuildingList()
		#config.set(section, key,"BOVE_5;CABOTO_27;CABOTO_3;CARLE_FRATELLI_25;CASSINI_14;CASSINI_41;CASSINI_57;CASSINI_73;CASSINI_74;COLOMBO_17;COLOMBO_45;COLOMBO_59;DE_GASPERI_24;DE_GASPERI_31;DE_GASPERI_51;DUCA_DAOSTA_7;DUCA_DEGLI_ABRUZZI_30;DUCA_DEGLI_ABRUZZI_56;DUCA_DEGLI_ABRUZZI_57;DUCA_DEGLI_ABRUZZI_83;EINAUDI_2;FERRARIS_138;FERRARIS_63;FERRARIS_65;FERRARIS_71;FERRARIS_99;GIOBERTI_88;GIOBERTI_94;GOVERNOLO_28;LAMARMORA_43;LAMARMORA_66;LAMARMORA_7;LAMARMORA_77;MAGENTA_35;MAGENTA_50;MARCO_POLO_41;MASSENA_94;MONTEVECCHIO_22;MONTEVECCHIO_49;MOROSINI_21;PASTRENGO_25;PASTRENGO_29;PIAZZI_7;PIGAFETTA_35;PIGAFETTA_38;RE_UMBERTO_25;RE_UMBERTO_40;RE_UMBERTO_60;RE_UMBERTO_75;RE_UMBERTO_76;RE_UMBERTO_85;S.SECONDO_98;SAN_SECONDO_80;SOMMEILLER_29;TURATI_25;TURATI_62;TURATI_7;VESPUCCI_55;VESPUCCI_61;VITTORIO_EMANUELE_111;VITTORIO_EMANUELE_II_105;")


		section = ConfigurationConstants.getRuleSettings()
		config.add_section(section)

		config.write(f)


	def setConfigValues(self):
		config = ConfigParser.SafeConfigParser()
		config.read(self.configPath)

		section = ConfigurationConstants.getGeneralSettings()

		self.brokerUri, self.brokerPort = ''.join(config.get(section, ConfigurationConstants.getMessageBroker()).split()).split(':')
		#self.buildingList = config.get(section, ConfigurationConstants.getMessageBroker())

	def loop(self):
		while (True):
			time.sleep(1.0)

	def start (self):

		self.mqttc = MyMQTTClass(self.subscriberName, self.logger, self)
		self.mqttc.connect(self.brokerUri,self.brokerPort)
		self.subscribedEventList = self.mqttc.subscribeEvent(None, EventTopics.getMeasurementEvent())

	
		self.loop()


	def stop (self):
		self.logger.info("Stopping %s" % (self.subscriberName))
		if hasattr (self, "mqttc"):
			try:
				for event in self.subscribedEventList:
					self.mqttc.unsubscribeEvent(event)	
				self.mqttc.disconnect()
			except Exception, e:
				self.logger.error("Error on stop(): %s" % (e))

		sys.exit(0)


	def notifyJsonEvent(self, topic, jsonEventString):
		self.logger.debug ("received topic: \"%s\" with msg: \"%s\"" % (topic, jsonEventString))	

		try:
			data = json.loads(jsonEventString)

		except Exception, e:
			self.logger.error("Error on Subscriber.notifyJsonEvent() %s: " % e)

		# TODO 
		# @Antonio: manage here the incoming event	



if __name__ == "__main__":
	s = Subscriber ("teleSubscriber")
	s.start()