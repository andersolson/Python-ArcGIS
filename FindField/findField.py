'''****************************************************************
utilities_networks_backup.py

Author(s): Anders Olson

Usage: Run script using python IDE or similar

Description:
              
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

'''
water_ds    = sde + '\OPERATIONS.OPS.WATER_NETWORK'
template_ds = sde + '\OPERATIONS.OPS.DatasetTemplate'
sewer_ds    = sde + '\OPERATIONS.OPS.WASTEWATER_NETWORK'
storm_ds    = sde + '\OPERATIONS.OPS.STORM_NETWORK'
comm_ds     = sde + '\OPERATIONS.OPS.COMMUNICATION_NETWORK'
engr_ds     = sde + '\OPERATIONS.OPS.ENGINEERING'
facilB_ds   = sde + '\OPERATIONS.OPS.FACILITY_BASEDATA'
facilN_ds   = sde + '\OPERATIONS.OPS.FACILITY_NETWORK'
miscData_ds = sde + '\OPERATIONS.OPS.MISC_DATA'
golf_ds     = sde + '\OPERATIONS.OPS.PARKS_GOLF'
prksWeb_ds  = sde + '\OPERATIONS.OPS.PARKS_WEBEDIT'
strmMisc_ds = sde + '\OPERATIONS.OPS.STORM'
street_ds   = sde + '\OPERATIONS.OPS.STREETS_NETWORK'
traffic_ds  = sde + '\OPERATIONS.OPS.TRAFFIC_NETWORK'
utlBill_ds  = sde + '\OPERATIONS.OPS.UTILITY_BILLING'
wwMisc_ds   = sde + '\OPERATIONS.OPS.WASTEWATER_MISC'
wMisc_ds    = sde + '\OPERATIONS.OPS.WATER_MISC'
wTreat_ds   = sde + '\OPERATIONS.OPS.WATER_TREATMENT'
wTreat2_ds  = sde + '\OPERATIONS.OPS.WATERTREATMENT'
webEdit_ds  = sde + '\OPERATIONS.OPS.Web_Editing'

datasets = [water_ds, template_ds, sewer_ds, storm_ds, comm_ds, engr_ds, facilB_ds, facilN_ds, miscData_ds,
            golf_ds, prksWeb_ds, strmMisc_ds, street_ds, traffic_ds, utlBill_ds, wwMisc_ds,
            wMisc_ds, wTreat_ds, wTreat2_ds, webEdit_ds]
'''

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