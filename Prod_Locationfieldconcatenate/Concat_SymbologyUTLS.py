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

swNetworkStructureFlds = ['NODETYPE','STATUS','STORMSYSTEM','SYMBOLOGY']
wSystemValveFlds       = []
wControlValveFlds      = []

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
'''
Concatnate 3 fields into the SYMBOLOGY field for input feature classes

Inputs:
inFC -- Feature class input for Water, Wastewater, or Storm Water datasets. e.g. wSystemValve, wControlValve, wNetworkStructure
fieldsList -- List of 3 field names that will be used to update the SYMBOLOGY field

Outputs:
output -- None

'''
def calculateSymbology(inFC, fieldsList):
    #Use update cursor to update any new or changed records in the inFC 
    with arcpy.da.UpdateCursor(inFC, fieldsList) as cursor:
        for row in cursor:
            symbol = "{}, {}, {}".format(row[0], row[1], row[2])
            
            #calc the symbology field if it doesn't match other fields
            if symbol != row[3]:
                row[3] = symbol
                
                #update the row
                cursor.updateRow(row)
                
            else:
                pass

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Call Functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

calculateSymbology()

logging.shutdown()

