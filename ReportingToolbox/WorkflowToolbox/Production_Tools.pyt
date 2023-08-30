import arcpy, os
import ftplib
from ftplib import FTP
import os, sys, os.path
import re
import glob
import shutil
from datetime import *
from dateutil.relativedelta import relativedelta

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Workflow Tools"
        self.alias = "Workflow Tools"

        # List of tool classes associated with this toolbox
        self.tools = [dataUpload,dataDownload,qaqcCheck]

class dataUpload(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2. Load Completed Metros to Archive"
        self.description = "Load Completed Metros from Production Table to Completed Table."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""  
        
        param0 = arcpy.Parameter(
            displayName="Database Connection to Metro 2.0 Production Table",
            name="Input Production Table",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")          

        param1 = arcpy.Parameter(
            displayName="Database Connection to Metro 2.0 Completed Table",
            name="Input Completed Table",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")   
        
        params = [param0,param1]
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

        def outputMessage(msg):
            #print(msg)
            arcpy.AddMessage(msg)
        
        def outputError(msg):
            #print(msg)
            arcpy.AddError(msg)
            
        # Set the overwriteOutput ON
        arcpy.gp.overwriteOutput = True
        
        # Set the workspace
        arcpy.env.workspace = "in_memory"    
        ScratchGDB = arcpy.env.scratchGDB
        
        prodTable    = parameters[0].valueAsText
        compTable    = parameters[1].valueAsText
        
        prodList = [] #List of completed Metros found in Production table
        compList = [] #List of Metros found in Completed table
        
        #Select only Completed Metros from the Production table
        outTable    = ScratchGDB + "\\outTable"
        whereClause = "Prod_State = 'Completed'" 
        arcpy.TableSelect_analysis(prodTable, outTable, whereClause)
        
        #Build lists of Product Names in production table
        cursor = arcpy.da.SearchCursor(outTable, ['Prod_Name'])
        for row in cursor:
            prodList.append(row[0])
        del row, cursor
        
        outputMessage("{0} Items in prodList".format(len(prodList)))
        
        #Build list of Product Names in completed table
        cursor = arcpy.da.SearchCursor(compTable, ['Prod_Name'])
        for row in cursor:
            compList.append(row[0])
        del row, cursor
            
        outputMessage("{0} Items in compList".format(len(compList)))
        
        #Look for duplicates in destination table before running append
        for item in prodList:
            if item not in compList:
                whereClause = "Prod_Name = '{0}'".format(item) 
                arcpy.TableSelect_analysis(prodTable, "itemTable", whereClause)  
                outputMessage("Appending record: {0}".format(item))
                arcpy.Append_management("itemTable", compTable, "NO_TEST", "","")
            else:
                pass
                #outputMessage("{0} already exists in destination table".format(item))
        del item, prodList

class dataDownload(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "3. Download Metro 2.0 Metadata"
        self.description = "Update metadata with new data."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""   
        
        param0 = arcpy.Parameter(
            displayName="Database Connection to Current Metadata feature class",
            name="Input Metadata dataset",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")        
        
        param1 = arcpy.Parameter(
            displayName="Database Connection to Completed Table",
            name="Input Completed Table",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")      

        params = [param0,param1]
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
        
        def outputMessage(msg):
            print(msg)
            arcpy.AddMessage(msg)
        
        def outputError(msg):
            print(msg)
            arcpy.AddError(msg)
        
        now = date.today()
        
        #writeTo.write(str(now) + "\n")
        
        # Set the overwriteOutput ON
        arcpy.gp.overwriteOutput = True
        
        # Set the workspace
        arcpy.env.workspace = "in_memory"
        ScratchFolder       = arcpy.env.scratchFolder  
        ScratchGDB          = arcpy.env.scratchGDB
        
        outputMessage("Scratch folder is: {}".format(ScratchGDB))
        
        #Inputs: Metadata for HVA and MDA to compare with what is in the Completed Table
        #Metadata         = r"C:\Users\aolson\Documents\Working\Plus_Metro\PLUS_METRO_011017.gdb\PlusMetro\Metadata"
        #completeTable    = r"C:\Users\aolson\Documents\Working\Plus_Metro\PLUS_METRO_011017.gdb\CompletedMetrosTable"
        Metadata         = parameters[0].valueAsText  #Input database connection to Metadata dataset
        completeTable    = parameters[1].valueAsText  #Input database connection to completed table
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define functions
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        #Format MDA data from the ftp pull that does not have a MOSAIC shapefile in the metadata
        def formatMDA(stripShape,pixelShape):
            dDir    = ScratchFolder + '\\Products'
            clipOut = ScratchFolder + '\\testClip.shp'
            joinOut = dDir + '\\{0}.shp'.format(product)  
        
            # Repair the geometry... JUST IN CASE!!
            arcpy.RepairGeometry_management(stripShape,"DELETE_NULL") 
            # Repair the geometry... JUST IN CASE!!
            arcpy.RepairGeometry_management(pixelShape,"DELETE_NULL")      
        
            # Clip the strip shapefile to the pixel/AOI shapefile
            arcpy.Clip_analysis(stripShape, pixelShape, clipOut)
        
            # Run a spatial join to add the attributes of the clipShape with the
            # pixel shape
            arcpy.SpatialJoin_analysis(pixelShape, clipOut, 
                                       joinOut, 
                                       "JOIN_ONE_TO_ONE", 
                                       "KEEP_ALL", "","INTERSECT")
        
            # ---------------------------------------------------------------------------
            # Calculate and create Prod_Name field
            # ---------------------------------------------------------------------------
            # Add field named "Prod_Name"
            arcpy.AddField_management(joinOut,"Prod_Name","TEXT","#","#","254","Product_Name","NULLABLE")
            # Calculate values for !Prod_Name!
            arcpy.CalculateField_management(joinOut,"Prod_Name","'{0}'".format(product),"PYTHON_9.3","#")
        
            # ---------------------------------------------------------------------------
            # Calculate and create CatID field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" to store attribute
            arcpy.AddField_management(joinOut,"tmp","TEXT","#","#","254","tmp","NULLABLE")
            # Calculate values for "tmp" from !stripDesc!
            arcpy.CalculateField_management(joinOut,"tmp","!stripDesc!","PYTHON_9.3","#")  
            # Add field named "CatID" with proper formating
            arcpy.AddField_management(joinOut,"CatID","TEXT","#","#","254","CatID","NULLABLE","NON_REQUIRED","#")    
            # Calculate values for "CatID" from !tmp!
            arcpy.CalculateField_management(joinOut,"CatID","!tmp!","PYTHON_9.3","#")    
            # Delete "tmp" field 
            arcpy.DeleteField_management(joinOut,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create ONA field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" with to store attribute
            arcpy.AddField_management(joinOut,
                                      field_name="tmp",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "tmp" from !offNadir!
            arcpy.CalculateField_management(joinOut,"tmp","!offNadir!","PYTHON_9.3","#")  
            # Add field named "ONA" with proper formating
            arcpy.AddField_management(joinOut,
                                      field_name="ONA",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="ONA",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "ONA" from !tmp!
            arcpy.CalculateField_management(joinOut,"ONA","!tmp!","PYTHON_9.3","#") 
            # Delete "tmp" field 
            arcpy.DeleteField_management(joinOut,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create Acq_Date field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" to store attribute
            arcpy.AddField_management(joinOut,
                                      field_name="tmp",field_type="DATE",field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate field from !acquisitio! 
            dateBlock = """import datetime
from datetime import date, datetime, timedelta
def dateConvert(inString):
    newDate = inString[0:10]
    aDate = datetime.strptime(newDate, "%Y-%m-%d")
    return aDate"""
            arcpy.CalculateField_management(joinOut,"tmp","dateConvert(!acquisitio!)","PYTHON_9.3",dateBlock)
            # Delete "acquisitio" field with wrong formating
            arcpy.DeleteField_management(joinOut,"acquisitio")
            # Add field "Acq_Date" with proper formating
            arcpy.AddField_management(joinOut,
                                      field_name="Acq_Date",field_type="DATE",field_alias="Acq_Date",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "Acq_Date" from "tmp"
            arcpy.CalculateField_management(joinOut,"Acq_Date","!tmp!","PYTHON_9.3","#")
            # Delete "tmp" field
            arcpy.DeleteField_management(joinOut,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create AREA_KM2 field
            # ---------------------------------------------------------------------------
            # Add field named "AREA_KM2" with proper formating
            arcpy.AddField_management(joinOut,
                                      field_name="AREA_KM2",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="AREA_KM2",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "AREA_KM2" from !tmp!
            arcpy.CalculateField_management(joinOut,"AREA_KM2","!shape.area@squarekilometers!","PYTHON_9.3","#") 
            # Delete "tmp" field 
            arcpy.DeleteField_management(joinOut,"tmp")
        
            # ---------------------------------------------------------------------------
            # Delete remaining fields
            # ---------------------------------------------------------------------------
            # List of fields to be deleted
            dropFields = ["Join_Count","TARGET_FID","prodDesc","volNum","stripDesc", "sunAzimuth", "offNadir"]
            # Delete fields that do not match schema
            arcpy.DeleteField_management(joinOut,dropFields)    
        
            # Append the new shapefile to the Metadata feature class on SDE
            arcpy.Append_management(joinOut,Metadata,"NO_TEST","","")
        
        #Format MDA data from the ftp pull that has a MOSAIC shapefile in the metadata
        def formatMDAmeta(mosaicShape):
            #dDir    = 'C:\\Users\\aolson\\Documents\\Working\\Plus_Metro\\PYTHON\\FTP_Metadata\\Products'
            #outShp = dDir + '\\{0}.shp'.format(product)    
        
            # Repair the geometry... JUST IN CASE!!
            arcpy.RepairGeometry_management(mosaicShape,"DELETE_NULL")    
        
            # ---------------------------------------------------------------------------
            # Calculate and create Prod_Name field
            # ---------------------------------------------------------------------------
            # Add field named "Prod_Name"
            arcpy.AddField_management(mosaicShape,"Prod_Name","TEXT","#","#","254","Product_Name","NULLABLE")
            # Calculate values for !Prod_Name!
            arcpy.CalculateField_management(mosaicShape,"Prod_Name","'{0}'".format(product),"PYTHON_9.3","#")
        
            # ---------------------------------------------------------------------------
            # Calculate and create CatID field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" to store attribute
            arcpy.AddField_management(mosaicShape,"tmp","TEXT","#","#","254","tmp","NULLABLE")
            # Calculate values for "tmp" from !stripDesc!
            arcpy.CalculateField_management(mosaicShape,"tmp","!imageIdStr!","PYTHON_9.3","#")  
            # Add field named "CatID" with proper formating
            arcpy.AddField_management(mosaicShape,"CatID","TEXT","#","#","254","CatID","NULLABLE","NON_REQUIRED","#")    
            # Calculate values for "CatID" from !tmp!
            arcpy.CalculateField_management(mosaicShape,"CatID","!tmp!","PYTHON_9.3","#")    
            # Delete "tmp" field 
            arcpy.DeleteField_management(mosaicShape,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create Acq_Date field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" to store attribute
            arcpy.AddField_management(mosaicShape,
                                      field_name="tmp",field_type="DATE",field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate field from !acquisitio! 
            dateBlock = """import datetime
from datetime import date, datetime, timedelta
def dateConvert(inString):
    newDate = inString[0:10]
    aDate = datetime.strptime(newDate, "%Y-%m-%d")
    return aDate"""
            arcpy.CalculateField_management(mosaicShape,
                                            field="tmp",expression="dateConvert(!acqDate!)",
                                            expression_type="PYTHON_9.3",code_block=dateBlock)
            # Add field "Acq_Date" with proper formating
            arcpy.AddField_management(mosaicShape,
                                      field_name="Acq_Date",field_type="DATE",field_alias="Acq_Date",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "Acq_Date" from "tmp"
            arcpy.CalculateField_management(mosaicShape,"Acq_Date","!tmp!","PYTHON_9.3","#")
            # Delete "tmp" field
            arcpy.DeleteField_management(mosaicShape,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create ONA field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" with to store attribute
            arcpy.AddField_management(mosaicShape,
                                      field_name="tmp",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "tmp" from !offNadir!
            arcpy.CalculateField_management(mosaicShape,"tmp","!offNadir!","PYTHON_9.3","#")  
            # Add field named "ONA" with proper formating
            arcpy.AddField_management(mosaicShape,
                                      field_name="ONA",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="ONA",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "ONA" from !tmp!
            arcpy.CalculateField_management(mosaicShape,"ONA","!tmp!","PYTHON_9.3","#") 
            # Delete "tmp" field 
            arcpy.DeleteField_management(mosaicShape,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create AREA_KM2 field
            # ---------------------------------------------------------------------------
            # Add field named "AREA_KM2" with proper formating
            arcpy.AddField_management(mosaicShape,
                                      field_name="AREA_KM2",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="AREA_KM2",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "AREA_KM2" from !tmp!
            arcpy.CalculateField_management(mosaicShape,"AREA_KM2","!shape.area@squarekilometers!","PYTHON_9.3","#") 
            # Delete "tmp" field 
            arcpy.DeleteField_management(mosaicShape,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create CC field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" with to store attribute
            arcpy.AddField_management(mosaicShape,
                                      field_name="tmp",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "tmp" from !cloudCover!
            arcpy.CalculateField_management(mosaicShape,"tmp","!cloudCover!","PYTHON_9.3","#")  
            # Add field named "ONA" with proper formating
            arcpy.AddField_management(mosaicShape,
                                      field_name="CC",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="Cloud_Cover",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "ONA" from !tmp!
            arcpy.CalculateField_management(mosaicShape,"CC","!tmp!","PYTHON_9.3","#") 
            # Delete "tmp" field 
            arcpy.DeleteField_management(mosaicShape,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create SUNEL field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" with to store attribute
            arcpy.AddField_management(mosaicShape,
                                      field_name="tmp",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "tmp" from !sunEl!
            arcpy.CalculateField_management(mosaicShape,"tmp","!sunEl!","PYTHON_9.3","#")  
            # Delete "sunEl" field 
            arcpy.DeleteField_management(mosaicShape,"sunEl")
            # Add field named "SUNEL" with proper formating
            arcpy.AddField_management(mosaicShape,
                                      field_name="SUNEL",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="SUNEL",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "SUNEL" from !tmp!
            arcpy.CalculateField_management(mosaicShape,"SUNEL","!tmp!","PYTHON_9.3","#") 
            # Delete "tmp" field 
            arcpy.DeleteField_management(mosaicShape,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create SENSOR field
            # ---------------------------------------------------------------------------
            # Add field named "SENSOR"
            arcpy.AddField_management(mosaicShape,"SENSOR","TEXT","#","#","254","SENSOR","NULLABLE")
            # Calculate values for !Prod_Name!
            arcpy.CalculateField_management(mosaicShape,"SENSOR","!satellite!","PYTHON_9.3","#")
        
            # ---------------------------------------------------------------------------
            # Calculate and create ACCURACY field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" with to store attribute
            arcpy.AddField_management(mosaicShape,
                                      field_name="tmp",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "tmp" from !sunEl!
            arcpy.CalculateField_management(mosaicShape,"tmp","!absAcc!","PYTHON_9.3","#")  
            # Add field named "ACCURACY" with proper formating
            arcpy.AddField_management(mosaicShape,
                                      field_name="ACCURACY",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="ACCURACY",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "ACCURACY" from !tmp!
            arcpy.CalculateField_management(mosaicShape,"ACCURACY","!tmp!","PYTHON_9.3","#") 
            # Delete "tmp" field 
            arcpy.DeleteField_management(mosaicShape,"tmp")
        
            # ---------------------------------------------------------------------------
            # Delete remaining fields
            # ---------------------------------------------------------------------------
            # List of fields to be deleted
            dropFields = ["imageIdStr", "acqDate", "horError", "gsd", "cloudCover", "offNadir",
                          "scanAz", "scanDir", "collectAz", "collectEl", "sunAz","satellite",
                          "prodDate", "currDate", "collDate", "absAcc", "absAccUnit", "relAcc", "relAccUnit"]
            # Delete fields that do not match schema
            arcpy.DeleteField_management(mosaicShape,dropFields)
        
            # Append the new shapefile to the Metadata feature class on SDE
            arcpy.Append_management(mosaicShape,Metadata,"NO_TEST","","")    
        
        #Format HVA metadata shapefiles from the ftp pull        
        def formatHVA(metaShape):
            dDir          = ScratchFolder + '\\Products'
            dissolve_meta = dDir + "\\dis_{0}.shp".format(product)
            proj_meta     = dDir + "\\prj_{0}.shp".format(product)
            
            ##Check if the metadata shapefile path exists in scratch folder
            #if os.path.exists(metaShape) is True:
                
            # Repair the geometry... JUST IN CASE!!
            arcpy.RepairGeometry_management(metaShape,"DELETE_NULL")
        
            # Dissolve metadata product based on the catid
            arcpy.Dissolve_management(metaShape, dissolve_meta, 
                                      ["CATALOG_ID","ACQ_DATE","ONA","CC", 
                                       "SUNEL","SENSOR","ACCURACY","TILE_TYPE","VERSION"],"","MULTI_PART","DISSOLVE_LINES")
        
            # ---------------------------------------------------------------------------
            # Calculate and create Prod_Name field
            # ---------------------------------------------------------------------------
            # Add field named "Prod_Name"
            arcpy.AddField_management(dissolve_meta,"Prod_Name","TEXT","#","#","254","Product_Name","NULLABLE")
            # Calculate values for !Prod_Name!
            arcpy.CalculateField_management(dissolve_meta,"Prod_Name","'{0}'".format(product),"PYTHON_9.3","#")
        
            # ---------------------------------------------------------------------------
            # Calculate and create CatID field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" to store attribute
            arcpy.AddField_management(dissolve_meta,"tmp","TEXT","#","#","254","tmp","NULLABLE")
            # Calculate values for "tmp" from !stripDesc!
            arcpy.CalculateField_management(dissolve_meta,"tmp","!CATALOG_ID!","PYTHON_9.3","#")  
            # Add field named "CatID" with proper formating
            arcpy.AddField_management(dissolve_meta,"CatID","TEXT","#","#","254","CatID","NULLABLE","NON_REQUIRED","#")    
            # Calculate values for "CatID" from !tmp!
            arcpy.CalculateField_management(dissolve_meta,"CatID","!tmp!","PYTHON_9.3","#")    
            # Delete "tmp" field 
            arcpy.DeleteField_management(dissolve_meta,["tmp","CATALOG_ID"])
        
            # ---------------------------------------------------------------------------
            # Calculate and create Acq_Date field
            # ---------------------------------------------------------------------------
            # Add field named "tmp" to store attribute
            arcpy.AddField_management(dissolve_meta,
                                      field_name="tmp",field_type="DATE",field_alias="tmp",
                                      field_is_nullable="NULLABLE")
            # Calculate field from !acquisitio! 
            dateBlock = """import datetime
from datetime import date, datetime, timedelta
def dateConvert(inString):
    aDate = datetime.strptime(inString, "%Y-%m-%d")
    return aDate"""
            arcpy.CalculateField_management(dissolve_meta,
                                            field="tmp",expression="dateConvert(!ACQ_DATE!)",
                                            expression_type="PYTHON_9.3",code_block=dateBlock)
            # Delete the "Acq_Date" field
            arcpy.DeleteField_management(dissolve_meta,"ACQ_DATE") 
            # Add field "Acq_Date" with proper formating
            arcpy.AddField_management(dissolve_meta,
                                      field_name="Acq_Date",field_type="DATE",field_alias="Acq_Date",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "Acq_Date" from "tmp"
            arcpy.CalculateField_management(dissolve_meta,"Acq_Date","!tmp!","PYTHON_9.3","#")
            # Delete "tmp" field
            arcpy.DeleteField_management(dissolve_meta,"tmp")
        
            # ---------------------------------------------------------------------------
            # Calculate and create AREA_KM2 field
            # ---------------------------------------------------------------------------
            # Delete "AREA_KM2" field 
            arcpy.DeleteField_management(dissolve_meta,"AREA_KM2")
            # Add field named "AREA_KM2" with proper formating
            arcpy.AddField_management(dissolve_meta,
                                      field_name="AREA_KM2",field_type="DOUBLE",field_precision=38,field_scale=8,field_alias="AREA_KM2",
                                      field_is_nullable="NULLABLE")
            # Calculate values for "AREA_KM2" from !tmp!
            arcpy.CalculateField_management(dissolve_meta,"AREA_KM2","!shape.area@squarekilometers!","PYTHON_9.3","#")
        
            # Project shapes to WGS84
            try:
                outCS = arcpy.SpatialReference('WGS 1984')
        
                #Run Project tool 
                arcpy.Project_management(dissolve_meta, proj_meta, outCS)
        
                # Append the new shapefile to the Metadata feature class on SDE
                arcpy.Append_management(proj_meta,Metadata,"NO_TEST","","")          
        
                #outputMessage(arcpy.GetMessages(0))
        
            except arcpy.ExecuteError:
                outputMessage(arcpy.GetMessages(2))
        
            except Exception as ex:
                outputMessage(ex.args[0])                
                
            #else:
                #outputError("\t###!! No local directory exists, Fix Product Name !!###")           
        
        def pullMDA(product):
            # Output location for ftp pull
            #
            dDir    = ScratchFolder + '\\MDA'
            # Variable for location of files on ftp site 
            #
            ftpPath = '/{0}/GIS_FILES/'.format(product) #product name
            # Define the ftp site
            #
            ftp     = ftplib.FTP("ftp2.digitalglobe.com") #The domain name of server ip
            # FTP login
            #
            outputMessage("\nLogging into FTP site...")
            #writeTo.write("Logging into FTP site...\n")
            ftp.login("xferplusmetro", "9yjMn1VQeZp3Sn") #The creds 
        
            # Change FTP file
            #
            try:
                outputMessage("Changing directory to {0}".format(ftpPath))
                #writeTo.write("Changing directory to {0}\n".format(ftpPath))
                ftp.cwd(ftpPath)
                files = ftp.nlst()     
        
                if any("MOSAIC" in name for name in files):
                    #outputMessage("{0} has mosaic product.".format(product))
                    #writeTo.write("{0} has mosaic product.\n".format(product))
                    # List of shapefile names for mosaic products
                    #
                    fileMatchMOS   = ['*CLOSEDPOLYGONS_SHAPE.shp', '*CLOSEDPOLYGONS_SHAPE.dbf', '*CLOSEDPOLYGONS_SHAPE.shx', '*CLOSEDPOLYGONS_SHAPE.prj']
        
                    for match in fileMatchMOS:
                        # Create a list of file names
                        #                
                        filename = ftp.nlst(match)
        
                        # Write the file output
                        for f in filename:
                            # Name the output file
                            local_filename = os.path.join(dDir, f)
        
                            #outputMessage("Opening local file " + local_filename)
        
                            # Open the output file for writing
                            file = open(local_filename, 'wb')
        
                            #outputMessage("Retrieving binary.")
        
                            # Retrive and write the output file
                            ftp.retrbinary('RETR '+ f, file.write)
                            file.close()  
                    ftp.quit()   
        
                    mosaicName = "{0}_P001_MOSAIC_CLOSEDPOLYGONS_SHAPE.shp".format(product)
        
                    for file in os.listdir(dDir):
                        if file.endswith(mosaicName):
                            global mosaic_filename
                            mosaic_filename = os.path.join(dDir, file)
                            #outputMessage(mosaic_filename)
                        else:
                            pass     
        
                    formatMDAmeta(mosaic_filename)
        
                elif any("MOSAIC" not in name for name in files):
                    #outputMessage("{0} has NO mosaic product.".format(product))
                    #writeTo.write("{0} has NO mosaic product.\n".format(product))
                    # List of shapefiles names for non-mosaic products
                    #
                    fileMatch = ['*PIXEL_SHAPE.shp', '*PIXEL_SHAPE.dbf', '*PIXEL_SHAPE.shx', '*PIXEL_SHAPE.prj',
                                 '*STRIP_SHAPE.shp', '*STRIP_SHAPE.dbf', '*STRIP_SHAPE.shx', '*STRIP_SHAPE.prj'] #shapefile and auxilary files
        
                    for match in fileMatch:
                        # Create a list of file names
                        #                
                        filename = ftp.nlst(match)
        
                        # Write the file output
                        for f in filename:
                            # Name the output file
                            local_filename = os.path.join(dDir, f)
        
                            #outputMessage()"Opening local file " + local_filename)
        
                            # Open the output file for writing
                            file = open(local_filename, 'wb')
        
                            #outputMessage("Retrieving binary.")
        
                            # Retrive and write the output file
                            ftp.retrbinary('RETR '+ f, file.write)
                            file.close()  
                    ftp.quit()   
        
                    pixelName = "{0}_P001_PIXEL_SHAPE.shp".format(product)
                    stripName = "{0}_STRIP_SHAPE.shp".format(product)
        
                    for file in os.listdir(dDir):
                        if file.endswith(pixelName):
                            global pixel_filename
                            pixel_filename = os.path.join(dDir, file)
                            #outputMessage(pixel_filename)
                        else:
                            pass
        
                    for file in os.listdir(dDir):
                        if file.endswith(stripName):
                            global strip_filename
                            strip_filename = os.path.join(dDir, file)
                            #outputMessage(strip_filename)
                        else:
                            pass
        
                    formatMDA(strip_filename,pixel_filename)
        
                else:
                    outputMessage("Error in pullMDA()...")
                    #writeTo.write("Error in pullMDA()...\n")
        
            except:
                #writeFile.write(product + "\n")
                outputError("\t###!! PRODUCT NAME DOES NOT EXIST ON FTP SITE !!###\n\t###!! FIX THE PRODUCT NAME: {0} !!###".format(product))
                #outputMessage("{0} not found in FTP directory!!".format(product))
                #writeTo.write("File does not exist in FTP directory.\n")
        
            #outputMessage(files)
        
        def pullHVA(product):
            dDir           = ScratchFolder + '\\HVA' 
            ftpPath        = '/{0}/'.format(product) #product name
            fileMatch      = ['*.shp', '*.dbf', '*.shx', '*.prj'] #shapefile and auxilary files
            ftp            = ftplib.FTP("ftp2.digitalglobe.com") #The domain name of server ip
        
            # FTP login
            #
            outputMessage("\nLogging into FTP site...")
            #writeTo.write("Logging into FTP site...\n")
            ftp.login("xferplusmetro", "9yjMn1VQeZp3Sn") #The creds 
        
            # Change FTP file
            #
            try:
                outputMessage("Changing directory to " + ftpPath)
                #writeTo.write("Changing directory to {0}\n".format(ftpPath))
                ftp.cwd(ftpPath)
                files = ftp.nlst()
        
                for match in fileMatch:
                    #outputMessage("File ending is: " + match)
                    filename = ftp.nlst(match)
            
                    # Write the file output
                    for item in filename:
                        # Name the output file
                        local_filename = os.path.join(dDir, item)
        
                        #outputMessage("Opening local file " + local_filename)
        
                        # Open the output file for writing
                        file = open(local_filename, 'wb')
        
                        #outputMessage("Retrieving binary.")
        
                        # Retrive and write the output file
                        ftp.retrbinary('RETR '+ item, file.write)
                        file.close()  
        
            except:
                outputError("\t###!! PRODUCT NAME DOES NOT EXIST ON FTP SITE !!###".format(product))
                #writeTo.write("{0} metadata file not found!!\n".format(product))
        
            ftp.quit()
        
            metaName = "{0}.shp".format(product)
            #outputMessage(metaName)
        
            for file in os.listdir(dDir):
                if file.endswith(metaName):
                    #global meta_filename
                    meta_filename = os.path.join(dDir, file)
                    #formatHVA(meta_filename)
                else:
                    pass   
            
            # Make sure the filename is defined before looking for it locally on scratch folder
            try:
                formatHVA(meta_filename)
            except NameError:
                outputError("\t###!! FIX THE PRODUCT NAME: {0} !!###".format(product))

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Start calling functions 
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        #Make the temprary directories for storing data
        dirHVA      = ScratchFolder + '\\HVA' 
        dirMDA      = ScratchFolder + '\\MDA' 
        dirProd     = ScratchFolder + '\\Products'
        
        #Delete directory if it exists and make a new one
        if os.path.exists(dirHVA):
            shutil.rmtree(dirHVA)
        os.makedirs(dirHVA)   
        
        if os.path.exists(dirMDA):
            shutil.rmtree(dirMDA)  
        os.makedirs(dirMDA)   
        
        if os.path.exists(dirProd):
            shutil.rmtree(dirProd)        
        os.makedirs(dirProd)   
        
        # Get product names from MDA and HVA metadata to compare with Completed Table.
        # Comparing lists finds metadata products that are missing and need to be 
        # downloaded via ftp pull.
        #
        metaList = [] #List of products that are already in current metadata dataset
        with arcpy.da.SearchCursor(Metadata, "Prod_Name") as cursor:
            outputMessage("Populating Metadata list...")
            #writeTo.write("Populating Metadata list...\n")    
            for row in cursor:
                metaName = str(row[0])
                metaList.append(metaName)
        outputMessage("Metadata list complete: {0}".format(len(metaList)))
        #writeTo.write("Metadata list complete: {0}\n".format(len(metaList)))
        
        cityNames   = [] #List of cities found in completed table
        cityTracker = [] #List for tracking duplicate city records in completed table
        outputMessage("Building city name index...")
        #Make an index list of all the city names found in the completed table
        for row in arcpy.da.SearchCursor(completeTable, ['City_Name']):
            if row[0] in cityTracker:
                pass
            elif row[0] not in cityTracker:
                cityNames.append(row[0])
                cityTracker.append(row[0])
            else:
                outputMessage("Error building city name index...")   
        outputMessage("City name index built...")
        
        compTable = [] #Table of all completed products and their attributes
        outputMessage("Building completed table index...")
        #Step Two: Make an index list of the Current Metadata table
        for row in arcpy.da.SearchCursor(completeTable, ['City_Name','Prod_Name','Prod_Run']):
            tmpLst = []
            tmpLst.append(row[0])
            tmpLst.append(row[1])
            tmpLst.append(row[2])
        
            compTable.append(tmpLst)
        
        outputMessage("Completed table index built...")
        #outputMessage(compTable)
        
        current_list = []
        outputMessage("Calculate highest production run...")
        # Make a list of the most current product runs
        for i in cityNames:
            new_list = [compTable[x][2] for x in range(len(compTable)) if compTable[x][0] == i]
        
            lastRun = max(new_list)
        
            product_list = [compTable[y][1] for y in range(len(compTable)) if compTable[y][0] == i and compTable[y][2] == lastRun]
        
            current_list.append(product_list)    
        
        outputMessage("Highest production run calculated...")
        
        ftpList = [] #List of product names that need to be downloaded from ftp site
        countMissing = 0
        #Find missing metadata records and write them to text
        for product in current_list:
            if product[0] in metaList:
                pass
            elif product[0] not in metaList:
                outputMessage("New Product: {0}".format(product[0]))
                #writeTo.write("{0}\n".format(product[0]))
                ftpList.append(str(product[0]))
                countMissing += 1
            else:
                outputMessage("Error.")
                #writeTo.write("Error.")
        
        outputMessage("New Products = {0}".format(countMissing))
        #writeTo.write("New Products = {0}\n".format(countMissing))
        
        if countMissing == 0:
            outputMessage("No new products found.")
            #writeTo.write("No new products found.\n")
        elif countMissing > 0:
            for product in ftpList:
                # If there are letters in the name follow the MDA file heirarchy
                #
                if re.search('[a-zA-Z]', product) == None:
                    #outputMessage("{0} is a MDA order.".format(product))
                    pullMDA(product)
                    #pass
                # If there are no letters in the name follow the MDA file heirarchy
                #        
                elif re.search('[a-zA-Z]', product) != None:
                    #outputMessage("{0} is a HVA order.".format(product))
                    pullHVA(product)         
                    #pass
                else:
                    outputMessage("{0} product failed...".format(product))
                    #writeTo.write("{0} product failed...\n".format(product))
        else:
            outputMessage("Error.")
            #writeTo.write("Error.\n")

class qaqcCheck(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1. Production Table QA/QC"
        self.description = "Validate that data attribution is correct before loading to Completed Table."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        param0 = arcpy.Parameter(
            displayName="Database Connection to Metro 2.0 Production Table",
            name="Input Production Table",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")     
        
        params = [param0]
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
        
        def outputMessage(msg):
            print(msg)
            arcpy.AddMessage(msg)
        
        def outputError(msg):
            print(msg)
            arcpy.AddError(msg)
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define variables and environments
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  
        
        # Set the overwriteOutput ON
        arcpy.gp.overwriteOutput = True
        
        # Set the workspace
        arcpy.env.workspace = "in_memory"
        ScratchGDB = arcpy.env.scratchGDB
        
        outputMessage("Scratch folder is: {}".format(ScratchGDB))
        
        #Input data
        prodTable = parameters[0].valueAsText  #Input database connection to production table
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define Functions: Hail Satan 666
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        # Check the catIds to make sure no QB or WV01 imagery used
        def isMetroCatId(inCatIDs):
            catId = inCatIDs.split(',')
            for i in catId:
                if i[:3] == '101':
                    return False
                elif i[:3] == '102':
                    return False
                else:
                    pass
        
        # Check to see if Category field is set right for 30cm_Com products
        def is30cm(inCategory,inCatIDs):
            if inCategory == '30cm_Com':
                catId = inCatIDs.split(',')
                for i in catId:
                    if i[:3] == '101' or i[:3] == '102' or i[:3] == '103' or i[:3] == '105':
                        return False
                    else:
                        return True
            else:
                pass
        
        # Check to see if GSD field is set right for 30cm products
        def is30gsd(inGSD,inCatIDs):
            if inGSD == '0.3':
                catId = inCatIDs.split(',')
                for i in catId:
                    if i[:3] == '101' or i[:3] == '102' or i[:3] == '103' or i[:3] == '105':
                        return False
                    else:
                        return True
            else:
                pass
        
        # Check to make sure the catId field matches what is documented in the sensor field
        def sensorMatch(inCatIDs,cityName):
            sensorLst = []
            catId = inCatIDs.split(',')
            for i in catId:
                if i[:3] == '101':
                    sensorLst.append('QB')
                elif i[:3] == '102':
                    sensorLst.append('WV01')
                elif i[:3] == '103':
                    sensorLst.append('WV02')
                elif i[:3] == '104':
                    sensorLst.append('WV03')
                elif i[:3] == '105':
                    sensorLst.append('GE01')
                else:
                    pass
            #outputMessage(len(sensorLst))
            #outputMessage(sensorLst)
            
            # is GE01 only:
            if 'GE01' in sensorLst and 'WV02' not in sensorLst and 'WV03' not in sensorLst:
                outputMessage('GE01')
                return('GE01')
            # is GE01 combined:
            elif 'GE01' in sensorLst and 'WV02' in sensorLst or 'WV03' in sensorLst:
                outputMessage('COMBO_GEO')
                return('COMBO_GEO')
            # is combined sensors with out GE01
            elif 'GE01' not in sensorLst and 'WV02' in sensorLst and 'WV03' in sensorLst:
                outputMessage('COMBO_noGEO')
                return('COMBO_noGEO')            
            # is WV02 only
            elif 'WV02' in sensorLst and 'WV03' not in sensorLst and 'GE01' not in sensorLst:
                outputMessage('WV02')
                return('WV02')              
            # is WV03 only
            elif 'WV03' in sensorLst and 'WV02' not in sensorLst and 'GE01' not in sensorLst:
                outputMessage('WV03')
                return('WV03')
            else:
                pass
        
        # Check the newest image date for 30cm products is less than 365 days old 
        def isNewImg(cat,imgDate,pState):
            
            #Get today's date
            today = datetime.now()
            
            # Get 30cm Commited AOIs with ordered, fulfilled and Dem status with a complete image date
            if (cat == '30cm_Com') and (pState == 'Ordered' or pState == 'Fulfilled' or pState == 'DEMs') and (imgDate is not None):
                
                # Get image age in days
                age     = abs(today-imgDate)
                ageDays = age.days 
                
                if ageDays > 365:
                    return False
                else:
                    return True
                
            else:
                pass
        
        # Check the Newest Image date of product is within 365 days of the production date
        def isProdDate(cat,imgDate,prodDate):
            if (imgDate is None) or (prodDate is None):
                pass
            elif (cat == '30cm_Com'):
            
                age     = abs(prodDate-imgDate)
                ageDays = age.days
                
                if ageDays > 365:
                    return False
                else:
                    return True
            else:
                pass
            
        # Check the Production name is not empty or has illegal characters
        def isNotBlankorChar(pStatus,cName,pName):
            if (pStatus == 'Completed') and (pName == ''): #No Blanks
                return False
            elif (pStatus == 'Completed') and ('\n' in pName): #No New Lines
                return False
            elif (pStatus == 'Completed'):
                if re.match("^[a-zA-Z0-9_]*$", pName): #No Special Characters
                    pass
                else:
                    return False
            else:
                pass                
            
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Commence running this Dope-as-Fuck python code
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##        
        
        prodLst   = []
        cityQuery = []
        
        #Step One: Build a nested list of values from the production table
        outputMessage("Building production list...")
        for row in arcpy.da.SearchCursor(prodTable, ['City_Name','ProdCatIDs','Prod_State',
                                                     'CatID_Cnt','GSD','Category','Sensor',
                                                     'NewestDate','Prod_Date','Prod_Name']):
            tmpLst = []
            tmpLst.append(row[0]) #CityName
            tmpLst.append(row[1]) #ProdCatIDs
            tmpLst.append(row[2]) #ProdState
            tmpLst.append(row[3]) #CatIDCount
            tmpLst.append(row[4]) #GSD
            tmpLst.append(row[5]) #Category
            tmpLst.append(row[6]) #Sensor
            tmpLst.append(row[7]) #NewestDate
            tmpLst.append(row[8]) #ProdDate
            tmpLst.append(row[9]) #ProdName
            prodLst.append(tmpLst)
            
        outputMessage("Production list built...")
        #outputMessage(prodLst)
        
        indexNum = list(range(len(prodLst)))
        # Loop through nested list and find any products that do not
        # fit the product spec
        for x in indexNum:
            cityName  = prodLst[x][0]
            catIds    = prodLst[x][1]
            prodState = prodLst[x][2]
            catIdCnt  = prodLst[x][3]
            gsd       = prodLst[x][4]
            category  = prodLst[x][5]
            sensor    = prodLst[x][6]
            newImg    = prodLst[x][7]
            prodate   = prodLst[x][8]
            prodName  = prodLst[x][9]
            
            #  Check the Category field is correct for 30cm_Com: No qb, wv01, wv02, ge01
            if is30cm(category, catIds) == False:
                outputError("\t### Check Category Field for {0}, Category can not be 30cm Commited.".format(cityName))
                cityQuery.append(str(cityName))
            else:
                pass
            
            # Check the GSD field is correct: No qb, wv01, wv02, ge01
            if is30gsd(gsd,catIds) == False:
                outputError("\t### Check GSD Field for {0}, GSD can not be 30cm.".format(cityName))
                cityQuery.append(str(cityName))
            else:
                pass
            
            # Check that no GeoEye or WV01 ids were pasted in table on accident... cause you know people make mistakes 
            if isMetroCatId(catIds) == False:
                outputError("\t### Check CatId Field for {0}, no QB or WV01 imagery allowed.".format(cityName))
                cityQuery.append(str(cityName))
            else:
                pass                
                
            #sensorMatch(catIds,cityName)
            
            # Check that newest image in select products is newer than 365 days
            if isNewImg(category,newImg,prodState) == False:
                outputError("\t### Check Newest Image Date Field for {0}, Newest Image is more than 365 days old from today.".format(cityName))
                cityQuery.append(str(cityName))
            else:
                pass      
            
            # Check that newest image in select products is within 365 days of the production date
            if isProdDate(category,newImg,prodate) == False:
                outputError("\t### Check Newest Image Date and Production Date for {0}, Newest Image not within 365 days of Production Date.".format(cityName))
                cityQuery.append(str(cityName))
            else:
                pass     
            
            # Check that product names are correct
            if isNotBlankorChar(prodState,cityName,prodName) == False:
                outputError("\t### Check Product Name for {0}, Product Name is INVALID.".format(cityName))
                cityQuery.append(str(cityName))
            else:
                pass            
            
        #Query builder: Create a query that can be copied and pasted into the definition query like so -
        #City_Name IN ('Danghara','Aabenraa')
        tCity = tuple(cityQuery)
        outputMessage("\nCity_Name IN {0}\n".format(tCity))
