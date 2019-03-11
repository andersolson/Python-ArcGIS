'''****************************************************************
Concat_SymbologyTBX.pyt

Author(s): Anders Olson

Usage: Run script using python IDE or similar

Description: This script populates a symbology field for x,y, and z 
        datasets in the Utilities Ops database. The status, type, and z field
        are concatenated in the Symbology field to dictate how points are symbolized
        on maps and services. This python script is run in a 10hr time window 7am-6pm
        every 5 min on the gdsprod01 server. 
        con-CAT-nation =^._.^=        

****************************************************************'''

import arcpy
import os
import sys
import logging
import datetime

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Workflow Tools"
        self.alias = "Workflow Tools"

        # List of tool classes associated with this toolbox
        self.tools = [fieldConcat]

class fieldConcat(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Concatnate fields"
        self.description = "Concatnate attributes from multiple fields into another field."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""  
        
        in_features = arcpy.Parameter(
            displayName="Input Feature Layer",
            name="Input Datatype: GPFeatureLayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True)          

        fields = arcpy.Parameter(
            displayName="Field",
            name="Input Datatype: GPString",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")   
        
        value_table = arcpy.Parameter(  
            displayName = "Value Table",  
            name = "Input Datatype: value_table",  
            datatype = "GPValueTable",  
            parameterType = "Optional",  
            direction="Input")          
        
        value_table.columns =([["GPString", "Feature Class"], ["GPString","Field"]])  

        params = [in_features, fields, value_table]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Configure logger 
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        # Setup the logfile name
        t = datetime.datetime.now()
        
        ##Local location for testing
        #logFile = r'U:\AOLSON\Working\temp\ConcatLog'
        
        #Server location for the real deal
        logFile = r'C:\ScriptsForArcGIS\Prod\UtilitiesNetworksBackup\utilities_networks_backup'
        logName = logFile + t.strftime("%y%m%d") + ".log"
        
        # Define, format, and set logger levels 
        logger = logging.getLogger("ConcatLog")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(logName)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(filename)s : line %(lineno)d - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        logger.info("Running: {0}".format(sys.argv[0]))       
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define environment and messaging
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        logger.info("Define environment and messaging...")
        
        def outputMessage(msg):
            print(msg)
            arcpy.AddMessage(msg)
        
        def outputError(msg):
            print(msg)
            arcpy.AddError(msg)
        
        # Set the overwriteOutput ON
        arcpy.gp.overwriteOutput = True
        
        # Set workspace to be in memory for faster run time
        arcpy.env.workspace = "in_memory"
        
        # Set a scratch workspace for storing any intermediate data
        ScratchGDB = arcpy.env.scratchGDB
        
        outputMessage("Workspace is: {}".format(arcpy.env.workspace))        
        
        prodTable    = parameters[0].valueAsText
        compTable    = parameters[1].valueAsText

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define variables
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        logger.info("Define Variables...")
        
        logging.shutdown()