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

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

# Setup the logfile name
t = datetime.datetime.now()

##Local location for testing
#logFile = r'U:\AOLSON\Working\temp\ConcatLog'

#Server location for the real deal
logFile = r'C:\ScriptsForArcGIS\Test'

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
outputMessage("Running: {0}".format(sys.argv[0]))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define environment and messaging
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

logger.info("Define environment and messaging...")
outputMessage("Define environment and messaging...")

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

# Set the overwriteOutput ON
arcpy.gp.overwriteOutput = True

# Set a scratch workspace for storing any intermediate data
ScratchGDB = arcpy.env.scratchGDB
arcpy.env.workspace = ScratchGDB

## Set workspace to be in memory for faster run time
#arcpy.env.workspace = "in_memory"

logger.info("Workspace is: {}".format(arcpy.env.workspace))
outputMessage("Workspace is: {}".format(arcpy.env.workspace))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define variables
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

logger.info("Define Variables...")
outputMessage("Define Variables...")


'''
# Define local testing gdb file location
gdb = r'U:\AOLSON\Working\temp\Concat_GDB.gdb'
wSystemValve       = gdb + '\wSystemValve'
swNetworkStructure = gdb + '\swNetworkStructure'
swPipeEnds         = gdb + '\swPipeEnd'
'''

# Define SDE file location and feature classes
sde = r'C:\ScriptsForArcGIS\OPERATIONS - Default.sde'

# Water Network features
wSystemValve  = sde + '\OPERATIONS.OPS.WATER_NETWORK\wSystemValve'

# Storm Network features
swNetworkStructure = sde + '\OPERATIONS.OPS.STORM_NETWORK\swNetworkStructure'
swPipeEnds         = sde + '\OPERATIONS.OPS.STORM_NETWORK\swPipeEnd'


#Water Network Concat Fields
wSystemValveFlds       = ['VALVEUSE','VALVETYPE','STATUS','SYMBOLOGY']

#Storm Network Concat Fields
swNetworkStructureFlds = ['NODETYPE','STATUS','STORMSYSTEM','SYMBOLOGY']
swPipeEndsFlds         = ['STATUS','STORMSYSTEM','SYMBOLOGY']

#Waste Water Network
##Nothing yet

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
''' No functions'''
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Call Functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

logger.info('Running Concatenate function...')
outputMessage('Running Concatenate function...')

# Define the feature dataset workspace

##Local gdb for testing
#edit = arcpy.da.Editor(gdb)

#SDE for the real deal
edit = arcpy.da.Editor(sde)

'''
logger.info('\tProcessing wSystemValve')
outputMessage('\tProcessing wSystemValve')
edit.startEditing()
edit.startOperation()
#Use update cursor to update any new or changed records in the inFC 
with arcpy.da.UpdateCursor(wSystemValve, wSystemValveFlds) as cursor0:
    for row in cursor0:
        symbol = "{}, {}, {}".format(row[0], row[1], row[2])
        
        # Calc the symbology field if it doesn't match other fields. Rows 
        # that do not match the concat pattern have been recently changed and 
        # need to be updated. This IF statement makes sure only the currently
        # edited rows are updated and not all the rows in the data.
        if symbol != row[3]:
            row[3] = symbol
            
            #update the row
            cursor0.updateRow(row)
            
        else:
            pass
del cursor0

#edit.stopOperation()
#edit.stopEditing(True)
logger.info('\twSystemValves Complete!')
outputMessage('\twSystemValves Complete!')
'''

'''
logger.info('\tProcessing swNetworkStructure')
outputMessage('\tProcessing swNetworkStructure')
edit.startEditing()
edit.startOperation()
#Use update cursor to update any new or changed records in the inFC 
with arcpy.da.UpdateCursor(swNetworkStructure, swNetworkStructureFlds) as cursor1:
    for row in cursor1:
        symbol = "{}, {}, {}".format(row[0], row[1], row[2])
        
        # Calc the symbology field if it doesn't match other fields. Rows 
        # that do not match the concat pattern have been recently changed and 
        # need to be updated. This IF statement makes sure only the currently
        # edited rows are updated and not all the rows in the data.
        if symbol != row[3]:
            row[3] = symbol
            
            #update the row
            cursor1.updateRow(row)
            
        else:
            pass
del cursor1

#edit.stopOperation()
#edit.stopEditing(True)
logger.info('\tswNetworkStructure Complete!')
outputMessage('\tswNetworkStructure Complete!')
'''

logger.info('\tProcessing swPipeEnds')
outputMessage('\tProcessing swPipeEnds')
edit.startEditing(True,False)
edit.startOperation()
#Use update cursor to update any new or changed records in the inFC 

outputMessage(swPipeEnds)

cursor = arcpy.da.UpdateCursor(swPipeEnds, swPipeEndsFlds)

for row in cursor:
    symbol = "{}, {}".format(row[0], row[1])
    outputMessage(symbol)
    
    # Calc the symbology field if it doesn't match other fields. Rows 
    # that do not match the concat pattern have been recently changed and 
    # need to be updated. This IF statement makes sure only the currently
    # edited rows are updated and not all the rows in the data.
    if symbol != row[2]:
        row[2] = symbol
        
        outputMessage("Cursor update row...")
        #update the row
        cursor.updateRow(row)
        
    else:
        outputMessage("No cursor update row...")
        pass
del cursor

edit.stopOperation()
edit.stopEditing(True) 
logger.info('\tswPipeEnds Complete!')
outputMessage('\tswPipeEnds Complete!')


logger.info('Process Completed!')
outputMessage('Process Complete!')

logging.shutdown()