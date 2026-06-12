#-----------------------------------------------------------------------------
# report-all-users.py
#
# Author: Anders Olson 2026
#
# Usage: Script is run as a stand-alone script
#
# Description: Script pulls a list of all users found in organization. Then,
#              creates a dataframe for the user data and a dataframe for David's
#              city employee list. Dataframes are joined and a report of active and
#              terminated users is created.
#
#-------------------------------------------------------------------------------

import arcpy
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

# Define working directory
working_dir = r'C:\Users\is_olson\Documents\Projects\SSO_Update'
arcpy.env.workspace = working_dir

# Output file: excel sheet containing all agol users with date stamp
all_users_xlsx = f'all_agol_users_{mdyDT}.xlsx'

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
# ================================#
# Start calling functions
# ================================#
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Output running message and start time
outputMessage(f'Running: {sys.argv[0]}\nStart Time: {dtStr}')

# Get a list of all org users
all_users = c3GIS.users.search(query='*',max_users=666)
outputMessage(f'Org has {len(all_users)} users')

# 1. Convert user list to a pandas df
# Start with a dictionary for the user data object from agol
user_data = []
for user in all_users:
    user_data.append({
        "username": user.username,
        "fullName": user.fullName,
        "email": user.email,
        "role": user.role,
        "type": user.userLicenseTypeId,
        "disabled": user.disabled,
        "lastLogin": user.lastLogin})

# Convert dictionary to a dataframe
df = pd.DataFrame(user_data)

# Reformat the date from UNIX timestamp to readable text date
df['lastLogin'] = pd.to_datetime(df['lastLogin'], unit='ms')

# 2. Convert dataframe to excel sheet
df.to_excel(all_users_xlsx, index=False)