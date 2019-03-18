import arcpy
import os
import sys
import logging.config
import datetime
from datetime import datetime

# Setup the logfile name
t = datetime.now()
logFile = "C:/ScriptsForArcGIS/log/ProdCompress"
logName = logFile + t.strftime("%y%m%d") + ".log"
# Setup logging
logger = logging.getLogger("prod_Compress")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logName)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s : line %(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

try:
    #Set the workspace
    logger.info("Set the Workspace")
    arcpy.env.workspace = "C:\\ScriptsForArcGIS\\OPERATIONS - Arcadmin.sde"

    #Set a variable for the workspace
    logger.info("Set a variable for the Workspace")
    workspace = arcpy.env.workspace

    # block new connections to the database.
    logger.info("block new connections to the database")
    arcpy.AcceptConnections(workspace, False)

    #disconnect all users from the database.
    logger.info("disconnect all users from the database")
    arcpy.DisconnectUser(workspace, "ALL")

    # Get a list of versions to pass into the ReconcileVersions tool.
    logger.info("Get a list of versions to pass into the ReconcileVersions tool")
    versionList = arcpy.ListVersions(workspace)

    # Execute the ReconcileVersions tool.
    logger.info("Execute the ReconcileVersions tool")
    arcpy.env.overwriteOutput = True
    arcpy.ReconcileVersions_management(workspace, "ALL_VERSIONS", "dbo.DEFAULT", versionList, "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", "KEEP_VERSION", "C:\ScriptsForArcGIS\log\TESTreconcilelog.txt")
    arcpy.ReconcileVersions_management(workspace, "BLOCKING_VERSIONS", "dbo.DEFAULT", versionList, "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", "KEEP_VERSION", "C:\ScriptsForArcGIS\log\TESTreconcilelog.txt")

    # Run the compress tool. 
    logger.info("Run the compress tool")
    arcpy.Compress_management(workspace)

    # Allow new connections to the database.
    logger.info("Allow new connections to the database")
    arcpy.AcceptConnections(workspace, True)

except Exception as e:
    print e.args[0]
    logger.exception(str(e))		

logging.shutdown()
