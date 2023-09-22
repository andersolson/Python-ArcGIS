'''****************************************************************
utilities_networks_backup.py

Author(s): Anders Olson

Usage: Run script using python IDE or similar

Description: Script runs through all Feature Datasets and their Feature 
       Classes to find a specific field.
              
Initial Release Date:
Last Edit:

****************************************************************'''

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Import modules and packages
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  

import arcpy

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Configure Messenger 
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
# Define variables
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Define SDE/GDB file location and name variables for datasets
sde = r'C:\ScriptsForArcGIS\OPERATIONS - Default.sde'
gdb = r'G:\Field_Assets\Backups\GEODB\OPERATIONS_052719.gdb'

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Execute Process
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

arcpy.env.workspace = gdb

datasets = arcpy.ListDatasets(feature_type='feature')
datasets = [''] + datasets if datasets is not None else []

for ds in datasets:
    for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
        print(fc)