'''****************************************************************
Concat_SymbologyUTLS.py

Author(s): Anders Olson

Usage: Run script using python IDE or similar

Description: This script populates a symbology field for x,y, and z 
        datasets in the Utilities Ops database. The status, type, and z field
        are concatenated in the Symbology field to dictate how points are symbolized
        on maps and services. This python script is run in a 10hr time window 7am-6pm
        every 5 min on the gdsprod01 server. 
        con-CAT-nation =^._.^=        

****************************************************************'''

import arcpy
import os
import sys
import logging
import datetime

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Configure logger 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Setup the logfile name
t = datetime.datetime.now()
#logFile = r'C:\ScriptsForArcGIS\Prod\UtilitiesNetworksBackup\utilities_networks_backup'
logFile = r'U:\AOLSON\Working\temp\ConcatLog'
logName = logFile + t.strftime("%y%m%d") + ".log"

# Define, format, and set logger levels 
logger = logging.getLogger("ConcatLog")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logName)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s : line %(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("Running: {0}".format(sys.argv[0]))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define environment and messaging
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

logger.info("Define environment and messaging...")

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

# Set the overwriteOutput ON
arcpy.gp.overwriteOutput = True

# Set workspace to be in memory for faster run time
arcpy.env.workspace = "in_memory"

# Set a scratch workspace for storing any intermediate data
ScratchGDB = arcpy.env.scratchGDB

outputMessage("Scratch folder is: {}".format(ScratchGDB))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define variables
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

logger.info("Define Variables...")

# Define local testing gdb file location
gdb = r'U:\AOLSON\Working\temp\Concat_GDB.gdb'
wMain              = gdb + '\wMain'
wSystemValve       = gdb + '\wSystemValve'
wControlValve      = gdb + '\wControlValve'
swNetworkStructure = gdb + '\swNetworkStructure'

## Define SDE file location
#sde = r'C:\ScriptsForArcGIS\OPERATIONS - Default.sde'
#water_ds = sde + '\OPERATIONS.OPS.WATER_NETWORK'
#sewer_ds = sde + '\OPERATIONS.OPS.WASTEWATER_NETWORK'
#storm_ds = sde + '\OPERATIONS.OPS.STORM_NETWORK'
#datasets = [water_ds, sewer_ds, storm_ds]

swNetworkStructureFlds = ['OBJECTID','NODETYPE','STATUS','STORMSYSTEM','SYMBOLOGY']
swNetworkStructureLST  = []

wSystemValveFlds       = []
wSystemValveLST        = []

wControlValveFlds      = []
wControlValveLST       = []

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
'''
Make a nested list of desired fields and their attributes using feature class input and a list of 
desired fields for the output nested list. Nested list is used

Inputs:
inFC -- Feature class input for Water, Wastewater, or Storm Water. e.g. wSystemValve, wControlValve, wNetworkStructure
inFieldNames -- The desired fields to use in concatnate function to populate the symbology field.

Outputs:
outNstLst -- Output is a nested list that stores all the attribute field info for the input feature class.

'''
def buildNestedLst(inFC, inFieldNames, outNstLst):
    
    outputMessage("Running Build Nested List for {}...".format(inFC))
    
    for row in arcpy.da.SearchCursor(inFC, inFieldNames):
        
        # Create a temporary list for storing field values and then appending to 
        # nested list.
        #
        tmpLst = []
        tmpLst.append(row[0])
        tmpLst.append(row[1])
        tmpLst.append(row[2])
        tmpLst.append(row[3])
        tmpLst.append(row[4])
    
        outNstLst.append(tmpLst)
    
    outputMessage("Build Nested List Completed for {}".format(inFC))
    
buildNestedLst(swNetworkStructure, swNetworkStructureFlds, swNetworkStructureLST) 

outputMessage(swNetworkStructureLST)

logging.shutdown()

#Use cursor to update any new or changed records in swPipeEnd 
with arcpy.da.UpdateCursor("OPERATIONS.OPS.swPipeEnd", ["STATUS", "STORMSYSTEM", "SERVICESYMBOLOGY"]) as cursor:
    for row in cursor:
        symbol = "{}, {}".format(row[0], row[1])
        #calc servicesymbology field if it doesn't match other fields
        if symbol != row[2]:
            row[2] = symbol
        else: continue
        cursor.updateRow(row)