import arcpy
import os
import sys
import logging.config
import datetime
from datetime import datetime

# Setup the logfile name
t = datetime.now()
logFile = "C:/ScriptsForArcGIS/Prod/LocationFieldConcatenate/PROD_LocationFieldConcatenate"
logName = logFile + t.strftime("%y%m%d") + ".log"
# Setup logging
logger = logging.getLogger("PROD_LocationFieldConcatenate")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logName)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s : line %(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

#Codeblock for ssGravityMain Concatenate
codeblock = """
def loc_concat(ASSETGROUP,TROUBLESPOT):
        if TROUBLESPOT is None:
                return ASSETGROUP
        return ASSETGROUP + " " + TROUBLESPOT"""

try:
        #Set the workspace
        logger.info("Set The workspace")
        arcpy.env.workspace = "C:\\ScriptsForArcGIS\\OPERATIONS - DEFAULT.sde"

        #Set a variable for the workspace
        logger.info("Set a variable for the workspace")
        workspace = arcpy.env.workspace

        #Concatenate for "Location" field using "AssetGroup" and "TroubleSpot"     
        arcpy.CalculateField_management("ssGravityMain", "LOCATION", "loc_concat(!ASSETGROUP!,!TROUBLESPOT!)", "PYTHON_9.3", codeblock)

except Exception as e:
        print e.args[0]
        logger.exception(str(e))                

logging.shutdown()
