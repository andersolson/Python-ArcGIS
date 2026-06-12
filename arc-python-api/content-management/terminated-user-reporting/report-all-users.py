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
working_dir = r'C:\Users\is_olson\Documents\Projects\SSO_Update\reports'

# Output file: excel sheet containing all agol users with date stamp
all_users_xlsx = f'{working_dir}\\all_agol_users_{mdyDT}.xlsx'

# Input: david's weekly excel report
employee_status_report = f'{working_dir}\\City_users_positions_GIS_integration.csv'

# Output: cleaned up excel version of david's report for reference, only active employees
employee_status_xlsx = f'{working_dir}\\City_users_positions_GIS_integration.xlsx'

# Output: joined report of matching active employees
active_joined_report = f'{working_dir}\\joined_active_user_report.xlsx'

# Output: joined report of nonactive employees
nonactive_joined_report = f'{working_dir}\\joined_nonactive_user_report.xlsx'

# Make a single output file
output_xlsx = f"{working_dir}\\agol_city_employee_match_report_{mdyDT}.xlsx"


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

# Reformat email address case for joining
df['email'] = df['email'].str.lower()

# 2. Convert dataframe to excel sheet
df.to_excel(all_users_xlsx, index=False)

# 3. Convert city employee status report to dataframe
# Read David's report to a dataframe
df2 = pd.read_csv(employee_status_report)

# Change email case to lower
df2['[Email]'] = df2['[Email]'].str.lower()

# Only active employees
active_employees = df2[df2['[Employee_Status]'] == 'Active']

# Export dataframe back to excel for reference
active_employees.to_excel(employee_status_xlsx, index=False)

# 4. Join dataframes on email
# Join df and df2 using common email field
merged = df.merge(active_employees, left_on='email', right_on='[Email]', how='left')
outputMessage(f'Found {len(merged)} matching active employees')

# Output active employee matches to excel sheet
merged.to_excel(active_joined_report, index=False)

# 5. Create a dataframe of terminated/retired/inactive employees
# Only deactivated employees
inactive_statuses = ['Terminated', 'Inactive', 'Retiree Gen', 'Retired']
deactivated_employees = df2[df2['[Employee_Status]'].isin(inactive_statuses)]

# Join df and df2 using common email field
merged = df.merge(deactivated_employees, left_on='email', right_on='[Email]', how='left')
outputMessage(f'Found {len(merged)} matching deactivated employees')

# Output active employee matches to excel sheet
merged.to_excel(nonactive_joined_report, index=False)

# 6. Write all three dataframes to a sheet in one excel file

with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
    active_matched.to_excel(writer, sheet_name='Active_Matched', index=False)
    active_unmatched.to_excel(writer, sheet_name='Unmatched', index=False)
    deactivated_with_accounts.to_excel(writer, sheet_name='Deactivated_With_Accounts', index=False)

outputMessage("Report built successfully!")
