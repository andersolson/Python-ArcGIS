'''****************************************************************
utilities_networks_backup.py

Author(s): Alex Buchans, Justin Hampton, Anders Olson

Usage: Run script using python IDE or similar

Description: Script to backup all Operations SDE datasets to file gdb on 
             network drive. Datasets for backup are: Water Network, Storm Network,
             Wastewater Network, Communication_Network, Engineering, Facility Basedata,
             Facility Network, Misc Data, Parks Golf, Parks Webedit, Storm,
             Streets Network, Traffic Network, Utility Billing, Wastewater Misc,
             Water Misc, Water Treatment, Web Editing and database tables. 
              

Initial Release Date: 07/25/18

****************************************************************'''

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Import modules and packages
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  

import arcpy, datetime, os, sys, logging

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Configure logger 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Setup the logfile name
t = datetime.datetime.now()
logFile = r'C:\ScriptsForArcGIS\Prod\UtilitiesNetworksBackup\utilities_networks_backup'
logName = logFile + t.strftime("%y%m%d") + ".log"

# Define, format, and set logger levels 
logger = logging.getLogger("utilities_networks_backup")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logName)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s : line %(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define variables
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

current_date = datetime.datetime.now().strftime('%m%d%y')
# Define backup file location
backup = r'\\isys.arvada.org\Engr\Apps\Field_Assets\Backups\GEODB\OPERATIONS_{}.gdb'.format(current_date)

# Define SDE file location and name variables for datasets
sde = r'C:\ScriptsForArcGIS\OPERATIONS - Default.sde'
water_ds    = sde + '\OPERATIONS.OPS.WATER_NETWORK'
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

datasets = [water_ds, sewer_ds, storm_ds, comm_ds, engr_ds, facilB_ds, facilN_ds, miscData_ds,
            golf_ds, prksWeb_ds, strmMisc_ds, street_ds, traffic_ds, utlBill_ds, wwMisc_ds,
            wMisc_ds, wTreat_ds]

# Define spatial reference from ssLaterlLines: NAD_1983_StatePlane_Colorado_Central_FIPS_0502_Feet
sr = sewer_ds + '\OPERATIONS.OPS.ssLateralLine' 

# Define variables for tables in SDE
table0 = sde + '\OPERATIONS.dbo.assetback'
table1 = sde + '\OPERATIONS.dbo.AssetIDSQL'
table2 = sde + '\OPERATIONS.dbo.AssetIDTableMap'
table3 = sde + '\OPERATIONS.dbo.AssetTableCounts'
table4 = sde + '\OPERATIONS.dbo.SDE_compress_log'
table5 = sde + '\OPERATIONS.dbo.v_Arvada_PipeMaterials'
table6 = sde + '\OPERATIONS.dbo.cwAnalyzer'
table7 = sde + '\OPERATIONS.dbo.cwGenerator'
table8 = sde + '\OPERATIONS.dbo.cwHMI'
table9 = sde + '\OPERATIONS.dbo.cwMotor'
table10 = sde + '\OPERATIONS.dbo.cwMotorControl'
table11 = sde + '\OPERATIONS.dbo.cwPLC'
table12 = sde + '\OPERATIONS.dbo.cwRadioEquip'
table13 = sde + '\OPERATIONS.dbo.cwTransmitter'
table14 = sde + '\OPERATIONS.dbo.swImperviousTable'
table15 = sde + '\OPERATIONS.dbo.wHoist'
table16 = sde + '\OPERATIONS.dbo.wStationValve'
table17 = sde + '\OPERATIONS.dbo.wSurgeValve'
table18 = sde + '\OPERATIONS.dbo.wtActuator'
table19 = sde + '\OPERATIONS.dbo.wtAirCompressor'
table20 = sde + '\OPERATIONS.dbo.wtBackFlowPrevent'
table21 = sde + '\OPERATIONS.dbo.wtControllers'
table22 = sde + '\OPERATIONS.dbo.wtElectricEquip'
table23 = sde + '\OPERATIONS.dbo.wtFilterEquip'
table24 = sde + '\OPERATIONS.dbo.wtPump'
table25 = sde + '\OPERATIONS.dbo.wtValve'

tables = [table0, table1, table2, table3, table4, table5,
          table6, table7, table8, table9, table10, table11,
          table12, table13, table14, table15, table16,
          table17, table18, table19, table20, table21, table22,
          table23, table24, table25]

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Execute backup process
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

try:
    logger.info("Create File GDB")
    arcpy.CreateFileGDB_management(r'\\isys.arvada.org\Engr\Apps\Field_Assets\Backups\GEODB', r'OPERATIONS_{}.gdb'.format(current_date))
    
    # Create a feature dataset for each network in the new file gdb
    for dataset in datasets:
        logger.info("Copying Dataset: {}".format(dataset))
        arcpy.CreateFeatureDataset_management(backup, dataset.split('.')[-1], sr)
        
        # Define the workspace environment to run ListFCs for each network feature dataset 
        arcpy.env.workspace = dataset
        for fc in arcpy.ListFeatureClasses():
            arcpy.CopyFeatures_management(fc, os.path.join(backup, dataset.split('.')[-1], fc.split('.')[-1]))

except Exception as e:
    print e.args[0]
    logger.exception(str(e))

logging.shutdown()
