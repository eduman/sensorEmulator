#!/usr/bin/env python

#About measurements

def getMeasurementEvent(buildigID):
	if buildigID:
		event = ("MEASUREMENT/BUILDING/%s" % (buildigID))
	else:
		event = "MEASUREMENT/BUILDING"
	return event

def getExternalTemperatureEvent(buildigID):
	return ("%s/" + "ExternalTemperature" % (getMeasurementEvent(buildigID)))

def getPowerEvent(buildigID):
	return ("%s/" + "Power" % (getMeasurementEvent(buildigID)))

