#!/usr/bin/env python


#About configuration sections

def getRuleSettings():
	return "rule_settings"

def getGeneralSettings():
	return "general_settings"

def getRuleSettingsKeywords():
	return []

def getGeneralSettingsKeywords():
	return [getFullBuildingList(), getMessageBroker(), getSamplingTime()]



# General settings to be saved
def getFullBuildingList():
	return "buildinglist"

def getMessageBroker():
	return "messagebroker"

def getSamplingTime():
	return "samplingtime"

def getDefaultSampligTimeValue():
	return 60

def getDefaultMessageBrokerValue():
	return "seemp.polito.it:1883"

