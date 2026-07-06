#-----------------------------------------------------------------------------
# sso-ad-list.py
#
# Author: Anders Olson 2026
#
# Usage: Script is run as a stand-alone script
#
# Description: Script pulls a list of all users found in AGOL organization and stores them
#              as a dataframe. The fields for the dataframe are last name, first name and
#              city email. The dataframe is filtered for users that have a city email address.
#              Then the list is saved as an excel file to tell Michael which users can be added
#              to the ArcGIS active directory user group
#
#-------------------------------------------------------------------------------

from arcgis.gis import GIS
import pandas as pd
from datetime import datetime as dt

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
# ================================#
# Define Messenger
# ================================#
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputWarning(msg):
    print(msg)
    arcpy.AddWarning(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
# ================================#
# Define functions
# ================================#
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# None

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
# ================================#
# Define variables and environments
# ================================#
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Define variable for run start date & time as a string
runStart = dt.now()

# Define string format for the start time
dtStr = runStart.strftime('%Y-%m-%d %H:%M:%S')
mdyDT = runStart.strftime('%Y%m%d')

# Connect to ArcGIS Online
c3GIS = GIS(profile='aolson_prfl2')