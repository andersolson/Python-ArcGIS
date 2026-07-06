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
#              Then the list is saved as a csv file to give Michael, which he uses to
#              add employees to the Azure active directory user group.
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
working_dir = r'C:\Users\is_olson\Documents\Projects\SSO_Update\reports'

# Make a single output csv file
output_csv = f"{working_dir}\\list_of_city_users_{mdyDT}.csv"

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

# 1. Convert AGOL user list to pandas df
# Start with a dictionary for the user data object from agol
user_data = []

for user in all_users:

    # Split full name into first and last on the space character
    if user.fullName and " " in user.fullName:
        first, last = user.fullName.split(" ", 1)
        formatted_name = f"{last}, {first}"
    else:
        # fallback if fullName is missing or single-part
        formatted_name = user.fullName

    user_data.append({
        "Full Name": formatted_name,
        "email": user.email
    })


# Convert dictionary to a dataframe
df = pd.DataFrame(user_data)

# Select only rows where user has a city email address and make sure case-sensitive match is applied
email_df = df[df["email"].str.lower().str.endswith("c3gov.com")]

# Display header and top 5 records
print(df.head())

# # 2. Write the current dataframe to a csv file
# with pd.CSVWriter(output_xlsx) as writer:
#     active_matched.to_csv(writer, sheet_name='User_Account_Info', index=False)


