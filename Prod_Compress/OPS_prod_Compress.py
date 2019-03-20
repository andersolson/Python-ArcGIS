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

# Create a messager for error handling
def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

try:
    #Set the workspace
    logger.info("Defining the Workspace...")
    arcpy.env.workspace = "C:\\ScriptsForArcGIS\\OPERATIONS - Arcadmin.sde"
    outputMessage("Defining the Workspace...")

    #Set a variable for the workspace
    logger.info("Define variable for the Workspace...")
    outputMessage("Define variable for the Workspace...")
    workspace = arcpy.env.workspace
    logger.info("Workspace is: {0}".format(workspace))
    outputMessage("Workspace is: {0}".format(workspace))
    
    #Get a list of connected users.
    logger.info("Get a list of connected users...")
    outputMessage("Get a list of connected users...")
    userList = arcpy.ListUsers(workspace)
    userNames = [user.Name for user in userList]
    logger.info("Connected users are:")
    logger.info(userNames)
    outputMessage("Connected users are:")
    outputMessage(userNames)
    
    #Block new connections to the database.
    logger.info("Block new connections to the database...")
    outputMessage("Block new connections to the database...")
    arcpy.AcceptConnections(workspace, False)
    logger.info("Connections blocked.")
    outputMessage("Connections blocked.")
    
    #Disconnect all users from the database.
    logger.info("Disconnect all users from the database...")
    outputMessage("Disconnect all users from the database...")
    arcpy.DisconnectUser(workspace, "ALL")
    logger.info("All users disconnected.")
    outputMessage("All users disconnected.")

    #Get a list of versions to pass into the ReconcileVersions tool.
    logger.info("Get a list of versions to pass into Reconcile Versions tool...")
    outputMessage("Get a list of versions to pass into Reconcile Versions tool...")
    versionList = arcpy.ListVersions(workspace)
    logger.info("Version list is: {0}".format(versionList))
    outputMessage("Version list is: {0}".format(versionList))
    
    #Execute the ReconcileVersions tool.
    logger.info("Execute the Reconcile Versions tool...")
    outputMessage("Execute the Reconcile ALL Versions tool...")
    arcpy.env.overwriteOutput = True
    arcpy.ReconcileVersions_management(workspace, "ALL_VERSIONS", "dbo.DEFAULT", versionList, "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", "KEEP_VERSION", "C:\ScriptsForArcGIS\log\ReconcileALL_log.txt")
    logger.info("Execute the Reconcile BLOCKING tool...")
    outputMessage("Execute the Reconcile BLOCKING Versions tool...")
    arcpy.ReconcileVersions_management(workspace, "BLOCKING_VERSIONS", "dbo.DEFAULT", versionList, "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_TARGET_VERSION", "POST", "KEEP_VERSION", "C:\ScriptsForArcGIS\log\ReconcileBLOCK_log.txt")
    logger.info("Reconcile complete.")
    outputMessage("Reconcile complete.")

    #Run the compress tool. 
    logger.info("Run the compress tool...")
    outputMessage("Run the compress tool...")
    arcpy.Compress_management(workspace)
    logger.info("Compress complete.")
    outputMessage("Compress complete.")

    #Allow new connections to the database.
    logger.info("Allow new connections to the database...")
    outputMessage("Allow new connections to the database...")
    arcpy.AcceptConnections(workspace, True)
    logger.info("New connections allowed.")
    outputMessage("New connections allowed.")

except Exception as e:
    print(e.args[0])
    logger.exception(str(e))

logging.shutdown()
