'''****************************************************************
FindDuplicateID.py
Author(s): Anders Olson
Usage: Run script using python IDE or similar
Description: 
        Script traverses the AssetID field for input dataset 
        to find duplicates. Duplicates cannot exist for CityWorks.
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

inData = r"U:\AOLSON\Working\temp\DumpingGrounds.gdb\sw_PipeEndDeleteList"

assetIDs = []

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Call Functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#Populate a list of Asset Ids found in asset id field
for row in arcpy.da.SearchCursor(inData, ['ASSETID']):
        assetIDs.append(row[0]) 

duplicates = [item for item, count in collections.Counter(assetIDs).items() if count > 1]

outputMessage(assetIDs)
outputMessage(duplicates)