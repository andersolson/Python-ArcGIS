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
import re

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
        self.label = "Concatenate Fields"
        self.description = "Concatenate attribute values from multiple fields into another field."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""  
        
        param0 = arcpy.Parameter(
            displayName="Input Feature Layer",
            name="Input Feature for Concatenate",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")          

        param1 = arcpy.Parameter(
            displayName="Fields",
            name="Input Fields for Concatenate",
            datatype="Field",
            parameterType="Required",
            direction="Input",
            multiValue=True)   
        
        param2 = arcpy.Parameter(
            displayName="Target Field",
            name="Target Field for Concatenate",
            datatype="Field",
            parameterType="Required",
            direction="Input")         
        
        param1.parameterDependencies = [param0.name]
        param2.parameterDependencies = [param0.name]

        params = [param0,param1,param2]
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
        # Define environment and messaging
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        #logger.info("Define environment and messaging...")
        
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
        
        ## Set a scratch workspace for storing any intermediate data
        #ScratchGDB = arcpy.env.scratchGDB

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define variables
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        inFeature       = parameters[0].valueAsText        
        fieldSelection  = parameters[1].valueAsText 
        targetField     = parameters[2].valueAsText 
        
        #Local gdb for testing and sde for the real deal
        try:
            editorWrksp     = re.match("(.*?)sde",inFeature).group()
            outputMessage("Workspace is: {}".format(editorWrksp))
        except:
            editorWrksp     = re.match("(.*?)gdb",inFeature).group()
            outputMessage("Workspace is: {}".format(editorWrksp))
        
        #outputMessage(editorWrksp)
        
        # Split the field selection input at ';' character and simultaneously
        # add the selected fields to a list.
        fieldLst = fieldSelection.split(";")
        
        # Append the target field name to the end of the selected fields list
        fieldLst.append(targetField)

        edit = arcpy.da.Editor(editorWrksp)     
        
        # Open an editor and start the editing function
        edit.startEditing()
        edit.startOperation()        

        with arcpy.da.UpdateCursor(inFeature, fieldLst) as cursor:
            
            for row in cursor:
                
                # Create the concatenate string, but exclude the last element in 
                # the list because it is the target field. 
                # Use the new concat string to populate the target field.
                concatValue = ",".join(map(str, row[:-1]))           
                
                #calc the target field if it does not match the concat pattern
                if row[-1] != concatValue:
                    
                    # Target field row is equal to the new string
                    row[-1] = concatValue
                    
                    #update the target row
                    cursor.updateRow(row)
                    
                else:
                    pass            
        
        # Close the editor and save edits
        edit.stopOperation()
        edit.stopEditing(True)     