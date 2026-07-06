#-----------------------------------------------------------------------------
# users-report.py
#
# Author: Anders Olson 2026
#
# Usage: Script is run as a stand-alone script
#
# Description: Script
#
#-------------------------------------------------------------------------------

from datetime import datetime as dt
import pandas as pd
from arcgis.gis import GIS

# Connect to the org GIS
gis = GIS("home")

# Define variable for run start date & time as a string
runStart = dt.now()
print(runStart)

# Search org for all content on the site
# Leave the type param blank to return all types
itemsList = gis.content.search('', '', max_items = 10000)
print(len(itemsList))

# # Fast Report: Write the list to a dataframe excluding Size and Shared-With
# dfItems = pd.concat([pd.DataFrame([{'Title':i.title, 'Type':i.type, 'Owner':i.owner, 'Description':i.description,
#                                     'Tags':i.tags, 'Snippet':i.snippet, 'Categories':i.categories, 'Access':i.access,
#                                     'URL':i.url} for i in itemsList])
#                      ]
#                     )

# Slow Report: Write the complete list to a dataframe including all fields, Size & Shared-With
dfItems = pd.concat([pd.DataFrame([{'Title':i.title, 'Type':i.type, 'Size':i.size, 'Owner':i.owner,
                                    'Description':i.description, 'Tags':i.tags, 'Snippet':i.snippet,
                                    'Categories':i.categories, 'Access':i.access, 'URL':i.url,
                                    'Shared With': i.shared_with} for i in itemsList])
                     ]
                    )

dfItems.reset_index(inplace=True, drop=True)

# Write to a csv report
csv = r'C:\Users\is_olson\Documents\Projects\ArcGIS-for-Server\UserReports\LongReport_050724.csv'
# csv = r'C:\Users\is_olson\Documents\Projects\ArcGIS-for-Server\UserReports\ShortReport_050724.csv'
myCSV = dfItems.to_csv(csv)

endTime = dt.now()-runStart
print(endTime)