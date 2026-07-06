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

