import arcpy
import os
import sys
import logging.config
import datetime
from datetime import datetime

# Setup the logfile name
t = datetime.now()
#logFile = "C:/ScriptsForArcGIS/Prod/LocationFieldConcatenate/PROD_LocationFieldConcatenate"
logFile = "U:/AOLSON/Working/temp/PROD_LocationFieldConcatenate" #local test logfile
logName = logFile + t.strftime("%y%m%d") + ".log"
# Setup logging
logger = logging.getLogger("PROD_LocationFieldConcatenate")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logName)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s : line %(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

#Codeblock for ssGravityMain concatenate: 
# Row-by-row populate the LOCATION field with with the ASSETGOUP and TROUBLESPOT attributes.
codeblock0 = """
def loc_concat(ASSETGROUP,TROUBLESPOT):
        if TROUBLESPOT is None:
                return ASSETGROUP
        return ASSETGROUP + " " + TROUBLESPOT"""

#Codeblock for pksCWTrees concatenate: 
# Row-by-row populate the LOCATION field with with the SUB_DISTRICT and PARK_NAME attributes.
codeblock1 = """
def loc_concat(SUB_DISTRICT,PARK_NAME):
        if SUB_DISTRICT is None:
                return PARK_NAME
        return SUB_DISTRICT + "/" + PARK_NAME"""

try:
        #Set the workspace
        logger.info("Set workspace environemnt")
        #arcpy.env.workspace = "C:\\ScriptsForArcGIS\\OPERATIONS - DEFAULT.sde"
        arcpy.env.workspace = r"U:\AOLSON\Working\temp\SDE_Copy.gdb" #local test workspace

        #Define a variable for the workspace
        logger.info("Define workspace environemnt as a variable")
        workspace = arcpy.env.workspace

        #Concatenate for "Location" field using "AssetGroup" and "TroubleSpot" 
        logger.info("Run concatenate for ssGravityMain LOCATION field")
        arcpy.CalculateField_management("ssGravityMain", "LOCATION", "loc_concat(!ASSETGROUP!,!TROUBLESPOT!)", "PYTHON_9.3", codeblock0)
        
        #Concatenate for "Location" field using "Sub_District" and "Park_Name" 
        logger.info("Run concatenate for pksCWTrees LOCATION field")
        arcpy.CalculateField_management("pksCWTrees", "LOCATION", "loc_concat(!SUB_DISTRICT!,!PARK_NAME!)", "PYTHON_9.3", codeblock1)        

except Exception as e:
        print e.args[0]
        logger.exception(str(e))                

logging.shutdown()
