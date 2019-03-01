'''****************************************************************
Concat_SymbologyUTLS.py

Author(s): Anders Olson

Usage: Run script using python IDE or similar

Description: This script populates a symbology field for x,y, and z 
        datasets in the Utilities Ops database. The status, type, and z field
        are concatenated in the Symbology field to dictate how points are symbolized
        on maps and services. This python script is run in a 10hr time window 7am-6pm
        every 5 min on the gdsprod01 server.        

****************************************************************'''

import arcpy
import os
import sys
import logging
import datetime
from datetime import datetime

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Configure logger 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# Setup the logfile name
t = datetime.datetime.now()
#logFile = r'C:\ScriptsForArcGIS\Prod\UtilitiesNetworksBackup\utilities_networks_backup'
logFile = r'U:\AOLSON\Working\temp'
logName = logFile + t.strftime("%y%m%d") + ".log"

# Define, format, and set logger levels 
logger = logging.getLogger("ConcatLog")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logName)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s : line %(lineno)d - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)