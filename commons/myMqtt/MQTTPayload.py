#!/usr/bin/env python

def getMQTTPayload(topic, buildingID, address,measurements):
	return ('{"topic":"%s", "building":"%s", "address":"%s", "measurements":[%s]}' % (str(topic), str(buildingID), str(address), str(measurements)))

def getSingleEvent(value, event, realTimestamp, fakeTimestamp):

	return ('{"value":"%s", "event":"%s", "realTimestamp":"%s", "fakeTimestamp":"%s"}' % (str(value), str(event), str(realTimestamp), str(fakeTimestamp)))