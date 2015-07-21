#!/usr/bin/env python

#About measurements
def getMeasurementEvent(buildigID):
	return ("MEASUREMENT/BUILDING/%s" % (buildigID))

def getExternalTemperatureEvent(buildigID):
	return ("%s/" + "ExternalTemperature" % (getMeasurementEvent(buildigID)))

def getPowerEvent(buildigID):
	return ("%s/" + "Power" % (getMeasurementEvent(buildigID)))

