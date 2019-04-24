'''****************************************************************
CompareFields.py
Author(s): Anders Olson
Usage: Run script using python IDE or similar
Description: 
        Script compares field names of two datasets and selects field
        names that are not a match/not found in both datasets.
        =^._.^=    
****************************************************************'''

import arcpy
import collections

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Configure logger 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define environment and messaging
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Set the overwriteOutput ON
arcpy.gp.overwriteOutput = True

# Set workspace to be in memory for faster run time
arcpy.env.workspace = "in_memory"

outputMessage("Workspace is: {}".format(arcpy.env.workspace))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define variables
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

inData0 = r"U:\AOLSON\Working\temp\Water_Network.gdb\wMain"
inData1 = r"U:\AOLSON\Working\temp\Water_Network.gdb\wNonPressurizedPipes"

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Call Functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Populate a list of fields found in input dataset
fieldNames0 = [f.name for f in arcpy.ListFields(inData0)]
fieldNames1 = [f.name for f in arcpy.ListFields(inData1)] 

noMatchMains = [x for x in fieldNames0 if x not in fieldNames1]
noMatchPipes = [x for x in fieldNames1 if x not in fieldNames0]

outputMessage("Fields with no match in Pipes: {0}".format(noMatchMains))
outputMessage("Fields with no match in Mains: {0}".format(noMatchPipes))

mainDomains = [x for x in fieldNames0 if x not in fieldNames1]
pipeDomains = [x for x in fieldNames1 if x not in fieldNames0]



    