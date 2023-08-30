import arcpy
from arcpy import env
import sys
import os
import string
import tempfile
import errno
import shutil
import datetime
from collections import Counter

#Import excel write tools
import xlwt
ezxf = xlwt.easyxf

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Reporting Tool"
        self.alias = "Reporting Tool"

        # List of tool classes associated with this toolbox
        self.tools = [Report_A,Report_B]
        
class Report_A(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Report A"
        self.description = "Report A"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        param0 = arcpy.Parameter(
            displayName="Database Connection to Current Metadata",
            name="Input Current Metadata",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Database Connection to Completed Metros Table",
            name="Input Completed Metros Table",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")              
        
        param2 = arcpy.Parameter(
            displayName="Output Excel File",
            name="Name Output Excel File",
            datatype="File",
            parameterType="Required",
            direction="Output")
        
        param3 = arcpy.Parameter(
            displayName="Orbit Environment",
            name="Orbit Environment",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")         
        
        params = [param0,param1,param2,param3]
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
        
        #outputMessage("Running: {0}".format(sys.argv[0]))
        
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
        
        inMetadata       = parameters[0].valueAsText #Input current metadata shp
        inCurrentTbl     = parameters[1].valueAsText #Input completed table
        fileLocation     = parameters[2].valueAsText #Output file location and name
        excelOutput      = fileLocation + ".xls"
        isOrbit          = parameters[3].valueAsText
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define functions
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        #List comprehension to find product names of the most recent product run:
        def findCurrentProducts(cityName,inTable,outTable):
            #New list contains the production runs
            new_list = [inTable[x][4] for x in range(len(inTable)) if inTable[x][0] == cityName]
            
            #Find the last run number for each city
            lastRun = max(new_list)
            
            product_list = [inTable[y][2] for y in range(len(inTable)) if inTable[y][0] == cityName and inTable[y][4] == lastRun]
            
            outTable.append(product_list)
        
        #Find the area percentage of images that are under 1 year old in a product
        def percent12Mos(pDate,inLst):
            
            # Get the product date from input list
            prodDate = pDate[0]
            #outputMessage("Production date is: {0}".format(prodDate))
            
            # Create new list for storing just Acqdate,AreaKM2 - key,value pairs
            nestLst = []
                 
            #Dictionary for storing the acquired date and the total area
            dateDic = {}        
            
            # Build a dictionary with the Acq image date and the area of the strip
            for x in range(len(inLst)):
                eggLst = []
                eggLst.append(inLst[x][0]) #AcqDate
                eggLst.append(inLst[x][1]) #AreaKM2
                nestLst.append(eggLst)
                
                #outputMessage("Acq Date is: {0}".format(inLst[x][0]))
                #outputMessage("Area is: {0}".format(inLst[x][1]))
            
            # Sum the area based on date and write to dictionary
            for date,area in nestLst:
                total = dateDic.get(date,0) + area
                dateDic[date] = total      
            #outputMessage(dateDic)
        
            #Show me what is in the dictionary to see if it is accurate
            #outputMessage("Dictionary is: {0}".format(dateDic))
            
            #Find the total area km2 of the product     
            sumVal = sum(dateDic.values())
            
            #Check the total area km2 is correct
            #outputMessage("Total Area KM2 is: {0}".format(sumVal))
            
            #Variable for storing total area of images less than 365 days in age
            sumArea = 0
                
            #Loop through the date acq & date keys
            for key in dateDic:

                # Get image age in days
                age     = abs(prodDate-key)
                ageDays = age.days
                #outputMessage("Age is: {0}".format(ageDays))
                   
                if ageDays <= 365:
                    #outputMessage("Age Less than 365 :)") 
                    
                    # Get the image area for the image if it is newer than 365 days
                    areaValue = dateDic.get(key)                        
                    #outputMessage(areaValue)
                    
                    # Add the area of the selected image to the running total
                    sumArea = sumArea + areaValue
                    #outputMessage("Sum area = {}".format(sumArea))
                    
                else:
                    pass                   
                            
            # Calculate the percentage of coverage
            coverage = (float(sumArea)/sumVal)*100
            #outputMessage("Coverage percent = {}".format(coverage))
            
            #outputMessage("% Cover is: {0}".format(coverage))
            return coverage

        #Find the area percentage of images that are under 2 years old in a product
        def percent24Mos(pDate,inLst):
            
            # Get the product name from input list
            prodDate = pDate[0]
            #outputMessage("Production date is: {0}".format(prodDate))
            
            # Create new list for storing just Acqdate,AreaKM2 - key,value pairs
            nestLst = []
                 
            #Dictionary for storing the acquired date and the total area
            dateDic = {}
            
            # Build a dictionary with the Acq image date and the area of the strip
            for x in range(len(inLst)):
                eggLst = []
                eggLst.append(inLst[x][0]) #AcqDate
                eggLst.append(inLst[x][1]) #AreaKM2
                nestLst.append(eggLst)
                
                #outputMessage("Acq Date is: {0}".format(inLst[x][0]))
                #outputMessage("Area is: {0}".format(inLst[x][1]))
            
            # Sum the area based on date and write to dictionary
            for date,area in nestLst:
                total = dateDic.get(date,0) + area
                dateDic[date] = total      
            #outputMessage(dateDic)             
    
            #Show me what is in the dictionary to see if it is accurate
            #outputMessage("Dictionary is: {0}".format(dateDic))
            
            #Find the total area km2 of the product     
            sumVal = sum(dateDic.values())
            
            #Check the total area km2 is correct
            #outputMessage("Total Area KM2 is: {0}".format(sumVal))
            
            #Variable for storing total area of images less than 365 days in age
            sumArea = 0
                
            #Loop through the date acq & date keys
            for key in dateDic:

                # Get image age in days
                age     = abs(prodDate-key)
                ageDays = age.days
                #outputMessage("Age is: {0}".format(ageDays))
                   
                if ageDays > 365:
                    #outputMessage("Age is greater than 365 :)") 
                    
                    # Get the image area for the image if it is newer than 365 days
                    areaValue = dateDic.get(key)                        
                    #outputMessage("Total Area older than 365 days: {0}".format(areaValue))
                    
                    # Add the area of the selected image to the running total
                    sumArea = sumArea + areaValue
                    #outputMessage("Sum area = {0}".format(sumArea))
                    
                else:
                    pass                   
                            
            # Calculate the percentage of coverage
            coverage = (float(sumArea)/sumVal)*100
            #outputMessage("Coverage percent = {0}".format(coverage))
            
            #outputMessage("% Cover is: {0}".format(coverage))
            return coverage
         
        #Function to find the accuracy for a product
        def accuracy(inLst):
            #List for storing accuracy values
            accuLst = []
                
            # Populate the min ssun el list with values from shapefile
            for x in range(len(inLst)):
                accuLst.append(inLst[x][2])            
            
            if len(accuLst)==0:
                outputError("#########################################\n"
                         "# Metadata Feature Class NOT CURRENT!!! #\n"
                         "#      DOWNLOAD MISSING METADATA        #\n"
                         "#########################################")
                sys.exit()
            elif len(accuLst)>0:
                accuracy = max(accuLst)
                return accuracy                 
            else:
                outputMessage("!!!Error in accuracy() function!!!")        
                
        # Function to find the Max ONA for a product
        def maxONA(inLst):
            #List for storing ONA values
            onaLst = []
            
            # Find Max ONA from list
            for x in range(len(inLst)):
                onaLst.append(inLst[x][3])
            
            maxONA = max(onaLst)
            
            return maxONA
            
        #Function to find the Min Sun El for a product
        def minSunEl(inLst):
            #List for storing min sun el values
            sunElLst = []
            
            # Populate the min sun el list with values from shapefile
            for x in range(len(inLst)):
                sunElLst.append(inLst[x][4])            
                
            sunEl = min(sunElLst)     
            
            return sunEl
        
        #Function to create a list of acquisition date and area for every metadata product 
        def metaList(metadata, outLst):
            for x in range(len(metadata)):
                yLst = []
                if metaTable[x][0] == name:
                    yLst.append(metaTable[x][1]) #Acq Date
                    yLst.append(metaTable[x][2]) #Area KM2
                    yLst.append(metaTable[x][3]) #Accuracy 
                    yLst.append(metaTable[x][4]) #ONA
                    yLst.append(metaTable[x][5]) #SunEl
                    outLst.append(yLst)    

        # Write master list into a excel sheet
        #
        def write_xls(file_name, book, sheet_name, headings, data, heading_xf, data_xfs):
            sheet = book.add_sheet(sheet_name)
            rowx = 0
            
            # Write and format the headings for the sheet
            for colx, value in enumerate(headings):
                sheet.write(rowx, colx, value, heading_xf)
            sheet.set_panes_frozen(True) # frozen headings instead of split panes
            sheet.set_horz_split_pos(rowx+1) # in general, freeze after last heading row
            sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there
            
            # Write and format the body/data for the sheet
            for row in data:
                # The row number is defined for the cell, and a new row is added on each time
                rowx += 1
                # The column number is defined for each cell, and the value to be writen is pulled
                # out using the enumerate list function.        
                for colx, value in enumerate(row):
                    # A new sheet is writen with the cell row number identified,
                    # the cell column number identified, the value that will 
                    # be written to the cell defined AND... Magically the 
                    # cell formating is defined with the 'data_xfs[colx]'. This
                    # is really important, but I don't know how it works.            
                    sheet.write(rowx, colx, value, data_xfs[colx])
            book.save(file_name)           
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Start calling functions 
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        
        #=====================================#
        # Inputs for excel conversion function
        #=====================================#
        # Create a new workbook to write both Archive and Current sheets to
        wb = xlwt.Workbook()
        # List of excel header titles
        hdngs = ['City','Country','Directory Name','FTP_Folder','GSD','Production Version',
                 'Same as +Vivid HVA', 'Oldest Date of Imagery', 'Newest Date of Imagery', 'KM2',
                 'Date Delivered','FTP Roll-Off','<12 Months','<24 Months','Refresh Image Age (12/24 Mos)',
                 'Accuracy','Avg. Cloud Cover','Max ONA','Min Sun El','Commited or Variable']
        # The different format types/'kinds' for each column !!!ORDER MATTERS!!! ORDER IS
        # SUPER FUCKING IMPORTANT, BUT I DON"T KNOW WHY"
        kinds =  'text text text text int0 int1 text date date int1 date date int2 int2 int1 int2 int2 int2 int2 text'.split()
        # The formating for the header using xlwt.easyxf
        heading_xf = ezxf('font: bold on; align: vert centre, horiz center')
        # Dictionaty for storing/defining format values. Uses xlwt.easyxf
        kind_to_xf_map = {
            'date': ezxf(num_format_str='m/d/yyyy'),
            'int0': ezxf(num_format_str='0.0'),
            'int1' : ezxf(num_format_str='0'),
            'int2' : ezxf(num_format_str='0.00'),
            'text': ezxf(),
        }
        # Dictionary is referenced with 'kind_to_xf_map[k]', which is all
        # the key values in the dictionary. The dictionary is linked to the 
        # different values in 'kinds'. This is really important, but I don't know
        # how it works.
        data_xfs = [kind_to_xf_map[k] for k in kinds]
        #=====================================#        
        
        cityTracker  = [] #List for tracking cities that have already been analyzed
        cityNames    = [] #List of city names
        compTable    = [] #List for storing the completed table
        productNames = [] #List of the most current products found in Completed Table
        metaTable    = [] #List of metadata attributes: Production name and acqdate
        reportLst    = [] #List for excel report
        cityDic      = {} #Dictionary for storing the city name and most recent run product name   
        
        #Step One: Make an index list of all the City Names to select from the metadata table
        outputMessage("Building city name index...")
        for row in arcpy.da.SearchCursor(inCurrentTbl, ['City_Name']):
            if row[0] in cityTracker:
                pass
            elif row[0] not in cityTracker:
                cityNames.append(row[0])
                cityTracker.append(row[0])
            else:
                outputMessage("Error building city name index...")   
        outputMessage("City name index built...")
        
        #Step Two: Make an index list of the Current Metadata table
        outputMessage("Building completed table index...")
        for row in arcpy.da.SearchCursor(inCurrentTbl, ['City_Name','Country','Prod_Name','GSD','Prod_Run',
                                                        'OldestDate','NewestDate','Area_sqkm','Prod_Date','Category','Avg_CC']):
            tmpLst = []
            tmpLst.append(row[0])
            tmpLst.append(row[1])
            tmpLst.append(row[2])
            tmpLst.append(row[3])
            tmpLst.append(row[4])
            tmpLst.append(row[5])
            tmpLst.append(row[6])
            tmpLst.append(row[7])
            tmpLst.append(row[8])
            tmpLst.append(row[9])
            tmpLst.append(row[10])
        
            compTable.append(tmpLst)
        
        outputMessage("Completed table index built...")
        #outputMessage(compTable)
        
        outputMessage("Building current product index...")
        #Step Three: Make a list of the product names that are them most current product run for an AOI
        for i in cityNames:
            findCurrentProducts(i,compTable,productNames)
        outputMessage("Current product index built...")
        #outputMessage(productNames)  
        
        #Step Four: Build a list of all metadata attributes
        outputMessage("Building metadata product index...")      
        for row in arcpy.da.SearchCursor(inMetadata, ['Prod_Name','Acq_Date','AREA_KM2',
                                                      'ACCURACY','ONA','SUNEL']):
            tmpLst = []
            tmpLst.append(row[0]) #Prod Name
            tmpLst.append(row[1]) #Acq Date
            tmpLst.append(row[2]) #Area
            tmpLst.append(row[3]) #Accuracy
            tmpLst.append(row[4]) #ONA
            tmpLst.append(row[5]) #Sun El
        
            metaTable.append(tmpLst)
        
        outputMessage("Metadata product index built...")
        #outputMessage(metaTable)        
        
        #Step Five: Calculate the fields for the report
        outputMessage("Calculating report fields...")
        for product in productNames:
            name = product[0]
            #outputMessage("Processing product: {0}".format(name))
            
            #Get city name, country, gsd, prodRun, oldest date, newest date, areakm2,
            # production date, category, and average cloud cover from the completed table for the product
            city    = [compTable[x][0] for x in range(len(compTable)) if compTable[x][2] == name]  
            country = [compTable[x][1] for x in range(len(compTable)) if compTable[x][2] == name]
            gsd     = [compTable[x][3] for x in range(len(compTable)) if compTable[x][2] == name] 
            prodRun = [compTable[x][4] for x in range(len(compTable)) if compTable[x][2] == name] 
            oldest  = [compTable[x][5] for x in range(len(compTable)) if compTable[x][2] == name] 
            newest  = [compTable[x][6] for x in range(len(compTable)) if compTable[x][2] == name] 
            areaKM  = [compTable[x][7] for x in range(len(compTable)) if compTable[x][2] == name] 
            prodDate= [compTable[x][8] for x in range(len(compTable)) if compTable[x][2] == name]
            cat     = [compTable[x][9] for x in range(len(compTable)) if compTable[x][2] == name]
            avgCC   = [compTable[x][10] for x in range(len(compTable)) if compTable[x][2] == name]
            
            # Make a nested list of the acq date & area for each metadata product
            xLst = []
            metaList(metaTable, xLst)
            #outputMessage("xLst: {0}".format(xLst))
            
            # Assign the percentages to a variable for the 12 and 24 month results
            twelveMonths = percent12Mos(prodDate,xLst) #<12 mon
            twentyMonths = percent24Mos(prodDate,xLst) #<24 mon
            
            # Append values to nested list for excel
            nestLst = []
            nestLst.append(city[0])
            nestLst.append(country[0])
            nestLst.append(name)
            nestLst.append("/plusMetro")
            nestLst.append(gsd[0])
            nestLst.append(prodRun[0])
            nestLst.append("TBD")
            nestLst.append(oldest[0])
            nestLst.append(newest[0])
            nestLst.append(areaKM[0])
            nestLst.append(prodDate[0])
            nestLst.append("NA")
            
            #Find the age of product from the production date
            if prodDate[0] is None:
                pass
            else:
                today = datetime.datetime.today()
                pAge = abs(today-prodDate[0])
                ageDays = pAge.days
            
            #Populate 12 month field
            if prodDate[0] is None:
                nestLst.append('Missing Data')
            else:
                nestLst.append(twelveMonths) #<12 mon
                #outputMessage("12 Month % = {0}".format(twelveMonths))
            
            #Populate 24 month field
            if prodDate[0] is None:
                nestLst.append('Missing Data')
            else:
                nestLst.append(twentyMonths) #<24 mon
                #outputMessage("24 Month % = {0}".format(twentyMonths))
            
            #Populate 12/24 month bin field using % area in 12mon/24mon fields and 
            #age of product based on production date's age
            if prodDate[0] is None:
                nestLst.append('Missing Data')
            elif twelveMonths > 75 and ageDays <= 365:
                nestLst.append('12') #12/24 mon aoi
            elif twelveMonths <= 75 and ageDays <= 730:
                nestLst.append('24') #12/24 mon aoi
            elif twelveMonths <= 75 and ageDays > 730:
                nestLst.append('>24') #12/24 mon aoi            
            else:
                nestLst.append('0') #12/24 mon aoi
                
            #If the metadata is not up-to-date, then the tool will error out at this line. I
            #wrote in logic for the function to send a message to the user for them to 
            #update the metadata.
            #
            nestLst.append(accuracy(xLst))
            nestLst.append(avgCC[0])
            nestLst.append(maxONA(xLst))
            nestLst.append(minSunEl(xLst))
            nestLst.append(cat[0])
            reportLst.append(nestLst)
            
        outputMessage("Calculating report fields complete...")

        outputMessage("Writing to excel...")
        write_xls(excelOutput, wb, '+Metro 2.0', hdngs, reportLst, heading_xf, data_xfs)
        outputMessage("Write to excel complete...")
    
        outputMessage("Task complete!")

class Report_B(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Report B"
        self.description = "Report B"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        param0 = arcpy.Parameter(
            displayName="Database Connection to Metro AOIs",
            name="Input AOI Feature Class",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
            displayName="Database Connection to Completed Table",
            name="Input Completed Table",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")        
        
        param2 = arcpy.Parameter(
            displayName="Database Connection to Production Table",
            name="Input Production Table",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")
        
        param3 = arcpy.Parameter(
            displayName="Database Connection to Current Metadata",
            name="Input Current Metadata",
            datatype="Dataset",
            parameterType="Required",
            direction="Input")        
        
        param4 = arcpy.Parameter(
            displayName="Output File",
            name="Name Output File",
            datatype="File",
            parameterType="Required",
            direction="Output")
        
        param5 = arcpy.Parameter(
            displayName="Orbit Environment",
            name="Orbit Environment",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")         
        
        params = [param0,param1,param2,param3,param4,param5]
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
        
        #outputMessage("Running: " + sys.argv[0])
        
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

        inAOIs           = parameters[0].valueAsText # Input metro AOI shapefiles
        inCurrentTbl     = parameters[1].valueAsText # Input completed table
        inProdTbl        = parameters[2].valueAsText # Input production table
        inMetadata       = parameters[3].valueAsText # Input metadata completed shapefile
        fileLocation     = parameters[4].valueAsText # Output file location and name for csv and xls
        isOrbit          = parameters[5].valueAsText
        excelOutput      = fileLocation + ".xls"
        
        # Regions KEY #
        '''
        AM -- AMERICAS
        EA -- EAST ASIA
        EU -- EUROPE / W AFRICA
        ME -- MIDDLE EAST / E AFRICA
        SP -- SOUTH PACIFIC
        WA -- WEST ASIA
        '''

        # Make a date marker for selecting shit that is only one year old
        global oneYRago
        oneYRago = datetime.datetime.now() - datetime.timedelta(days=365)
        
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
        #================================#
        # Define functions
        #================================# 
        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
        '''
        Function to create a list of AOIs city names by region
        
        Inputs:
        aois -- The inAOIs shapefile
        region -- The desired region for making an attribute query
        
        Outputs:
        aoiRegion -- An output list of all the aois and attributes for a selected region
        
        '''
        def createAOIList(aois,region):
           
            #Name the output list
            aoiRegion = []
            
            for row in arcpy.da.SearchCursor(aois, ['City_Name','Area_sqkm','Region','Start_Task','Uniq_ID']):
                
                if row[2] == region:
                    tmpLst = []
                    tmpLst.append(row[0]) #City_Name
                    tmpLst.append(row[1]) #Area_sqkm
                    tmpLst.append(row[2]) #Region
                    tmpLst.append(row[3]) #Start_Task
                    tmpLst.append(row[4]) #Uniq_ID
                    
                    #Append tmpLst to the region list            
                    aoiRegion.append(tmpLst)
                    
                else:
                    pass
            
            return aoiRegion
        
        '''
        Function to create a production table list for each region
        
        Inputs:
        prodTable -- The production table input inProdTbl
        region -- The desired region for making an attribute query
        
        Outputs:
        prodRegion -- An output list of production table attributes for a selected region
        
        '''        
        def createProdList(prodTable,region):          
            
            #Name the output list
            prodRegion = []

            for row in arcpy.da.SearchCursor(prodTable, ['City_Name','Prod_Name','OldestDate','NewestDate','Prod_Date',
                                                         'Last_Comp','Prod_Run','Area_sqkm','Task_Month','Region','Prod_State',
                                                         'Uniq_ID','Category','GSD']):
                if row[9] == region:
                    tmpLst = []
                    tmpLst.append(row[0]) #City_Name
                    tmpLst.append(row[1]) #Prod_Name
                    tmpLst.append(row[2]) #OldestDate
                    tmpLst.append(row[3]) #NewestDate
                    tmpLst.append(row[4]) #prod_Date
                    tmpLst.append(row[5]) #Last_Comp
                    tmpLst.append(row[6]) #Prod_Run
                    tmpLst.append(row[7]) #Area_sqkm
                    tmpLst.append(row[8]) #Task_Month
                    tmpLst.append(row[9]) #Region
                    tmpLst.append(row[10]) #Prod_State
                    tmpLst.append(row[11]) #Uniq_ID
                    tmpLst.append(row[12]) #Category
                    tmpLst.append(row[13]) #GSD
                    
                    #Append tmpLst to the region production list            
                    prodRegion.append(tmpLst)
                
                else:
                    pass

            return prodRegion    
        
        '''
        Function to create a completed table list for each region
        
        Inputs:
        compTable -- The completed table input 
        region -- The desired region for making an attribute query
        
        Outputs:
        compRegion -- An output list of completed table attributes for a selected region
        
        '''              
        def createCompList(compTable,region):
            #Name the output list
            compRegion = []
        
            for row in arcpy.da.SearchCursor(compTable, ['City_Name','Prod_Name','OldestDate','NewestDate','Prod_Date',
                                                         'Last_Comp','Prod_Run','Area_sqkm','Task_Month','Region','Prod_State',
                                                         'Uniq_ID','Category','GSD']):
                
                if row[9] == region:
                    tmpLst = []
                    tmpLst.append(row[0]) #City_Name
                    tmpLst.append(row[1]) #Prod_Name
                    tmpLst.append(row[2]) #OldestDate
                    tmpLst.append(row[3]) #NewestDate
                    tmpLst.append(row[4]) #prod_Date
                    tmpLst.append(row[5]) #Last_Comp
                    tmpLst.append(row[6]) #Prod_Run
                    tmpLst.append(row[7]) #Area_sqkm
                    tmpLst.append(row[8]) #Task_Month
                    tmpLst.append(row[9]) #Region
                    tmpLst.append(row[10]) #Prod_State
                    tmpLst.append(row[11]) #Uniq_ID
                    tmpLst.append(row[12]) #Category
                    tmpLst.append(row[13]) #GSD
        
                    #Append tmpLst to the region production list            
                    compRegion.append(tmpLst)
        
                else:
                    pass
        
            return compRegion
        
        '''
        Function to create a metadata list for all metadata products found
        in the current metadata feature class
        
        Inputs:
        inMeta -- The whole metadata feature class as an input 
        
        Outputs:
        MetaLst -- An output list of the metadata feature class
        
        '''              
        def createMetaList(inMeta):
            #Name the output list
            MetaLst = []
            
            for row in arcpy.da.SearchCursor(inMeta, ['Prod_Name','Acq_Date','AREA_KM2']):
                tmpLst = []
                #tmpLst.append(row[0]) #City Name
                tmpLst.append(row[0]) #Prod Name
                tmpLst.append(row[1]) #Acq Date
                tmpLst.append(row[2]) #Area
            
                MetaLst.append(tmpLst)            
        
            return MetaLst       
        
        '''
        Function to create a  list of product names from the completed table that
        are the highest production run for their metro AOI. 
        
        Inputs: 
        inLst -- Input is a region's completed table as a list
        
        Outputs:
        newestProd -- Output is a list of completed products that are the most recent
                      production run for a city.
        '''        
        def currentProducts(inLst):
            newestProd = []
            
            for x in inLst:
                cityName = x[0]
                #outputMessage(cityName)
                
                #New list contains the production runs
                new_list = [inLst[x][6] for x in range(len(inLst)) if inLst[x][0] == cityName]
                #outputMessage(new_list)
            
                #Find the last run number for each city
                lastRun = max(new_list)
                
                #Find the product name for the most recent product 
                product_list = [inLst[y][1] for y in range(len(inLst)) if inLst[y][0] == cityName and inLst[y][6] == lastRun]
                #outputMessage(product_list)
                
                newestProd.append(product_list[0])
            
            return newestProd
        
        '''
        Function to count the number of AOIs for a given tasking date.
        
        Inputs: 
        inLst -- A region list of all AOIs
        inMonth -- The desired tasking month
        
        Outputs:
        aoiCount -- The count of AOIs in the tasking month and in the region
        '''
        def numAOIs(inLst,inMonth):
            aoiCount = 0
            for x in inLst:
                if x[3] == inMonth:
                    aoiCount += 1
                else:
                    pass
            return aoiCount
        
        '''
        Function to count the number of records that with "Completed" status
        within the last year (365 days) divided up by tasking month.
        
        Inputs:
        inTbl -- The metro production table as a list
        inMonth -- The desired month number for an attribure query
        
        Output:
        Record Count -- The count of selected records 
        '''
        def numComplete(inLst,inMonth):
            cntLst = []
            for x in inLst:
                #outputMessage("{0},{1},{2}".format(x[8],x[10],x[4]))
                if x[4] == None:
                    pass
                elif x[8] == inMonth and x[10] == 'Completed' and x[4] >= oneYRago:
                    cntLst.append(x)
                else:
                    pass
            #outputMessage(len(cntLst))
            return len(cntLst) #Record Count
        
        '''
        Function to count the number of Completed-Commited AOIs with a 30cm GSD that were produced
        within the last year (365 days) divided up by tasking month.
        
        Inputs:
        inLst -- The metro completed table as a list
        inMonth -- The desired month number for an attribure query
        outLst -- A named blank list to be populated with Completed-Commited-30cm products built within the last year
        
        Output:
        cntLst -- Nested list of Completed-Commited-30cm AOIs built within last year
        '''
        def numComplete30cmCom(inLst,inMonth):
            cntLst = []
            for x in inLst:
                #outputMessage("{0},{1},{2},{3},{4}".format(x[8],x[10],x[4],x[13],x[12]))
                if x[4] == None:
                    pass
                elif x[8] == inMonth and x[10] == 'Completed' and x[13] == '0.3' and x[12] == '30_Com' and x[4] >= oneYRago:
                    cntLst.append(x)
                else:
                    pass
            #outputMessage(cntLst)
            return len(cntLst) #Record Count
        
        '''
        Function to create list of Completed-Commited AOIs with a 30cm GSD that were produced
        within the last year (365 days) divided up by tasking month.
        
        Inputs:
        inLst -- The metro completed table as a list
        inMonth -- The desired month number for an attribure query
        outLst -- A named blank list to be populated with Completed-Commited-30cm products built within the last year
        
        Output:
        cntLst -- Nested list of Completed-Commited-30cm AOIs built within last year
        '''
        def lstComplete30cmCom(inLst,inMonth):
            cntLst = []
            for x in inLst:
                #outputMessage("{0},{1},{2},{3},{4}".format(x[8],x[10],x[4],x[13],x[12]))
                if x[4] == None:
                    pass
                elif x[8] == inMonth and x[10] == 'Completed' and x[13] == '0.3' and x[12] == '30_Com' and x[4] >= oneYRago:
                    cntLst.append(x)
                else:
                    pass
            #outputMessage(cntLst)
            return cntLst      
        
        '''
        Function to create a list of Completed-Variable-30cm AOIs that were produced
        within the last year (365 days) divided up by tasking month.
        
        Inputs:
        inLst -- The completed table list for a region and tasking month
        inMonth -- The desired month number for an attribure query
        
        Output:
        cntLst -- Nested list of Completed-Variable-50cm AOIs built within last year
        '''
        def lstComplete30cmVar(inLst,inMonth):
            cntLst = []
            for x in inLst:
                #outputMessage("{0},{1},{2},{3},{4}".format(x[8],x[10],x[4],x[13],x[12]))
                if x[4] == None:
                    pass
                elif x[8] == inMonth and x[10] == 'Completed' and x[13] == '0.3' and x[12] == 'Var' and x[4] >= oneYRago:
                    cntLst.append(x)
                else:
                    pass
            #outputMessage(cntLst)
            return cntLst 
        
        '''
        Function to create a list of Completed-Variable-50cm AOIs that were produced
        within the last year (365 days) divided up by tasking month.
        
        Inputs:
        inLst -- The completed table list for a region and tasking month
        inMonth -- The desired month number for an attribure query
        
        Output:
        cntLst -- Nested list of Completed-Variable-30cm AOIs built within last year
        '''
        def lstComplete50cmVar(inLst,inMonth):
            cntLst = []
            for x in inLst:
                #outputMessage("{0},{1},{2},{3},{4}".format(x[8],x[10],x[4],x[13],x[12]))
                if x[4] == None:
                    pass
                elif x[8] == inMonth and x[10] == 'Completed' and x[13] == '0.5' and x[12] == 'Var' and x[4] >= oneYRago:
                    cntLst.append(x)
                else:
                    pass
            #outputMessage(cntLst)
            return cntLst 
        
        '''
        Function to count the number of AOIs in "Ordered" status that are within 
        SLA using the region, the start tasking date, and production status
        
        Inputs:
        inLst -- The metro production table as a list
        inMonth -- The desired month for query
        
        Output:
        Record Count -- The count of selected records 
        
        '''
        def numProduction(inLst,inMonth):
            cntLst = []
            for x in inLst:
                if x[8] == inMonth and x[10] == 'Ordered':
                    cntLst.append(x)
                else:
                    pass
            #outputMessage("Ordered products for {0}: {1}".format(inMonth,len(cntLst)))
            return len(cntLst) #Record Count
            
        '''
        Function to count the number of records with "Fulfilled" status
        within the last year (365 days) divided up by tasking month.
        
        Inputs:
        inLst -- The metro production table as a list
        inMonth -- The desired month for query
        
        Output:
        Record Count -- The count of selected records 
        
        '''
        def numFulfilled(inLst,inMonth):
            cntLst = []
            for x in inLst:
                if x[8] == inMonth and x[10] == 'Fulfilled':
                    cntLst.append(x)
                else:
                    pass
            #outputMessage("Fulfilled products for {0}: {1}".format(inMonth,len(cntLst)))
            return len(cntLst) #Record Count
        
        '''
        Function to count the number of records with "Tasking" status
        within the last year (365 days) divided up by tasking month.
        
        Inputs:
        inLst -- The metro production table as a list
        inMonth -- The desired month for query
        
        Output:
        Record Count -- The count of selected records 
        
        '''
        def numTasking(inLst,inMonth):
            cntLst = []
            for x in inLst:
                #outputMessage("{0},{1},{2}".format(x[8],x[10],x[4]))
                if x[8] == inMonth and x[10] == 'Tasking':
                    cntLst.append(x)
                else:
                    pass
            #outputMessage("Tasking products for {0}: {1}".format(inMonth,len(cntLst)))
            return len(cntLst) #Record Count
        
        '''
        Function to count the number of records that are out of SLA. Their production 
        status is not "Completed","Ordered", or "Fulfilled".  
        
        Inputs:
        inTbl -- The metro production table as a list
        inMonth -- The desired month number for an attribure query
        
        Output:
        Record Count -- The count of selected records 
        '''
        def numMiscNoData(inLst,inMonth):
            cntLst = []
            for x in inLst:
                if x[8] == inMonth and (x[10] == 'Misc' or x[10] == 'No Data (DEFAULT)'):
                    cntLst.append(x)
                else:
                    pass
            #outputMessage(len(cntLst))
            return len(cntLst) #Record Count        

        '''
        Function to create a list of Acquisition Date and Area km2 for each product found with the 
        highest production run in the completed list. Funciton is called inside of another function.
        
        Inputs:
        prodName -- The currently selected product name, the highest production run for an Aoi
        metadata -- The full metadata list of all metadata
        
        Outputs:
        outLst -- An output list containing the acq date and area km2 for a named product
        
        '''        
        def metaList(prodName, metadata, outLst):
            for x in range(len(metadata)):
                yLst = []
                if metadata[x][0] == prodName:
                    yLst.append(metadata[x][1]) #Acq Date
                    yLst.append(metadata[x][2]) #Area KM2
                    outLst.append(yLst)          
              
        '''
        Function to find the percent area of a finished a product that falls inside within the 
        12 month SLA and output the percentage.
        
        Inputs:
        pDate -- The production date for the input product
        inLst -- The metadata list for selected product containing seamline acquisition 
                 data and area sqkm2.
        
        Output:
        percentCoverage -- Returns the percent area coverage of the product within 1yr SLA  
        
        '''        
        def percent12Mos(pDate,inLst,productName):
            
            # Check that the input list is not empty. An empty list triggers a float division by zero error. If the 
            # input list is empty it is because there is something wrong with the data in the dataset. Likely, the
            # the product name is not found in the metadata dataset.            
            if len(inLst) == 0:
                outputError("\n######## !!!ERROR!!! ########\n\t Error encountered for product name: {0}!!\
                \n\t Double check the product name exists in all Metro 2.0 tables and feature datasets.\
                \n######## !!!ERROR!!! ########".format(productName))
            else:
                # Get the product date from input list
                prodDate = pDate[0]
                #outputMessage("Production date is: {0}\nList is: {1}".format(prodDate,inLst))
                
                # Create new list for storing just Acqdate,AreaKM2 - key,value pairs
                nestLst = []
                     
                #Dictionary for storing the acquired date and the total area
                dateDic = {}        
                
                # Build a dictionary with the Acq image date and the area of the strip
                for x in range(len(inLst)):
                    eggLst = []
                    eggLst.append(inLst[x][0]) #AcqDate
                    eggLst.append(inLst[x][1]) #AreaKM2
                    nestLst.append(eggLst)
                    
                    #outputMessage("Acq Date is: {0}".format(inLst[x][0]))
                    #outputMessage("Area is: {0}".format(inLst[x][1]))
                
                # Sum the area based on date and write to dictionary
                for date,area in nestLst:
                    total = dateDic.get(date,0) + area
                    dateDic[date] = total      
                #outputMessage(dateDic)
            
                #Show me what is in the dictionary to see if it is accurate
                #outputMessage("Dictionary is: {0}".format(dateDic))
                
                #Find the total area km2 of the product     
                sumVal = sum(dateDic.values())
                
                #Check the total area km2 is correct
                #outputMessage("Total Area KM2 is: {0}".format(sumVal))
                
                #Variable for storing total area of images less than 365 days in age
                sumArea = 0
                    
                #Loop through the date acq & date keys
                for key in dateDic:
    
                    # Get image age in days
                    age     = abs(prodDate-key)
                    ageDays = age.days
                    #outputMessage("Age is: {0}".format(ageDays))
                       
                    if ageDays <= 365:
                        #outputMessage("Age Less than 365 :)") 
                        
                        # Get the image area for the image if it is newer than 365 days
                        areaValue = dateDic.get(key)                        
                        #outputMessage(areaValue)
                        
                        # Add the area of the selected image to the running total
                        sumArea = sumArea + areaValue
                        #outputMessage("Sum area = {}".format(sumArea))
                        
                    else:
                        pass
                    
                # Calculate the percentage of coverage
                percentCoverage = (float(sumArea)/sumVal)*100
                #outputMessage("Coverage percent = {}".format(percentCoverage))
                
                #outputMessage("% Cover is: {0}".format(coverage))
                return percentCoverage            
            
        '''
        Function to find the percent area of a finished a product that falls inside within the 
        24 month SLA and output the percentage.
        
        Inputs:
        pDate -- The production date for the input product
        inLst -- The metadata list of seamline acquisition data and area sqkm2
        
        Output:
        percentCoverage -- Returns the percent area coverage of the product within 2yr SLA  
        
        '''        
        def percent24Mos(pDate,inLst,productName):
            
            # Check that the input list is not empty. An empty list triggers a float division by zero error. If the 
            # input list is empty it is because there is something wrong with the data in the dataset. Likely, the
            # the product name is not found in the metadata dataset.            
            if len(inLst) == 0:
                outputError("\n######## !!!ERROR!!! ########\n\t Error encountered for product name: {0}!!\
                \n\t Double check the product name exists in all Metro 2.0 tables and feature datasets.\
                \n######## !!!ERROR!!! ########".format(productName))
            
            else:
                # Get the product name from input list
                prodDate = pDate[0]
                #outputMessage("Production date is: {0}".format(prodDate))
                
                # Create new list for storing just Acqdate,AreaKM2 - key,value pairs
                nestLst = []
                     
                #Dictionary for storing the acquired date and the total area
                dateDic = {}
                
                # Build a dictionary with the Acq image date and the area of the strip
                for x in range(len(inLst)):
                    eggLst = []
                    eggLst.append(inLst[x][0]) #AcqDate
                    eggLst.append(inLst[x][1]) #AreaKM2
                    nestLst.append(eggLst)
                    
                    #outputMessage("Acq Date is: {0}".format(inLst[x][0]))
                    #outputMessage("Area is: {0}".format(inLst[x][1]))
                
                # Sum the area based on date and write to dictionary
                for date,area in nestLst:
                    total = dateDic.get(date,0) + area
                    dateDic[date] = total      
                #outputMessage(dateDic)             
        
                #Show me what is in the dictionary to see if it is accurate
                #outputMessage("Dictionary is: {0}".format(dateDic))
                
                #Find the total area km2 of the product     
                sumVal = sum(dateDic.values())
                
                #Check the total area km2 is correct
                #outputMessage("Total Area KM2 is: {0}".format(sumVal))
                
                #Variable for storing total area of images less than 365 days in age
                sumArea = 0
                    
                #Loop through the date acq & date keys
                for key in dateDic:
    
                    # Get image age in days
                    age     = abs(prodDate-key)
                    ageDays = age.days
                    #outputMessage("Age is: {0}".format(ageDays))
                       
                    if ageDays > 365:
                        #outputMessage("Age is greater than 365 :)") 
                        
                        # Get the image area for the image if it is newer than 365 days
                        areaValue = dateDic.get(key)                        
                        #outputMessage("Total Area older than 365 days: {0}".format(areaValue))
                        
                        # Add the area of the selected image to the running total
                        sumArea = sumArea + areaValue
                        #outputMessage("Sum area = {0}".format(sumArea))
                        
                    else:
                        pass                   
                            
                # Calculate the percentage of coverage
                percentCoverage = (float(sumArea)/sumVal)*100
                #outputMessage("Coverage percent = {0}".format(coverage))
                
                #outputMessage("% Cover is: {0}".format(coverage))
                return percentCoverage            
        
        '''
        Function to count the number of AOIs with Commited-30cm that are in roll off, >75% area, within 12month/1yr 
        of the production date.
        
        Inputs:
        inProductLst -- The list of product names that are the highest production run taken 
                        from completed table
        inCompletedLst -- The list of all completed metros, used to get the production date 
                          for the desired product
        inMetaDataLst -- The complete metadata list with acq date and area km2 for calculating % area
                        within 1yr of age
        
        Output:
        prodCount -- A count of all the products that meet the SLA requirement of 1yr
        '''
        def numComOver12mos(inProductLst,inCompletedLst,inMetaDataLst):
            #outputMessage(inCompletedLst)
            
            #Counter for number of products are within the 1yr SLA at 75% of total area
            prodCount = 0
            
            for product in inProductLst:
                #outputMessage(product)
                
                # Retrieve the production date for the desired product from the completed table list
                prodDate = [inCompletedLst[x][4] for x in range(len(inCompletedLst)) if inCompletedLst[x][1] == product]
                #outputMessage(prodDate)
                
                # Make a list of the acq date & area for the named product
                xLst = []
                metaList(product, inMetaDataLst, xLst)
                #outputMessage("xLst: {0}".format(xLst))
                
                # Calculate the % coverage within 12 months
                twelveMonths = percent12Mos(prodDate,xLst,product) #<12 mon
                #outputMessage(twelveMonths)
                
                if twelveMonths >= 75:
                    prodCount += 1
                else:
                    pass
                
            #outputMessage(prodCount)
            return prodCount            
            
        '''
        Function to count the number of AOIs that meet the SLA criteria, 75% area, within 12month/1yr 
        of the production date.
        
        Inputs:
        inProductLst -- The list of product names that are the highest production run taken 
                        from completed table
        inCompletedLst -- The list of all completed metros, used to get the production date 
                          for the desired product
        inMetaDataLst -- The complete metadata list with acq date and area km2 for calculating % area
                        within 1yr of age
        
        Output:
        prodCount -- A count of all the products that meet the SLA requirement of 1yr
        
        '''
        def num12mos(inProductLst,inCompletedLst,inMetaDataLst):
            #outputMessage(inCompletedLst)
            
            #Counter for number of products are within the 1yr SLA at 75% of total area
            prodCount = 0
            
            for product in inProductLst:
                #outputMessage(product)
                
                # Retrieve the production date for the desired product from the completed table list
                prodDate = [inCompletedLst[x][4] for x in range(len(inCompletedLst)) if inCompletedLst[x][1] == product]
                #outputMessage(prodDate)
                
                # Make a list of the acq date & area for the named product
                xLst = []
                metaList(product, inMetaDataLst, xLst)
                #outputMessage("xLst: {0}".format(xLst))
                
                # Calculate the % coverage within 12 months
                twelveMonths = percent12Mos(prodDate,xLst,product) #<12 mon
                #outputMessage(twelveMonths)
            
                if twelveMonths >= 75:
                    prodCount += 1
                else:
                    pass

            #outputMessage(prodCount)
            return prodCount
        
        '''
        Function to count the number of AOIs that meet the SLA criteria, 75% area, within 24month/2yr 
        of the production date.
        
        Inputs:
        inProductLst -- The list of product names that are the highest production run taken 
                        from completed table
        inCompletedLst -- The list of all completed metros, used to get the production date 
                          for the desired product
        inMetaDataLst -- The complete metadata list with acq date and area km2 for calculating % area
                        within 1yr of age
        
        Output:
        prodCount -- A count of all the products that meet the SLA requirement of 1yr
        
        '''
        def num24mos(inProductLst,inCompletedLst,inMetaDataLst):
            
            #Counter for number of products that are within the 2yr SLA at 75% of total area
            prodCount = 0
            
            for product in inProductLst:
                #outputMessage(product)
                
                # Retrieve the production date for the desired product from the completed table list
                prodDate = [inCompletedLst[x][4] for x in range(len(inCompletedLst)) if inCompletedLst[x][1] == product]
                #outputMessage(prodDate)
                
                # Make a list of the acq date & area for the named product
                xLst = []
                metaList(product, inMetaDataLst, xLst)
                #outputMessage("xLst: {0}".format(xLst))
                
                # Calculate the % coverage within 12 months
                twentyMonths = percent24Mos(prodDate,xLst,product) #<24 mon
                #outputMessage(twelveMonths)
                
                if twentyMonths >= 75:
                    prodCount += 1
                else:
                    pass
                
            #outputMessage(prodCount)
            return prodCount        
        
        ##===============================##
        # Call Functions and Execute      #
        ##===============================##
        
        # Step One: Make a nested list of all AOIs for each region
        #
        # Create an AOI list for each region
        amAOIs = createAOIList(inAOIs,'AM')
        eaAOIs = createAOIList(inAOIs,'EA')
        euAOIs = createAOIList(inAOIs,'EU')
        meAOIs = createAOIList(inAOIs,'ME')
        spAOIs = createAOIList(inAOIs,'SP')
        waAOIs = createAOIList(inAOIs,'WA')
        
        # Step Two: Make a nested list of production tables for each region
        #
        # Create a production table list for each region        
        amProdLST = createProdList(inProdTbl,'AM')
        eaProdLST = createProdList(inProdTbl,'EA')
        euProdLST = createProdList(inProdTbl,'EU')
        meProdLST = createProdList(inProdTbl,'ME')
        spProdLST = createProdList(inProdTbl,'SP')
        waProdLST = createProdList(inProdTbl,'WA')
        
        # Step Three: Make a nested list of completed tables for each region. Then create a variety of 
        # derived sub lists based on queries of Category, Task Month, GSD and other fields. This shit is way too complicated. 
        #  
        # Create a completed table list for each region
        amCompLST = createCompList(inCurrentTbl,'AM')
        eaCompLST = createCompList(inCurrentTbl,'EA')
        euCompLST = createCompList(inCurrentTbl,'EU')
        meCompLST = createCompList(inCurrentTbl,'ME')
        spCompLST = createCompList(inCurrentTbl,'SP')
        waCompLST = createCompList(inCurrentTbl,'WA')
        
        # Create a list of Completed-Variable-30cm AOIs by region and tasking month 
        # for input to the num12mos() and num24mos()functions
        amComp30Var_1 = lstComplete30cmVar(amCompLST, 1)
        amComp30Var_2 = lstComplete30cmVar(amCompLST, 2)   
        amComp30Var_3 = lstComplete30cmVar(amCompLST, 3) 
        amComp30Var_4 = lstComplete30cmVar(amCompLST, 4) 
        amComp30Var_5 = lstComplete30cmVar(amCompLST, 5) 
        amComp30Var_6 = lstComplete30cmVar(amCompLST, 6) 
        amComp30Var_7 = lstComplete30cmVar(amCompLST, 7) 
        amComp30Var_8 = lstComplete30cmVar(amCompLST, 8) 
        amComp30Var_9 = lstComplete30cmVar(amCompLST, 9) 
        amComp30Var_10 = lstComplete30cmVar(amCompLST, 10) 
        amComp30Var_11 = lstComplete30cmVar(amCompLST, 11) 
        amComp30Var_12 = lstComplete30cmVar(amCompLST, 12)
        
        eaComp30Var_1 = lstComplete30cmVar(eaCompLST, 1)
        eaComp30Var_2 = lstComplete30cmVar(eaCompLST, 2)   
        eaComp30Var_3 = lstComplete30cmVar(eaCompLST, 3) 
        eaComp30Var_4 = lstComplete30cmVar(eaCompLST, 4) 
        eaComp30Var_5 = lstComplete30cmVar(eaCompLST, 5) 
        eaComp30Var_6 = lstComplete30cmVar(eaCompLST, 6) 
        eaComp30Var_7 = lstComplete30cmVar(eaCompLST, 7) 
        eaComp30Var_8 = lstComplete30cmVar(eaCompLST, 8) 
        eaComp30Var_9 = lstComplete30cmVar(eaCompLST, 9) 
        eaComp30Var_10 = lstComplete30cmVar(eaCompLST, 10) 
        eaComp30Var_11 = lstComplete30cmVar(eaCompLST, 11) 
        eaComp30Var_12 = lstComplete30cmVar(eaCompLST, 12)
        
        euComp30Var_1 = lstComplete30cmVar(euCompLST, 1)
        euComp30Var_2 = lstComplete30cmVar(euCompLST, 2)   
        euComp30Var_3 = lstComplete30cmVar(euCompLST, 3) 
        euComp30Var_4 = lstComplete30cmVar(euCompLST, 4) 
        euComp30Var_5 = lstComplete30cmVar(euCompLST, 5) 
        euComp30Var_6 = lstComplete30cmVar(euCompLST, 6) 
        euComp30Var_7 = lstComplete30cmVar(euCompLST, 7) 
        euComp30Var_8 = lstComplete30cmVar(euCompLST, 8) 
        euComp30Var_9 = lstComplete30cmVar(euCompLST, 9) 
        euComp30Var_10 = lstComplete30cmVar(euCompLST, 10) 
        euComp30Var_11 = lstComplete30cmVar(euCompLST, 11) 
        euComp30Var_12 = lstComplete30cmVar(euCompLST, 12)          
        
        meComp30Var_1 = lstComplete30cmVar(meCompLST, 1)
        meComp30Var_2 = lstComplete30cmVar(meCompLST, 2)   
        meComp30Var_3 = lstComplete30cmVar(meCompLST, 3) 
        meComp30Var_4 = lstComplete30cmVar(meCompLST, 4) 
        meComp30Var_5 = lstComplete30cmVar(meCompLST, 5) 
        meComp30Var_6 = lstComplete30cmVar(meCompLST, 6) 
        meComp30Var_7 = lstComplete30cmVar(meCompLST, 7) 
        meComp30Var_8 = lstComplete30cmVar(meCompLST, 8) 
        meComp30Var_9 = lstComplete30cmVar(meCompLST, 9) 
        meComp30Var_10 = lstComplete30cmVar(meCompLST, 10) 
        meComp30Var_11 = lstComplete30cmVar(meCompLST, 11) 
        meComp30Var_12 = lstComplete30cmVar(meCompLST, 12)  
        
        spComp30Var_1 = lstComplete30cmVar(spCompLST, 1)
        spComp30Var_2 = lstComplete30cmVar(spCompLST, 2)   
        spComp30Var_3 = lstComplete30cmVar(spCompLST, 3) 
        spComp30Var_4 = lstComplete30cmVar(spCompLST, 4) 
        spComp30Var_5 = lstComplete30cmVar(spCompLST, 5) 
        spComp30Var_6 = lstComplete30cmVar(spCompLST, 6) 
        spComp30Var_7 = lstComplete30cmVar(spCompLST, 7) 
        spComp30Var_8 = lstComplete30cmVar(spCompLST, 8) 
        spComp30Var_9 = lstComplete30cmVar(spCompLST, 9) 
        spComp30Var_10 = lstComplete30cmVar(spCompLST, 10) 
        spComp30Var_11 = lstComplete30cmVar(spCompLST, 11) 
        spComp30Var_12 = lstComplete30cmVar(spCompLST, 12)  
        
        waComp30Var_1 = lstComplete30cmVar(waCompLST, 1)
        waComp30Var_2 = lstComplete30cmVar(waCompLST, 2)   
        waComp30Var_3 = lstComplete30cmVar(waCompLST, 3) 
        waComp30Var_4 = lstComplete30cmVar(waCompLST, 4) 
        waComp30Var_5 = lstComplete30cmVar(waCompLST, 5) 
        waComp30Var_6 = lstComplete30cmVar(waCompLST, 6) 
        waComp30Var_7 = lstComplete30cmVar(waCompLST, 7) 
        waComp30Var_8 = lstComplete30cmVar(waCompLST, 8) 
        waComp30Var_9 = lstComplete30cmVar(waCompLST, 9) 
        waComp30Var_10 = lstComplete30cmVar(waCompLST, 10) 
        waComp30Var_11 = lstComplete30cmVar(waCompLST, 11) 
        waComp30Var_12 = lstComplete30cmVar(waCompLST, 12)        
        
        # Create a list of Completed-Variable-50cm AOIs by region and tasking month 
        # for input to the num12mos() and num24mos()functions
        amComp50Var_1 = lstComplete50cmVar(amCompLST, 1)
        amComp50Var_2 = lstComplete50cmVar(amCompLST, 2)
        amComp50Var_3 = lstComplete50cmVar(amCompLST, 3)
        amComp50Var_4 = lstComplete50cmVar(amCompLST, 4)
        amComp50Var_5 = lstComplete50cmVar(amCompLST, 5)
        amComp50Var_6 = lstComplete50cmVar(amCompLST, 6)
        amComp50Var_7 = lstComplete50cmVar(amCompLST, 7)
        amComp50Var_8 = lstComplete50cmVar(amCompLST, 8)
        amComp50Var_9 = lstComplete50cmVar(amCompLST, 9)
        amComp50Var_10 = lstComplete50cmVar(amCompLST, 10)
        amComp50Var_11 = lstComplete50cmVar(amCompLST, 11)
        amComp50Var_12 = lstComplete50cmVar(amCompLST, 12)
        
        eaComp50Var_1 = lstComplete50cmVar(eaCompLST, 1)
        eaComp50Var_2 = lstComplete50cmVar(eaCompLST, 2)
        eaComp50Var_3 = lstComplete50cmVar(eaCompLST, 3)
        eaComp50Var_4 = lstComplete50cmVar(eaCompLST, 4)
        eaComp50Var_5 = lstComplete50cmVar(eaCompLST, 5)
        eaComp50Var_6 = lstComplete50cmVar(eaCompLST, 6)
        eaComp50Var_7 = lstComplete50cmVar(eaCompLST, 7)
        eaComp50Var_8 = lstComplete50cmVar(eaCompLST, 8)
        eaComp50Var_9 = lstComplete50cmVar(eaCompLST, 9)
        eaComp50Var_10 = lstComplete50cmVar(eaCompLST, 10)
        eaComp50Var_11 = lstComplete50cmVar(eaCompLST, 11)
        eaComp50Var_12 = lstComplete50cmVar(eaCompLST, 12)   
        
        euComp50Var_1 = lstComplete50cmVar(euCompLST, 1)
        euComp50Var_2 = lstComplete50cmVar(euCompLST, 2)
        euComp50Var_3 = lstComplete50cmVar(euCompLST, 3)
        euComp50Var_4 = lstComplete50cmVar(euCompLST, 4)
        euComp50Var_5 = lstComplete50cmVar(euCompLST, 5)
        euComp50Var_6 = lstComplete50cmVar(euCompLST, 6)
        euComp50Var_7 = lstComplete50cmVar(euCompLST, 7)
        euComp50Var_8 = lstComplete50cmVar(euCompLST, 8)
        euComp50Var_9 = lstComplete50cmVar(euCompLST, 9)
        euComp50Var_10 = lstComplete50cmVar(euCompLST, 10)
        euComp50Var_11 = lstComplete50cmVar(euCompLST, 11)
        euComp50Var_12 = lstComplete50cmVar(euCompLST, 12)
        
        meComp50Var_1 = lstComplete50cmVar(meCompLST, 1)
        meComp50Var_2 = lstComplete50cmVar(meCompLST, 2)
        meComp50Var_3 = lstComplete50cmVar(meCompLST, 3)
        meComp50Var_4 = lstComplete50cmVar(meCompLST, 4)
        meComp50Var_5 = lstComplete50cmVar(meCompLST, 5)
        meComp50Var_6 = lstComplete50cmVar(meCompLST, 6)
        meComp50Var_7 = lstComplete50cmVar(meCompLST, 7)
        meComp50Var_8 = lstComplete50cmVar(meCompLST, 8)
        meComp50Var_9 = lstComplete50cmVar(meCompLST, 9)
        meComp50Var_10 = lstComplete50cmVar(meCompLST, 10)
        meComp50Var_11 = lstComplete50cmVar(meCompLST, 11)
        meComp50Var_12 = lstComplete50cmVar(meCompLST, 12)
        
        spComp50Var_1 = lstComplete50cmVar(spCompLST, 1)
        spComp50Var_2 = lstComplete50cmVar(spCompLST, 2)
        spComp50Var_3 = lstComplete50cmVar(spCompLST, 3)
        spComp50Var_4 = lstComplete50cmVar(spCompLST, 4)
        spComp50Var_5 = lstComplete50cmVar(spCompLST, 5)
        spComp50Var_6 = lstComplete50cmVar(spCompLST, 6)
        spComp50Var_7 = lstComplete50cmVar(spCompLST, 7)
        spComp50Var_8 = lstComplete50cmVar(spCompLST, 8)
        spComp50Var_9 = lstComplete50cmVar(spCompLST, 9)
        spComp50Var_10 = lstComplete50cmVar(spCompLST, 10)
        spComp50Var_11 = lstComplete50cmVar(spCompLST, 11)
        spComp50Var_12 = lstComplete50cmVar(spCompLST, 12)
        
        waComp50Var_1 = lstComplete50cmVar(waCompLST, 1)
        waComp50Var_2 = lstComplete50cmVar(waCompLST, 2)
        waComp50Var_3 = lstComplete50cmVar(waCompLST, 3)
        waComp50Var_4 = lstComplete50cmVar(waCompLST, 4)
        waComp50Var_5 = lstComplete50cmVar(waCompLST, 5)
        waComp50Var_6 = lstComplete50cmVar(waCompLST, 6)
        waComp50Var_7 = lstComplete50cmVar(waCompLST, 7)
        waComp50Var_8 = lstComplete50cmVar(waCompLST, 8)
        waComp50Var_9 = lstComplete50cmVar(waCompLST, 9)
        waComp50Var_10 = lstComplete50cmVar(waCompLST, 10)
        waComp50Var_11 = lstComplete50cmVar(waCompLST, 11)
        waComp50Var_12 = lstComplete50cmVar(waCompLST, 12)        
        
        # Create a list of Completed-Commited-30cm AOIs by region and tasking month 
        # for input to the numComOver12mos()     
        amComp30Com_1 = lstComplete30cmCom(amCompLST, 1)
        amComp30Com_2 = lstComplete30cmCom(amCompLST, 2)
        amComp30Com_3 = lstComplete30cmCom(amCompLST, 3)
        amComp30Com_4 = lstComplete30cmCom(amCompLST, 4)
        amComp30Com_5 = lstComplete30cmCom(amCompLST, 5)
        amComp30Com_6 = lstComplete30cmCom(amCompLST, 6)
        amComp30Com_7 = lstComplete30cmCom(amCompLST, 7)
        amComp30Com_8 = lstComplete30cmCom(amCompLST, 8)
        amComp30Com_9 = lstComplete30cmCom(amCompLST, 9)
        amComp30Com_10 = lstComplete30cmCom(amCompLST, 10)
        amComp30Com_11 = lstComplete30cmCom(amCompLST, 11)
        amComp30Com_12 = lstComplete30cmCom(amCompLST, 12)
        
        eaComp30Com_1 = lstComplete30cmCom(eaCompLST, 1)
        eaComp30Com_2 = lstComplete30cmCom(eaCompLST, 2)
        eaComp30Com_3 = lstComplete30cmCom(eaCompLST, 3)
        eaComp30Com_4 = lstComplete30cmCom(eaCompLST, 4)
        eaComp30Com_5 = lstComplete30cmCom(eaCompLST, 5)
        eaComp30Com_6 = lstComplete30cmCom(eaCompLST, 6)
        eaComp30Com_7 = lstComplete30cmCom(eaCompLST, 7)
        eaComp30Com_8 = lstComplete30cmCom(eaCompLST, 8)
        eaComp30Com_9 = lstComplete30cmCom(eaCompLST, 9)
        eaComp30Com_10 = lstComplete30cmCom(eaCompLST, 10)
        eaComp30Com_11 = lstComplete30cmCom(eaCompLST, 11)
        eaComp30Com_12 = lstComplete30cmCom(eaCompLST, 12)
        
        euComp30Com_1 = lstComplete30cmCom(euCompLST, 1)
        euComp30Com_2 = lstComplete30cmCom(euCompLST, 2)
        euComp30Com_3 = lstComplete30cmCom(euCompLST, 3)
        euComp30Com_4 = lstComplete30cmCom(euCompLST, 4)
        euComp30Com_5 = lstComplete30cmCom(euCompLST, 5)
        euComp30Com_6 = lstComplete30cmCom(euCompLST, 6)
        euComp30Com_7 = lstComplete30cmCom(euCompLST, 7)
        euComp30Com_8 = lstComplete30cmCom(euCompLST, 8)
        euComp30Com_9 = lstComplete30cmCom(euCompLST, 9)
        euComp30Com_10 = lstComplete30cmCom(euCompLST, 10)
        euComp30Com_11 = lstComplete30cmCom(euCompLST, 11)
        euComp30Com_12 = lstComplete30cmCom(euCompLST, 12)
        
        meComp30Com_1 = lstComplete30cmCom(meCompLST, 1)
        meComp30Com_2 = lstComplete30cmCom(meCompLST, 2)
        meComp30Com_3 = lstComplete30cmCom(meCompLST, 3)
        meComp30Com_4 = lstComplete30cmCom(meCompLST, 4)
        meComp30Com_5 = lstComplete30cmCom(meCompLST, 5)
        meComp30Com_6 = lstComplete30cmCom(meCompLST, 6)
        meComp30Com_7 = lstComplete30cmCom(meCompLST, 7)
        meComp30Com_8 = lstComplete30cmCom(meCompLST, 8)
        meComp30Com_9 = lstComplete30cmCom(meCompLST, 9)
        meComp30Com_10 = lstComplete30cmCom(meCompLST, 10)
        meComp30Com_11 = lstComplete30cmCom(meCompLST, 11)
        meComp30Com_12 = lstComplete30cmCom(meCompLST, 12)
        
        spComp30Com_1 = lstComplete30cmCom(spCompLST, 1)
        spComp30Com_2 = lstComplete30cmCom(spCompLST, 2)
        spComp30Com_3 = lstComplete30cmCom(spCompLST, 3)
        spComp30Com_4 = lstComplete30cmCom(spCompLST, 4)
        spComp30Com_5 = lstComplete30cmCom(spCompLST, 5)
        spComp30Com_6 = lstComplete30cmCom(spCompLST, 6)
        spComp30Com_7 = lstComplete30cmCom(spCompLST, 7)
        spComp30Com_8 = lstComplete30cmCom(spCompLST, 8)
        spComp30Com_9 = lstComplete30cmCom(spCompLST, 9)
        spComp30Com_10 = lstComplete30cmCom(spCompLST, 10)
        spComp30Com_11 = lstComplete30cmCom(spCompLST, 11)
        spComp30Com_12 = lstComplete30cmCom(spCompLST, 12)
        
        waComp30Com_1 = lstComplete30cmCom(waCompLST, 1)
        waComp30Com_2 = lstComplete30cmCom(waCompLST, 2)
        waComp30Com_3 = lstComplete30cmCom(waCompLST, 3)
        waComp30Com_4 = lstComplete30cmCom(waCompLST, 4)
        waComp30Com_5 = lstComplete30cmCom(waCompLST, 5)
        waComp30Com_6 = lstComplete30cmCom(waCompLST, 6)
        waComp30Com_7 = lstComplete30cmCom(waCompLST, 7)
        waComp30Com_8 = lstComplete30cmCom(waCompLST, 8)
        waComp30Com_9 = lstComplete30cmCom(waCompLST, 9)
        waComp30Com_10 = lstComplete30cmCom(waCompLST, 10)
        waComp30Com_11 = lstComplete30cmCom(waCompLST, 11)
        waComp30Com_12 = lstComplete30cmCom(waCompLST, 12)        

        # Create a product name list from the completed table of all the highest production 
        # runs with Completed-Variable-30cm
        amCurrentLST_30cm_1 = currentProducts(amComp30Var_1)
        amCurrentLST_30cm_2 = currentProducts(amComp30Var_2)
        amCurrentLST_30cm_3 = currentProducts(amComp30Var_3)
        amCurrentLST_30cm_4 = currentProducts(amComp30Var_4)
        amCurrentLST_30cm_5 = currentProducts(amComp30Var_5)
        amCurrentLST_30cm_6 = currentProducts(amComp30Var_6)
        amCurrentLST_30cm_7 = currentProducts(amComp30Var_7)
        amCurrentLST_30cm_8 = currentProducts(amComp30Var_8)
        amCurrentLST_30cm_9 = currentProducts(amComp30Var_9)
        amCurrentLST_30cm_10 = currentProducts(amComp30Var_10)
        amCurrentLST_30cm_11 = currentProducts(amComp30Var_11)
        amCurrentLST_30cm_12 = currentProducts(amComp30Var_12)
        
        eaCurrentLST_30cm_1 = currentProducts(eaComp30Var_1)
        eaCurrentLST_30cm_2 = currentProducts(eaComp30Var_2)
        eaCurrentLST_30cm_3 = currentProducts(eaComp30Var_3)
        eaCurrentLST_30cm_4 = currentProducts(eaComp30Var_4)
        eaCurrentLST_30cm_5 = currentProducts(eaComp30Var_5)
        eaCurrentLST_30cm_6 = currentProducts(eaComp30Var_6)
        eaCurrentLST_30cm_7 = currentProducts(eaComp30Var_7)
        eaCurrentLST_30cm_8 = currentProducts(eaComp30Var_8)
        eaCurrentLST_30cm_9 = currentProducts(eaComp30Var_9)
        eaCurrentLST_30cm_10 = currentProducts(eaComp30Var_10)
        eaCurrentLST_30cm_11 = currentProducts(eaComp30Var_11)
        eaCurrentLST_30cm_12 = currentProducts(eaComp30Var_12)
        
        euCurrentLST_30cm_1 = currentProducts(euComp30Var_1)
        euCurrentLST_30cm_2 = currentProducts(euComp30Var_2)
        euCurrentLST_30cm_3 = currentProducts(euComp30Var_3)
        euCurrentLST_30cm_4 = currentProducts(euComp30Var_4)
        euCurrentLST_30cm_5 = currentProducts(euComp30Var_5)
        euCurrentLST_30cm_6 = currentProducts(euComp30Var_6)
        euCurrentLST_30cm_7 = currentProducts(euComp30Var_7)
        euCurrentLST_30cm_8 = currentProducts(euComp30Var_8)
        euCurrentLST_30cm_9 = currentProducts(euComp30Var_9)
        euCurrentLST_30cm_10 = currentProducts(euComp30Var_10)
        euCurrentLST_30cm_11 = currentProducts(euComp30Var_11)
        euCurrentLST_30cm_12 = currentProducts(euComp30Var_12) 
        
        meCurrentLST_30cm_1 = currentProducts(meComp30Var_1)
        meCurrentLST_30cm_2 = currentProducts(meComp30Var_2)
        meCurrentLST_30cm_3 = currentProducts(meComp30Var_3)
        meCurrentLST_30cm_4 = currentProducts(meComp30Var_4)
        meCurrentLST_30cm_5 = currentProducts(meComp30Var_5)
        meCurrentLST_30cm_6 = currentProducts(meComp30Var_6)
        meCurrentLST_30cm_7 = currentProducts(meComp30Var_7)
        meCurrentLST_30cm_8 = currentProducts(meComp30Var_8)
        meCurrentLST_30cm_9 = currentProducts(meComp30Var_9)
        meCurrentLST_30cm_10 = currentProducts(meComp30Var_10)
        meCurrentLST_30cm_11 = currentProducts(meComp30Var_11)
        meCurrentLST_30cm_12 = currentProducts(meComp30Var_12) 
        
        spCurrentLST_30cm_1 = currentProducts(spComp30Var_1)
        spCurrentLST_30cm_2 = currentProducts(spComp30Var_2)
        spCurrentLST_30cm_3 = currentProducts(spComp30Var_3)
        spCurrentLST_30cm_4 = currentProducts(spComp30Var_4)
        spCurrentLST_30cm_5 = currentProducts(spComp30Var_5)
        spCurrentLST_30cm_6 = currentProducts(spComp30Var_6)
        spCurrentLST_30cm_7 = currentProducts(spComp30Var_7)
        spCurrentLST_30cm_8 = currentProducts(spComp30Var_8)
        spCurrentLST_30cm_9 = currentProducts(spComp30Var_9)
        spCurrentLST_30cm_10 = currentProducts(spComp30Var_10)
        spCurrentLST_30cm_11 = currentProducts(spComp30Var_11)
        spCurrentLST_30cm_12 = currentProducts(spComp30Var_12) 
        
        waCurrentLST_30cm_1 = currentProducts(waComp30Var_1)
        waCurrentLST_30cm_2 = currentProducts(waComp30Var_2)
        waCurrentLST_30cm_3 = currentProducts(waComp30Var_3)
        waCurrentLST_30cm_4 = currentProducts(waComp30Var_4)
        waCurrentLST_30cm_5 = currentProducts(waComp30Var_5)
        waCurrentLST_30cm_6 = currentProducts(waComp30Var_6)
        waCurrentLST_30cm_7 = currentProducts(waComp30Var_7)
        waCurrentLST_30cm_8 = currentProducts(waComp30Var_8)
        waCurrentLST_30cm_9 = currentProducts(waComp30Var_9)
        waCurrentLST_30cm_10 = currentProducts(waComp30Var_10)
        waCurrentLST_30cm_11 = currentProducts(waComp30Var_11)
        waCurrentLST_30cm_12 = currentProducts(waComp30Var_12) 
        
        # Create a product name list from the completed table of all the highest production 
        # runs with Completed-Variable-50cm      
        amCurrentLST_50cm_1 = currentProducts(amComp50Var_1)
        amCurrentLST_50cm_2 = currentProducts(amComp50Var_2)
        amCurrentLST_50cm_3 = currentProducts(amComp50Var_3)
        amCurrentLST_50cm_4 = currentProducts(amComp50Var_4)
        amCurrentLST_50cm_5 = currentProducts(amComp50Var_5)
        amCurrentLST_50cm_6 = currentProducts(amComp50Var_6)
        amCurrentLST_50cm_7 = currentProducts(amComp50Var_7)
        amCurrentLST_50cm_8 = currentProducts(amComp50Var_8)
        amCurrentLST_50cm_9 = currentProducts(amComp50Var_9)
        amCurrentLST_50cm_10 = currentProducts(amComp50Var_10)
        amCurrentLST_50cm_11 = currentProducts(amComp50Var_11)
        amCurrentLST_50cm_12 = currentProducts(amComp50Var_12)
        
        eaCurrentLST_50cm_1 = currentProducts(eaComp50Var_1)
        eaCurrentLST_50cm_2 = currentProducts(eaComp50Var_2)
        eaCurrentLST_50cm_3 = currentProducts(eaComp50Var_3)
        eaCurrentLST_50cm_4 = currentProducts(eaComp50Var_4)
        eaCurrentLST_50cm_5 = currentProducts(eaComp50Var_5)
        eaCurrentLST_50cm_6 = currentProducts(eaComp50Var_6)
        eaCurrentLST_50cm_7 = currentProducts(eaComp50Var_7)
        eaCurrentLST_50cm_8 = currentProducts(eaComp50Var_8)
        eaCurrentLST_50cm_9 = currentProducts(eaComp50Var_9)
        eaCurrentLST_50cm_10 = currentProducts(eaComp50Var_10)
        eaCurrentLST_50cm_11 = currentProducts(eaComp50Var_11)
        eaCurrentLST_50cm_12 = currentProducts(eaComp50Var_12)
        
        euCurrentLST_50cm_1 = currentProducts(euComp50Var_1)
        euCurrentLST_50cm_2 = currentProducts(euComp50Var_2)
        euCurrentLST_50cm_3 = currentProducts(euComp50Var_3)
        euCurrentLST_50cm_4 = currentProducts(euComp50Var_4)
        euCurrentLST_50cm_5 = currentProducts(euComp50Var_5)
        euCurrentLST_50cm_6 = currentProducts(euComp50Var_6)
        euCurrentLST_50cm_7 = currentProducts(euComp50Var_7)
        euCurrentLST_50cm_8 = currentProducts(euComp50Var_8)
        euCurrentLST_50cm_9 = currentProducts(euComp50Var_9)
        euCurrentLST_50cm_10 = currentProducts(euComp50Var_10)
        euCurrentLST_50cm_11 = currentProducts(euComp50Var_11)
        euCurrentLST_50cm_12 = currentProducts(euComp50Var_12)
        
        meCurrentLST_50cm_1 = currentProducts(meComp50Var_1)
        meCurrentLST_50cm_2 = currentProducts(meComp50Var_2)
        meCurrentLST_50cm_3 = currentProducts(meComp50Var_3)
        meCurrentLST_50cm_4 = currentProducts(meComp50Var_4)
        meCurrentLST_50cm_5 = currentProducts(meComp50Var_5)
        meCurrentLST_50cm_6 = currentProducts(meComp50Var_6)
        meCurrentLST_50cm_7 = currentProducts(meComp50Var_7)
        meCurrentLST_50cm_8 = currentProducts(meComp50Var_8)
        meCurrentLST_50cm_9 = currentProducts(meComp50Var_9)
        meCurrentLST_50cm_10 = currentProducts(meComp50Var_10)
        meCurrentLST_50cm_11 = currentProducts(meComp50Var_11)
        meCurrentLST_50cm_12 = currentProducts(meComp50Var_12)
        
        spCurrentLST_50cm_1 = currentProducts(spComp50Var_1)
        spCurrentLST_50cm_2 = currentProducts(spComp50Var_2)
        spCurrentLST_50cm_3 = currentProducts(spComp50Var_3)
        spCurrentLST_50cm_4 = currentProducts(spComp50Var_4)
        spCurrentLST_50cm_5 = currentProducts(spComp50Var_5)
        spCurrentLST_50cm_6 = currentProducts(spComp50Var_6)
        spCurrentLST_50cm_7 = currentProducts(spComp50Var_7)
        spCurrentLST_50cm_8 = currentProducts(spComp50Var_8)
        spCurrentLST_50cm_9 = currentProducts(spComp50Var_9)
        spCurrentLST_50cm_10 = currentProducts(spComp50Var_10)
        spCurrentLST_50cm_11 = currentProducts(spComp50Var_11)
        spCurrentLST_50cm_12 = currentProducts(spComp50Var_12)
        
        waCurrentLST_50cm_1 = currentProducts(waComp50Var_1)
        waCurrentLST_50cm_2 = currentProducts(waComp50Var_2)
        waCurrentLST_50cm_3 = currentProducts(waComp50Var_3)
        waCurrentLST_50cm_4 = currentProducts(waComp50Var_4)
        waCurrentLST_50cm_5 = currentProducts(waComp50Var_5)
        waCurrentLST_50cm_6 = currentProducts(waComp50Var_6)
        waCurrentLST_50cm_7 = currentProducts(waComp50Var_7)
        waCurrentLST_50cm_8 = currentProducts(waComp50Var_8)
        waCurrentLST_50cm_9 = currentProducts(waComp50Var_9)
        waCurrentLST_50cm_10 = currentProducts(waComp50Var_10)
        waCurrentLST_50cm_11 = currentProducts(waComp50Var_11)
        waCurrentLST_50cm_12 = currentProducts(waComp50Var_12)        
        
        # Create a product name list from the completed table of all the highest production 
        # runs with Completed-Commited-30cm for input to the numComOver12mos()
        amCurrentLST_30cm_C1 = currentProducts(amComp30Com_1)
        amCurrentLST_30cm_C2 = currentProducts(amComp30Com_2)
        amCurrentLST_30cm_C3 = currentProducts(amComp30Com_3)
        amCurrentLST_30cm_C4 = currentProducts(amComp30Com_4)
        amCurrentLST_30cm_C5 = currentProducts(amComp30Com_5)
        amCurrentLST_30cm_C6 = currentProducts(amComp30Com_6)
        amCurrentLST_30cm_C7 = currentProducts(amComp30Com_7)
        amCurrentLST_30cm_C8 = currentProducts(amComp30Com_8)
        amCurrentLST_30cm_C9 = currentProducts(amComp30Com_9)
        amCurrentLST_30cm_C10 = currentProducts(amComp30Com_10)
        amCurrentLST_30cm_C11 = currentProducts(amComp30Com_11)
        amCurrentLST_30cm_C12 = currentProducts(amComp30Com_12)
        
        eaCurrentLST_30cm_C1 = currentProducts(eaComp30Com_1)
        eaCurrentLST_30cm_C2 = currentProducts(eaComp30Com_2)
        eaCurrentLST_30cm_C3 = currentProducts(eaComp30Com_3)
        eaCurrentLST_30cm_C4 = currentProducts(eaComp30Com_4)
        eaCurrentLST_30cm_C5 = currentProducts(eaComp30Com_5)
        eaCurrentLST_30cm_C6 = currentProducts(eaComp30Com_6)
        eaCurrentLST_30cm_C7 = currentProducts(eaComp30Com_7)
        eaCurrentLST_30cm_C8 = currentProducts(eaComp30Com_8)
        eaCurrentLST_30cm_C9 = currentProducts(eaComp30Com_9)
        eaCurrentLST_30cm_C10 = currentProducts(eaComp30Com_10)
        eaCurrentLST_30cm_C11 = currentProducts(eaComp30Com_11)
        eaCurrentLST_30cm_C12 = currentProducts(eaComp30Com_12)     
        
        euCurrentLST_30cm_C1 = currentProducts(euComp30Com_1)
        euCurrentLST_30cm_C2 = currentProducts(euComp30Com_2)
        euCurrentLST_30cm_C3 = currentProducts(euComp30Com_3)
        euCurrentLST_30cm_C4 = currentProducts(euComp30Com_4)
        euCurrentLST_30cm_C5 = currentProducts(euComp30Com_5)
        euCurrentLST_30cm_C6 = currentProducts(euComp30Com_6)
        euCurrentLST_30cm_C7 = currentProducts(euComp30Com_7)
        euCurrentLST_30cm_C8 = currentProducts(euComp30Com_8)
        euCurrentLST_30cm_C9 = currentProducts(euComp30Com_9)
        euCurrentLST_30cm_C10 = currentProducts(euComp30Com_10)
        euCurrentLST_30cm_C11 = currentProducts(euComp30Com_11)
        euCurrentLST_30cm_C12 = currentProducts(euComp30Com_12)     
        
        meCurrentLST_30cm_C1 = currentProducts(meComp30Com_1)
        meCurrentLST_30cm_C2 = currentProducts(meComp30Com_2)
        meCurrentLST_30cm_C3 = currentProducts(meComp30Com_3)
        meCurrentLST_30cm_C4 = currentProducts(meComp30Com_4)
        meCurrentLST_30cm_C5 = currentProducts(meComp30Com_5)
        meCurrentLST_30cm_C6 = currentProducts(meComp30Com_6)
        meCurrentLST_30cm_C7 = currentProducts(meComp30Com_7)
        meCurrentLST_30cm_C8 = currentProducts(meComp30Com_8)
        meCurrentLST_30cm_C9 = currentProducts(meComp30Com_9)
        meCurrentLST_30cm_C10 = currentProducts(meComp30Com_10)
        meCurrentLST_30cm_C11 = currentProducts(meComp30Com_11)
        meCurrentLST_30cm_C12 = currentProducts(meComp30Com_12)     
        
        spCurrentLST_30cm_C1 = currentProducts(spComp30Com_1)
        spCurrentLST_30cm_C2 = currentProducts(spComp30Com_2)
        spCurrentLST_30cm_C3 = currentProducts(spComp30Com_3)
        spCurrentLST_30cm_C4 = currentProducts(spComp30Com_4)
        spCurrentLST_30cm_C5 = currentProducts(spComp30Com_5)
        spCurrentLST_30cm_C6 = currentProducts(spComp30Com_6)
        spCurrentLST_30cm_C7 = currentProducts(spComp30Com_7)
        spCurrentLST_30cm_C8 = currentProducts(spComp30Com_8)
        spCurrentLST_30cm_C9 = currentProducts(spComp30Com_9)
        spCurrentLST_30cm_C10 = currentProducts(spComp30Com_10)
        spCurrentLST_30cm_C11 = currentProducts(spComp30Com_11)
        spCurrentLST_30cm_C12 = currentProducts(spComp30Com_12)     
        
        waCurrentLST_30cm_C1 = currentProducts(waComp30Com_1)
        waCurrentLST_30cm_C2 = currentProducts(waComp30Com_2)
        waCurrentLST_30cm_C3 = currentProducts(waComp30Com_3)
        waCurrentLST_30cm_C4 = currentProducts(waComp30Com_4)
        waCurrentLST_30cm_C5 = currentProducts(waComp30Com_5)
        waCurrentLST_30cm_C6 = currentProducts(waComp30Com_6)
        waCurrentLST_30cm_C7 = currentProducts(waComp30Com_7)
        waCurrentLST_30cm_C8 = currentProducts(waComp30Com_8)
        waCurrentLST_30cm_C9 = currentProducts(waComp30Com_9)
        waCurrentLST_30cm_C10 = currentProducts(waComp30Com_10)
        waCurrentLST_30cm_C11 = currentProducts(waComp30Com_11)
        waCurrentLST_30cm_C12 = currentProducts(waComp30Com_12)     
        
        #Step Four: Make a list copy of all the metadata seamlines
        metaDataLst = createMetaList(inMetadata)        
        
        # example of aoi counts
        #cnt12 = num12mos(amCurrentLST, amCompLST, metaDataLst)
        #cnt12 = num12mos(amCurrentLST_50cm_1, amComp50Var_1, metaDataLst)
        #cnt24 = num24mos(amCurrentLST_50cm_1, amComp50Var_1, metaDataLst)
        
        #outputMessage(cnt12)
        #outputMessage(cnt24)
        
        ##===============================##
        # Make an excel table using easyxf#
        ##===============================##
        
        style0 = xlwt.easyxf('font: name Calibri, color-index black, bold on', num_format_str = 'general')
        style2 = xlwt.easyxf('font: name Calibri, color-index black', num_format_str = 'general')
        style3 = xlwt.easyxf('font: name Calibri, color-index black', num_format_str = '0')
        style1 = xlwt.easyxf(num_format_str='D-MMM-YY')
        
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Regional_Report')
        
        #Top Header: Months and Total # AOIs
        ws.write(0, 1, "Months", style0)
        ws.write(0, 2, "Jan", style2)
        ws.write(0, 3, "Feb", style2)
        ws.write(0, 4, "Mar", style2)
        ws.write(0, 5, "Apr", style2)
        ws.write(0, 6, "May", style2)
        ws.write(0, 7, "Jun", style2)
        ws.write(0, 8, "Jul", style2)
        ws.write(0, 9, "Aug", style2)
        ws.write(0, 10, "Sep", style2)
        ws.write(0, 11, "Oct", style2)
        ws.write(0, 12, "Nov", style2)
        ws.write(0, 13, "Dec", style2)
        ws.write(0, 14, "Totals", style2)
        ws.write(1, 1, "Total # of AOIs", style0)
        ws.write(1, 2, xlwt.Formula("SUM(C4;C22;C40;C58;C76;C94)"), style2) #Jan
        ws.write(1, 3, xlwt.Formula("SUM(D4;D22;D40;D58;D76;D94)"), style2) #Feb
        ws.write(1, 4, xlwt.Formula("SUM(E4;E22;E40;E58;E76;E94)"), style2) #Mar
        ws.write(1, 5, xlwt.Formula("SUM(F4;F22;F40;F58;F76;F94)"), style2) #Apr
        ws.write(1, 6, xlwt.Formula("SUM(G4;G22;G40;G58;G76;G94)"), style2) #May
        ws.write(1, 7, xlwt.Formula("SUM(H4;H22;H40;H58;H76;H94)"), style2) #Jun
        ws.write(1, 8, xlwt.Formula("SUM(I4;I22;I40;I58;I76;I94)"), style2) #Jul
        ws.write(1, 9, xlwt.Formula("SUM(J4;J22;J40;J58;J76;J94)"), style2) #Aug
        ws.write(1, 10, xlwt.Formula("SUM(K4;K22;K40;K58;K76;K94)"), style2) #Sep
        ws.write(1, 11, xlwt.Formula("SUM(L4;L22;L40;L58;L76;L94)"), style2) #Oct
        ws.write(1, 12, xlwt.Formula("SUM(M4;M22;M40;M58;M76;M94)"), style2) #Nov
        ws.write(1, 13, xlwt.Formula("SUM(N4;N22;N40;N58;N76;N94)"), style2) #Dec
        ws.write(1, 14, xlwt.Formula("SUM(O4;O22;O40;O58;O76;O94)"), style3) #Totals
        
        #First Header: Americas -- AM
        ws.write(3, 0, "Americas", style0)
        ws.write(3, 1, "# of AOIs", style2)
        ws.write(3, 2, numAOIs(amAOIs, 1), style2) #Jan
        ws.write(3, 3, numAOIs(amAOIs, 2), style2) #Feb
        ws.write(3, 4, numAOIs(amAOIs, 3), style2) #Mar
        ws.write(3, 5, numAOIs(amAOIs, 4), style2) #Apr
        ws.write(3, 6, numAOIs(amAOIs, 5), style2) #May
        ws.write(3, 7, numAOIs(amAOIs, 6), style2) #Jun
        ws.write(3, 8, numAOIs(amAOIs, 7), style2) #Jul
        ws.write(3, 9, numAOIs(amAOIs, 8), style2) #Aug
        ws.write(3, 10, numAOIs(amAOIs, 9), style2) #Sep
        ws.write(3, 11, numAOIs(amAOIs, 10), style2) #Oct
        ws.write(3, 12, numAOIs(amAOIs, 11), style2) #Nov
        ws.write(3, 13, numAOIs(amAOIs, 12), style2) #Dec
        ws.write(3, 14, xlwt.Formula("SUM(C4:N4)"), style3) #Total
        ws.write(4, 1, "# of Completed AOIs (Completed this year)", style2)
        ws.write(4, 2, numComplete(amCompLST, 1), style2) #Jan
        ws.write(4, 3, numComplete(amCompLST, 2), style2) #Feb
        ws.write(4, 4, numComplete(amCompLST, 3), style2) #Mar
        ws.write(4, 5, numComplete(amCompLST, 4), style2) #Apr
        ws.write(4, 6, numComplete(amCompLST, 5), style2) #May
        ws.write(4, 7, numComplete(amCompLST, 6), style2) #Jun
        ws.write(4, 8, numComplete(amCompLST, 7), style2) #Jul
        ws.write(4, 9, numComplete(amCompLST, 8), style2) #Aug
        ws.write(4, 10, numComplete(amCompLST, 9), style2) #Sep
        ws.write(4, 11, numComplete(amCompLST, 10), style2) #Oct
        ws.write(4, 12, numComplete(amCompLST, 11), style2) #Nov
        ws.write(4, 13, numComplete(amCompLST, 12), style2) #Dec       
        ws.write(4, 14, xlwt.Formula("SUM(C5:N5)"), style3) #Total
        ws.write(5, 1, "# of Completed 30cm Committed AOIs (Completed this year)", style2)
        ws.write(5, 2, numComplete30cmCom(amProdLST, 1), style2) #Jan
        ws.write(5, 3, numComplete30cmCom(amProdLST, 2), style2) #Feb
        ws.write(5, 4, numComplete30cmCom(amProdLST, 3), style2) #Mar
        ws.write(5, 5, numComplete30cmCom(amProdLST, 4), style2) #Apr
        ws.write(5, 6, numComplete30cmCom(amProdLST, 5), style2) #May
        ws.write(5, 7, numComplete30cmCom(amProdLST, 6), style2) #Jun
        ws.write(5, 8, numComplete30cmCom(amProdLST, 7), style2) #Jul
        ws.write(5, 9, numComplete30cmCom(amProdLST, 8), style2) #Aug
        ws.write(5, 10, numComplete30cmCom(amProdLST, 9), style2) #Sep
        ws.write(5, 11, numComplete30cmCom(amProdLST, 10), style2) #Oct
        ws.write(5, 12, numComplete30cmCom(amProdLST, 11), style2) #Nov
        ws.write(5, 13, numComplete30cmCom(amProdLST, 12), style2) #Dec    
        ws.write(5, 14, xlwt.Formula("SUM(C6:N6)"), style3) #Total
        ws.write(6, 1, "# of Completed Variable AOIs 30cm 1yr (Completed this year)", style2)
        ws.write(6, 2, num12mos(amCurrentLST_30cm_1, amComp30Var_1, metaDataLst), style2) #Jan
        ws.write(6, 3, num12mos(amCurrentLST_30cm_2, amComp30Var_2, metaDataLst), style2) #Feb
        ws.write(6, 4, num12mos(amCurrentLST_30cm_3, amComp30Var_3, metaDataLst), style2) #Mar
        ws.write(6, 5, num12mos(amCurrentLST_30cm_4, amComp30Var_4, metaDataLst), style2) #Apr
        ws.write(6, 6, num12mos(amCurrentLST_30cm_5, amComp30Var_5, metaDataLst), style2) #May
        ws.write(6, 7, num12mos(amCurrentLST_30cm_6, amComp30Var_6, metaDataLst), style2) #Jun
        ws.write(6, 8, num12mos(amCurrentLST_30cm_7, amComp30Var_7, metaDataLst), style2) #Jul
        ws.write(6, 9, num12mos(amCurrentLST_30cm_8, amComp30Var_8, metaDataLst), style2) #Aug
        ws.write(6, 10, num12mos(amCurrentLST_30cm_9, amComp30Var_9, metaDataLst), style2) #Sep
        ws.write(6, 11, num12mos(amCurrentLST_30cm_10, amComp30Var_10, metaDataLst), style2) #Oct
        ws.write(6, 12, num12mos(amCurrentLST_30cm_11, amComp30Var_11, metaDataLst), style2) #Nov
        ws.write(6, 13, num12mos(amCurrentLST_30cm_12, amComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(6, 14, xlwt.Formula("SUM(C7:N7)"), style3) #Total
        ws.write(7, 1, "# of Completed Variable AOIs 30cm 2yr (Completed this year)", style2)
        ws.write(7, 2, num24mos(amCurrentLST_30cm_1, amComp30Var_1, metaDataLst), style2) #Jan
        ws.write(7, 3, num24mos(amCurrentLST_30cm_2, amComp30Var_2, metaDataLst), style2) #Feb
        ws.write(7, 4, num24mos(amCurrentLST_30cm_3, amComp30Var_3, metaDataLst), style2) #Mar
        ws.write(7, 5, num24mos(amCurrentLST_30cm_4, amComp30Var_4, metaDataLst), style2) #Apr
        ws.write(7, 6, num24mos(amCurrentLST_30cm_5, amComp30Var_5, metaDataLst), style2) #May
        ws.write(7, 7, num24mos(amCurrentLST_30cm_6, amComp30Var_6, metaDataLst), style2) #Jun
        ws.write(7, 8, num24mos(amCurrentLST_30cm_7, amComp30Var_7, metaDataLst), style2) #Jul
        ws.write(7, 9, num24mos(amCurrentLST_30cm_8, amComp30Var_8, metaDataLst), style2) #Aug
        ws.write(7, 10, num24mos(amCurrentLST_30cm_9, amComp30Var_9, metaDataLst), style2) #Sep
        ws.write(7, 11, num24mos(amCurrentLST_30cm_10, amComp30Var_10, metaDataLst), style2) #Oct
        ws.write(7, 12, num24mos(amCurrentLST_30cm_11, amComp30Var_11, metaDataLst), style2) #Nov
        ws.write(7, 13, num24mos(amCurrentLST_30cm_12, amComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(7, 14, xlwt.Formula("SUM(C8:N8)"), style3) #Total        
        ws.write(8, 1, "# of Completed Variable AOIs 50cm 1yr (Completed this year)", style2)   
        ws.write(8, 2, num12mos(amCurrentLST_50cm_1, amComp50Var_1, metaDataLst), style2) #Jan
        ws.write(8, 3, num12mos(amCurrentLST_50cm_2, amComp50Var_2, metaDataLst), style2) #Feb
        ws.write(8, 4, num12mos(amCurrentLST_50cm_3, amComp50Var_3, metaDataLst), style2) #Mar
        ws.write(8, 5, num12mos(amCurrentLST_50cm_4, amComp50Var_4, metaDataLst), style2) #Apr
        ws.write(8, 6, num12mos(amCurrentLST_50cm_5, amComp50Var_5, metaDataLst), style2) #May
        ws.write(8, 7, num12mos(amCurrentLST_50cm_6, amComp50Var_6, metaDataLst), style2) #Jun
        ws.write(8, 8, num12mos(amCurrentLST_50cm_7, amComp50Var_7, metaDataLst), style2) #Jul
        ws.write(8, 9, num12mos(amCurrentLST_50cm_8, amComp50Var_8, metaDataLst), style2) #Aug
        ws.write(8, 10, num12mos(amCurrentLST_50cm_9, amComp50Var_9, metaDataLst), style2) #Sep
        ws.write(8, 11, num12mos(amCurrentLST_50cm_10, amComp50Var_10, metaDataLst), style2) #Oct
        ws.write(8, 12, num12mos(amCurrentLST_50cm_11, amComp50Var_11, metaDataLst), style2) #Nov
        ws.write(8, 13, num12mos(amCurrentLST_50cm_12, amComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(8, 14, xlwt.Formula("SUM(C9:N9)"), style3) #Total        
        ws.write(9, 1, "# of Completed Variable AOIs 50cm 2yr (Completed this year)", style2) 
        ws.write(9, 2, num24mos(amCurrentLST_50cm_1, amComp50Var_1, metaDataLst), style2) #Jan
        ws.write(9, 3, num24mos(amCurrentLST_50cm_2, amComp50Var_2, metaDataLst), style2) #Feb
        ws.write(9, 4, num24mos(amCurrentLST_50cm_3, amComp50Var_3, metaDataLst), style2) #Mar
        ws.write(9, 5, num24mos(amCurrentLST_50cm_4, amComp50Var_4, metaDataLst), style2) #Apr
        ws.write(9, 6, num24mos(amCurrentLST_50cm_5, amComp50Var_5, metaDataLst), style2) #May
        ws.write(9, 7, num24mos(amCurrentLST_50cm_6, amComp50Var_6, metaDataLst), style2) #Jun
        ws.write(9, 8, num24mos(amCurrentLST_50cm_7, amComp50Var_7, metaDataLst), style2) #Jul
        ws.write(9, 9, num24mos(amCurrentLST_50cm_8, amComp50Var_8, metaDataLst), style2) #Aug
        ws.write(9, 10, num24mos(amCurrentLST_50cm_9, amComp50Var_9, metaDataLst), style2) #Sep
        ws.write(9, 11, num24mos(amCurrentLST_50cm_10, amComp50Var_10, metaDataLst), style2) #Oct
        ws.write(9, 12, num24mos(amCurrentLST_50cm_11, amComp50Var_11, metaDataLst), style2) #Nov
        ws.write(9, 13, num24mos(amCurrentLST_50cm_12, amComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(9, 14, xlwt.Formula("SUM(C10:N10)"), style3) #Total         
        ws.write(10, 1, "# of AOIs In Production (Ordered)", style2)     
        ws.write(10, 2, numProduction(amProdLST, 1), style2) #Jan
        ws.write(10, 3, numProduction(amProdLST, 2), style2) #Feb
        ws.write(10, 4, numProduction(amProdLST, 3), style2) #Mar
        ws.write(10, 5, numProduction(amProdLST, 4), style2) #Apr
        ws.write(10, 6, numProduction(amProdLST, 5), style2) #May
        ws.write(10, 7, numProduction(amProdLST, 6), style2) #Jun
        ws.write(10, 8, numProduction(amProdLST, 7), style2) #Jul
        ws.write(10, 9, numProduction(amProdLST, 8), style2) #Aug
        ws.write(10, 10, numProduction(amProdLST, 9), style2) #Sep
        ws.write(10, 11, numProduction(amProdLST, 10), style2) #Oct
        ws.write(10, 12, numProduction(amProdLST, 11), style2) #Nov
        ws.write(10, 13, numProduction(amProdLST, 12), style2) #Dec    
        ws.write(10, 14, xlwt.Formula("SUM(C11:N11)"), style3) #Total        
        ws.write(11, 1, "# of AOIs Ready to Order (Fulfilled)", style2)
        ws.write(11, 2, numFulfilled(amProdLST, 1), style2) #Jan
        ws.write(11, 3, numFulfilled(amProdLST, 2), style2) #Feb
        ws.write(11, 4, numFulfilled(amProdLST, 3), style2) #Mar
        ws.write(11, 5, numFulfilled(amProdLST, 4), style2) #Apr
        ws.write(11, 6, numFulfilled(amProdLST, 5), style2) #May
        ws.write(11, 7, numFulfilled(amProdLST, 6), style2) #Jun
        ws.write(11, 8, numFulfilled(amProdLST, 7), style2) #Jul
        ws.write(11, 9, numFulfilled(amProdLST, 8), style2) #Aug
        ws.write(11, 10, numFulfilled(amProdLST, 9), style2) #Sep
        ws.write(11, 11, numFulfilled(amProdLST, 10), style2) #Oct
        ws.write(11, 12, numFulfilled(amProdLST, 11), style2) #Nov
        ws.write(11, 13, numFulfilled(amProdLST, 12), style2) #Dec    
        ws.write(11, 14, xlwt.Formula("SUM(C12:N12)"), style3) #Total         
        ws.write(12, 1, "# of Out of SLA AOIs (Not Completed, Ordered, or Fulfilled this year)", style2)
        ws.write(12, 2, numMiscNoData(amProdLST, 1), style2) #Jan
        ws.write(12, 3, numMiscNoData(amProdLST, 2), style2) #Feb
        ws.write(12, 4, numMiscNoData(amProdLST, 3), style2) #Mar
        ws.write(12, 5, numMiscNoData(amProdLST, 4), style2) #Apr
        ws.write(12, 6, numMiscNoData(amProdLST, 5), style2) #May
        ws.write(12, 7, numMiscNoData(amProdLST, 6), style2) #Jun
        ws.write(12, 8, numMiscNoData(amProdLST, 7), style2) #Jul
        ws.write(12, 9, numMiscNoData(amProdLST, 8), style2) #Aug
        ws.write(12, 10, numMiscNoData(amProdLST, 9), style2) #Sep
        ws.write(12, 11, numMiscNoData(amProdLST, 10), style2) #Oct
        ws.write(12, 12, numMiscNoData(amProdLST, 11), style2) #Nov
        ws.write(12, 13, numMiscNoData(amProdLST, 12), style2) #Dec    
        ws.write(12, 14, xlwt.Formula("SUM(C13:N13)"), style3) #Total         
        ws.write(13, 1, "    % in SLA", style2)   
        ws.write(13, 2, xlwt.Formula("SUM(C7:C10)/C4*100"), style3) #Jan
        ws.write(13, 3, xlwt.Formula("SUM(D7:D10)/D4*100"), style3) #Feb
        ws.write(13, 4, xlwt.Formula("SUM(E7:E10)/E4*100"), style3) #Mar
        ws.write(13, 5, xlwt.Formula("SUM(F7:F10)/F4*100"), style3) #Apr
        ws.write(13, 6, xlwt.Formula("SUM(G7:G10)/G4*100"), style3) #May
        ws.write(13, 7, xlwt.Formula("SUM(H7:H10)/H4*100"), style3) #Jun
        ws.write(13, 8, xlwt.Formula("SUM(I7:I10)/I4*100"), style3) #Jul
        ws.write(13, 9, xlwt.Formula("SUM(J7:J10)/J4*100"), style3) #Aug
        ws.write(13, 10, xlwt.Formula("SUM(K7:K10)/K4*100"), style3) #Sep
        ws.write(13, 11, xlwt.Formula("SUM(L7:L10)/L4*100"), style3) #Oct
        ws.write(13, 12, xlwt.Formula("SUM(M7:M10)/M4*100"), style3) #Nov
        ws.write(13, 13, xlwt.Formula("SUM(N7:N10)/N4*100"), style3) #Dec          
        ws.write(14, 1, "    % out of SLA", style2)
        ws.write(14, 2, xlwt.Formula("100-C14"), style3) #Jan
        ws.write(14, 3, xlwt.Formula("100-D14"), style3) #Feb
        ws.write(14, 4, xlwt.Formula("100-E14"), style3) #Mar
        ws.write(14, 5, xlwt.Formula("100-F14"), style3) #Apr
        ws.write(14, 6, xlwt.Formula("100-G14"), style3) #May
        ws.write(14, 7, xlwt.Formula("100-H14"), style3) #Jun
        ws.write(14, 8, xlwt.Formula("100-I14"), style3) #Jul
        ws.write(14, 9, xlwt.Formula("100-J14"), style3) #Aug
        ws.write(14, 10, xlwt.Formula("100-K14"), style3) #Sep
        ws.write(14, 11, xlwt.Formula("100-L14"), style3) #Oct
        ws.write(14, 12, xlwt.Formula("100-M14"), style3) #Nov
        ws.write(14, 13, xlwt.Formula("100-N14"), style3) #Dec       
        ws.write(15, 1, "# of 30cm Committed AOIs Rolling Off SLA", style2)
        ws.write(15, 2, numComOver12mos(amCurrentLST_30cm_C1, amComp30Com_1, metaDataLst), style2) #Jan
        ws.write(15, 3, numComOver12mos(amCurrentLST_30cm_C2, amComp30Com_2, metaDataLst), style2) #Feb
        ws.write(15, 4, numComOver12mos(amCurrentLST_30cm_C3, amComp30Com_3, metaDataLst), style2) #Mar
        ws.write(15, 5, numComOver12mos(amCurrentLST_30cm_C4, amComp30Com_4, metaDataLst), style2) #Apr
        ws.write(15, 6, numComOver12mos(amCurrentLST_30cm_C5, amComp30Com_5, metaDataLst), style2) #May
        ws.write(15, 7, numComOver12mos(amCurrentLST_30cm_C6, amComp30Com_6, metaDataLst), style2) #Jun
        ws.write(15, 8, numComOver12mos(amCurrentLST_30cm_C7, amComp30Com_7, metaDataLst), style2) #Jul
        ws.write(15, 9, numComOver12mos(amCurrentLST_30cm_C8, amComp30Com_8, metaDataLst), style2) #Aug
        ws.write(15, 10, numComOver12mos(amCurrentLST_30cm_C9, amComp30Com_9, metaDataLst), style2) #Sep
        ws.write(15, 11, numComOver12mos(amCurrentLST_30cm_C10, amComp30Com_10, metaDataLst), style2) #Oct
        ws.write(15, 12, numComOver12mos(amCurrentLST_30cm_C11, amComp30Com_11, metaDataLst), style2) #Nov
        ws.write(15, 13, numComOver12mos(amCurrentLST_30cm_C12, amComp30Com_12, metaDataLst), style2) #Dec    
        ws.write(15, 14, xlwt.Formula("SUM(C16:N16)"), style3) #Total        
        ws.write(16, 1, "# of Active AOIs (tasking on the deck)", style2)
        ws.write(16, 2, numTasking(amProdLST, 1), style2) #Jan
        ws.write(16, 3, numTasking(amProdLST, 2), style2) #Feb
        ws.write(16, 4, numTasking(amProdLST, 3), style2) #Mar
        ws.write(16, 5, numTasking(amProdLST, 4), style2) #Apr
        ws.write(16, 6, numTasking(amProdLST, 5), style2) #May
        ws.write(16, 7, numTasking(amProdLST, 6), style2) #Jun
        ws.write(16, 8, numTasking(amProdLST, 7), style2) #Jul
        ws.write(16, 9, numTasking(amProdLST, 8), style2) #Aug
        ws.write(16, 10, numTasking(amProdLST, 9), style2) #Sep
        ws.write(16, 11, numTasking(amProdLST, 10), style2) #Oct
        ws.write(16, 12, numTasking(amProdLST, 11), style2) #Nov
        ws.write(16, 13, numTasking(amProdLST, 12), style2) #Dec    
        ws.write(16, 14, xlwt.Formula("SUM(C17:N17)"), style3) #Total
        ws.write(18, 0, "Totals", style0)
        ws.write(18, 1, "Delta target within SLA", style2)
        ws.write(18, 2, xlwt.Formula("SUM(C7:C10)"), style2) #Jan
        ws.write(18, 3, xlwt.Formula("SUM(D7:D10)"), style2) #Feb
        ws.write(18, 4, xlwt.Formula("SUM(E7:E10)"), style2) #Mar
        ws.write(18, 5, xlwt.Formula("SUM(F7:F10)"), style2) #Apr
        ws.write(18, 6, xlwt.Formula("SUM(G7:G10)"), style2) #May
        ws.write(18, 7, xlwt.Formula("SUM(H7:H10)"), style2) #Jun
        ws.write(18, 8, xlwt.Formula("SUM(I7:I10)"), style2) #Jul
        ws.write(18, 9, xlwt.Formula("SUM(J7:J10)"), style2) #Aug
        ws.write(18, 10, xlwt.Formula("SUM(K7:K10)"), style2) #Sep
        ws.write(18, 11, xlwt.Formula("SUM(L7:L10)"), style2) #Oct
        ws.write(18, 12, xlwt.Formula("SUM(M7:M10)"), style2) #Nov
        ws.write(18, 13, xlwt.Formula("SUM(N7:N10)"), style2) #Dec
        ws.write(18, 14, xlwt.Formula("SUM(C19:N19)"), style3) #Total 
        ws.write(19, 1, "Total expired AOIs", style2)
        ws.write(19, 2, xlwt.Formula("MAX(0,C4-C19)"), style2) #Jan
        ws.write(19, 3, xlwt.Formula("MAX(0,D4-D19)"), style2) #Feb
        ws.write(19, 4, xlwt.Formula("MAX(0,E4-E19)"), style2) #Mar
        ws.write(19, 5, xlwt.Formula("MAX(0,F4-F19)"), style2) #Apr
        ws.write(19, 6, xlwt.Formula("MAX(0,G4-G19)"), style2) #May
        ws.write(19, 7, xlwt.Formula("MAX(0,H4-H19)"), style2) #Jun
        ws.write(19, 8, xlwt.Formula("MAX(0,I4-I19)"), style2) #Jul
        ws.write(19, 9, xlwt.Formula("MAX(0,J4-J19)"), style2) #Aug
        ws.write(19, 10, xlwt.Formula("MAX(0,K4-K19)"), style2) #Sep
        ws.write(19, 11, xlwt.Formula("MAX(0,L4-L19)"), style2) #Oct
        ws.write(19, 12, xlwt.Formula("MAX(0,M4-M19)"), style2) #Nov
        ws.write(19, 13, xlwt.Formula("MAX(0,N4-N19)"), style2) #Dec
        ws.write(19, 14, xlwt.Formula("SUM(C20:N20)"), style3) #Total         
        
        #Second Header: EAST ASIA -- EA
        ws.write(21, 0, "East Asia", style0)
        ws.write(21, 1, "# of AOIs", style2)
        ws.write(21, 2, numAOIs(eaAOIs, 1), style2) #Jan
        ws.write(21, 3, numAOIs(eaAOIs, 2), style2) #Feb
        ws.write(21, 4, numAOIs(eaAOIs, 3), style2) #Mar
        ws.write(21, 5, numAOIs(eaAOIs, 4), style2) #Apr
        ws.write(21, 6, numAOIs(eaAOIs, 5), style2) #May
        ws.write(21, 7, numAOIs(eaAOIs, 6), style2) #Jun
        ws.write(21, 8, numAOIs(eaAOIs, 7), style2) #Jul
        ws.write(21, 9, numAOIs(eaAOIs, 8), style2) #Aug
        ws.write(21, 10, numAOIs(eaAOIs, 9), style2) #Sep
        ws.write(21, 11, numAOIs(eaAOIs, 10), style2) #Oct
        ws.write(21, 12, numAOIs(eaAOIs, 11), style2) #Nov
        ws.write(21, 13, numAOIs(eaAOIs, 12), style2) #Dec
        ws.write(21, 14, xlwt.Formula("SUM(C22:N22)"), style3) #Total
        ws.write(22, 1, "# of Completed AOIs (Completed this year)", style2)
        ws.write(22, 2, numComplete(eaCompLST, 1), style2) #Jan
        ws.write(22, 3, numComplete(eaCompLST, 2), style2) #Feb
        ws.write(22, 4, numComplete(eaCompLST, 3), style2) #Mar
        ws.write(22, 5, numComplete(eaCompLST, 4), style2) #Apr
        ws.write(22, 6, numComplete(eaCompLST, 5), style2) #May
        ws.write(22, 7, numComplete(eaCompLST, 6), style2) #Jun
        ws.write(22, 8, numComplete(eaCompLST, 7), style2) #Jul
        ws.write(22, 9, numComplete(eaCompLST, 8), style2) #Aug
        ws.write(22, 10, numComplete(eaCompLST, 9), style2) #Sep
        ws.write(22, 11, numComplete(eaCompLST, 10), style2) #Oct
        ws.write(22, 12, numComplete(eaCompLST, 11), style2) #Nov
        ws.write(22, 13, numComplete(eaCompLST, 12), style2) #Dec       
        ws.write(22, 14, xlwt.Formula("SUM(C23:N23)"), style3) #Total
        ws.write(23, 1, "# of Completed 30cm Committed AOIs (Completed this year)", style2)
        ws.write(23, 2, numComplete30cmCom(eaProdLST, 1), style2) #Jan
        ws.write(23, 3, numComplete30cmCom(eaProdLST, 2), style2) #Feb
        ws.write(23, 4, numComplete30cmCom(eaProdLST, 3), style2) #Mar
        ws.write(23, 5, numComplete30cmCom(eaProdLST, 4), style2) #Apr
        ws.write(23, 6, numComplete30cmCom(eaProdLST, 5), style2) #May
        ws.write(23, 7, numComplete30cmCom(eaProdLST, 6), style2) #Jun
        ws.write(23, 8, numComplete30cmCom(eaProdLST, 7), style2) #Jul
        ws.write(23, 9, numComplete30cmCom(eaProdLST, 8), style2) #Aug
        ws.write(23, 10, numComplete30cmCom(eaProdLST, 9), style2) #Sep
        ws.write(23, 11, numComplete30cmCom(eaProdLST, 10), style2) #Oct
        ws.write(23, 12, numComplete30cmCom(eaProdLST, 11), style2) #Nov
        ws.write(23, 13, numComplete30cmCom(eaProdLST, 12), style2) #Dec    
        ws.write(23, 14, xlwt.Formula("SUM(C24:N24)"), style3) #Total
        ws.write(24, 1, "# of Completed Variable AOIs 30cm 1yr (Completed this year)", style2)
        ws.write(24, 2, num12mos(eaCurrentLST_30cm_1, eaComp30Var_1, metaDataLst), style2) #Jan
        ws.write(24, 3, num12mos(eaCurrentLST_30cm_2, eaComp30Var_2, metaDataLst), style2) #Feb
        ws.write(24, 4, num12mos(eaCurrentLST_30cm_3, eaComp30Var_3, metaDataLst), style2) #Mar
        ws.write(24, 5, num12mos(eaCurrentLST_30cm_4, eaComp30Var_4, metaDataLst), style2) #Apr
        ws.write(24, 6, num12mos(eaCurrentLST_30cm_5, eaComp30Var_5, metaDataLst), style2) #May
        ws.write(24, 7, num12mos(eaCurrentLST_30cm_6, eaComp30Var_6, metaDataLst), style2) #Jun
        ws.write(24, 8, num12mos(eaCurrentLST_30cm_7, eaComp30Var_7, metaDataLst), style2) #Jul
        ws.write(24, 9, num12mos(eaCurrentLST_30cm_8, eaComp30Var_8, metaDataLst), style2) #Aug
        ws.write(24, 10, num12mos(eaCurrentLST_30cm_9, eaComp30Var_9, metaDataLst), style2) #Sep
        ws.write(24, 11, num12mos(eaCurrentLST_30cm_10, eaComp30Var_10, metaDataLst), style2) #Oct
        ws.write(24, 12, num12mos(eaCurrentLST_30cm_11, eaComp30Var_11, metaDataLst), style2) #Nov
        ws.write(24, 13, num12mos(eaCurrentLST_30cm_12, eaComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(24, 14, xlwt.Formula("SUM(C25:N25)"), style3) #Total
        ws.write(25, 1, "# of Completed Variable AOIs 30cm 2yr (Completed this year)", style2)
        ws.write(25, 2, num24mos(eaCurrentLST_30cm_1, eaComp30Var_1, metaDataLst), style2) #Jan
        ws.write(25, 3, num24mos(eaCurrentLST_30cm_2, eaComp30Var_2, metaDataLst), style2) #Feb
        ws.write(25, 4, num24mos(eaCurrentLST_30cm_3, eaComp30Var_3, metaDataLst), style2) #Mar
        ws.write(25, 5, num24mos(eaCurrentLST_30cm_4, eaComp30Var_4, metaDataLst), style2) #Apr
        ws.write(25, 6, num24mos(eaCurrentLST_30cm_5, eaComp30Var_5, metaDataLst), style2) #May
        ws.write(25, 7, num24mos(eaCurrentLST_30cm_6, eaComp30Var_6, metaDataLst), style2) #Jun
        ws.write(25, 8, num24mos(eaCurrentLST_30cm_7, eaComp30Var_7, metaDataLst), style2) #Jul
        ws.write(25, 9, num24mos(eaCurrentLST_30cm_8, eaComp30Var_8, metaDataLst), style2) #Aug
        ws.write(25, 10, num24mos(eaCurrentLST_30cm_9, eaComp30Var_9, metaDataLst), style2) #Sep
        ws.write(25, 11, num24mos(eaCurrentLST_30cm_10, eaComp30Var_10, metaDataLst), style2) #Oct
        ws.write(25, 12, num24mos(eaCurrentLST_30cm_11, eaComp30Var_11, metaDataLst), style2) #Nov
        ws.write(25, 13, num24mos(eaCurrentLST_30cm_12, eaComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(25, 14, xlwt.Formula("SUM(C26:N26)"), style3) #Total        
        ws.write(26, 1, "# of Completed Variable AOIs 50cm 1yr (Completed this year)", style2)   
        ws.write(26, 2, num12mos(eaCurrentLST_50cm_1, eaComp50Var_1, metaDataLst), style2) #Jan
        ws.write(26, 3, num12mos(eaCurrentLST_50cm_2, eaComp50Var_2, metaDataLst), style2) #Feb
        ws.write(26, 4, num12mos(eaCurrentLST_50cm_3, eaComp50Var_3, metaDataLst), style2) #Mar
        ws.write(26, 5, num12mos(eaCurrentLST_50cm_4, eaComp50Var_4, metaDataLst), style2) #Apr
        ws.write(26, 6, num12mos(eaCurrentLST_50cm_5, eaComp50Var_5, metaDataLst), style2) #May
        ws.write(26, 7, num12mos(eaCurrentLST_50cm_6, eaComp50Var_6, metaDataLst), style2) #Jun
        ws.write(26, 8, num12mos(eaCurrentLST_50cm_7, eaComp50Var_7, metaDataLst), style2) #Jul
        ws.write(26, 9, num12mos(eaCurrentLST_50cm_8, eaComp50Var_8, metaDataLst), style2) #Aug
        ws.write(26, 10, num12mos(eaCurrentLST_50cm_9, eaComp50Var_9, metaDataLst), style2) #Sep
        ws.write(26, 11, num12mos(eaCurrentLST_50cm_10, eaComp50Var_10, metaDataLst), style2) #Oct
        ws.write(26, 12, num12mos(eaCurrentLST_50cm_11, eaComp50Var_11, metaDataLst), style2) #Nov
        ws.write(26, 13, num12mos(eaCurrentLST_50cm_12, eaComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(26, 14, xlwt.Formula("SUM(C27:N27)"), style3) #Total        
        ws.write(27, 1, "# of Completed Variable AOIs 50cm 2yr (Completed this year)", style2) 
        ws.write(27, 2, num24mos(eaCurrentLST_50cm_1, eaComp50Var_1, metaDataLst), style2) #Jan
        ws.write(27, 3, num24mos(eaCurrentLST_50cm_2, eaComp50Var_2, metaDataLst), style2) #Feb
        ws.write(27, 4, num24mos(eaCurrentLST_50cm_3, eaComp50Var_3, metaDataLst), style2) #Mar
        ws.write(27, 5, num24mos(eaCurrentLST_50cm_4, eaComp50Var_4, metaDataLst), style2) #Apr
        ws.write(27, 6, num24mos(eaCurrentLST_50cm_5, eaComp50Var_5, metaDataLst), style2) #May
        ws.write(27, 7, num24mos(eaCurrentLST_50cm_6, eaComp50Var_6, metaDataLst), style2) #Jun
        ws.write(27, 8, num24mos(eaCurrentLST_50cm_7, eaComp50Var_7, metaDataLst), style2) #Jul
        ws.write(27, 9, num24mos(eaCurrentLST_50cm_8, eaComp50Var_8, metaDataLst), style2) #Aug
        ws.write(27, 10, num24mos(eaCurrentLST_50cm_9, eaComp50Var_9, metaDataLst), style2) #Sep
        ws.write(27, 11, num24mos(eaCurrentLST_50cm_10, eaComp50Var_10, metaDataLst), style2) #Oct
        ws.write(27, 12, num24mos(eaCurrentLST_50cm_11, eaComp50Var_11, metaDataLst), style2) #Nov
        ws.write(27, 13, num24mos(eaCurrentLST_50cm_12, eaComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(27, 14, xlwt.Formula("SUM(C28:N28)"), style3) #Total         
        ws.write(28, 1, "# of AOIs In Production (Ordered)", style2)     
        ws.write(28, 2, numProduction(eaProdLST, 1), style2) #Jan
        ws.write(28, 3, numProduction(eaProdLST, 2), style2) #Feb
        ws.write(28, 4, numProduction(eaProdLST, 3), style2) #Mar
        ws.write(28, 5, numProduction(eaProdLST, 4), style2) #Apr
        ws.write(28, 6, numProduction(eaProdLST, 5), style2) #May
        ws.write(28, 7, numProduction(eaProdLST, 6), style2) #Jun
        ws.write(28, 8, numProduction(eaProdLST, 7), style2) #Jul
        ws.write(28, 9, numProduction(eaProdLST, 8), style2) #Aug
        ws.write(28, 10, numProduction(eaProdLST, 9), style2) #Sep
        ws.write(28, 11, numProduction(eaProdLST, 10), style2) #Oct
        ws.write(28, 12, numProduction(eaProdLST, 11), style2) #Nov
        ws.write(28, 13, numProduction(eaProdLST, 12), style2) #Dec    
        ws.write(28, 14, xlwt.Formula("SUM(C29:N29)"), style3) #Total        
        ws.write(29, 1, "# of AOIs Ready to Order (Fulfilled)", style2)
        ws.write(29, 2, numFulfilled(eaProdLST, 1), style2) #Jan
        ws.write(29, 3, numFulfilled(eaProdLST, 2), style2) #Feb
        ws.write(29, 4, numFulfilled(eaProdLST, 3), style2) #Mar
        ws.write(29, 5, numFulfilled(eaProdLST, 4), style2) #Apr
        ws.write(29, 6, numFulfilled(eaProdLST, 5), style2) #May
        ws.write(29, 7, numFulfilled(eaProdLST, 6), style2) #Jun
        ws.write(29, 8, numFulfilled(eaProdLST, 7), style2) #Jul
        ws.write(29, 9, numFulfilled(eaProdLST, 8), style2) #Aug
        ws.write(29, 10, numFulfilled(eaProdLST, 9), style2) #Sep
        ws.write(29, 11, numFulfilled(eaProdLST, 10), style2) #Oct
        ws.write(29, 12, numFulfilled(eaProdLST, 11), style2) #Nov
        ws.write(29, 13, numFulfilled(eaProdLST, 12), style2) #Dec    
        ws.write(29, 14, xlwt.Formula("SUM(C30:N30)"), style3) #Total         
        ws.write(30, 1, "# of Out of SLA AOIs (Not Completed, Ordered, or Fulfilled this year)", style2)
        ws.write(30, 2, numMiscNoData(eaProdLST, 1), style2) #Jan
        ws.write(30, 3, numMiscNoData(eaProdLST, 2), style2) #Feb
        ws.write(30, 4, numMiscNoData(eaProdLST, 3), style2) #Mar
        ws.write(30, 5, numMiscNoData(eaProdLST, 4), style2) #Apr
        ws.write(30, 6, numMiscNoData(eaProdLST, 5), style2) #May
        ws.write(30, 7, numMiscNoData(eaProdLST, 6), style2) #Jun
        ws.write(30, 8, numMiscNoData(eaProdLST, 7), style2) #Jul
        ws.write(30, 9, numMiscNoData(eaProdLST, 8), style2) #Aug
        ws.write(30, 10, numMiscNoData(eaProdLST, 9), style2) #Sep
        ws.write(30, 11, numMiscNoData(eaProdLST, 10), style2) #Oct
        ws.write(30, 12, numMiscNoData(eaProdLST, 11), style2) #Nov
        ws.write(30, 13, numMiscNoData(eaProdLST, 12), style2) #Dec    
        ws.write(30, 14, xlwt.Formula("SUM(C31:N31)"), style3) #Total         
        ws.write(31, 1, "    % in SLA", style2)   
        ws.write(31, 2, xlwt.Formula("SUM(C7:C10)/C4*100"), style3) #Jan
        ws.write(31, 3, xlwt.Formula("SUM(D7:D10)/D4*100"), style3) #Feb
        ws.write(31, 4, xlwt.Formula("SUM(E7:E10)/E4*100"), style3) #Mar
        ws.write(31, 5, xlwt.Formula("SUM(F7:F10)/F4*100"), style3) #Apr
        ws.write(31, 6, xlwt.Formula("SUM(G7:G10)/G4*100"), style3) #May
        ws.write(31, 7, xlwt.Formula("SUM(H7:H10)/H4*100"), style3) #Jun
        ws.write(31, 8, xlwt.Formula("SUM(I7:I10)/I4*100"), style3) #Jul
        ws.write(31, 9, xlwt.Formula("SUM(J7:J10)/J4*100"), style3) #Aug
        ws.write(31, 10, xlwt.Formula("SUM(K7:K10)/K4*100"), style3) #Sep
        ws.write(31, 11, xlwt.Formula("SUM(L7:L10)/L4*100"), style3) #Oct
        ws.write(31, 12, xlwt.Formula("SUM(M7:M10)/M4*100"), style3) #Nov
        ws.write(31, 13, xlwt.Formula("SUM(N7:N10)/N4*100"), style3) #Dec        
        ws.write(32, 1, "    % out of SLA", style2)
        ws.write(32, 2, xlwt.Formula("100-C14"), style3) #Jan
        ws.write(32, 3, xlwt.Formula("100-D14"), style3) #Feb
        ws.write(32, 4, xlwt.Formula("100-E14"), style3) #Mar
        ws.write(32, 5, xlwt.Formula("100-F14"), style3) #Apr
        ws.write(32, 6, xlwt.Formula("100-G14"), style3) #May
        ws.write(32, 7, xlwt.Formula("100-H14"), style3) #Jun
        ws.write(32, 8, xlwt.Formula("100-I14"), style3) #Jul
        ws.write(32, 9, xlwt.Formula("100-J14"), style3) #Aug
        ws.write(32, 10, xlwt.Formula("100-K14"), style3) #Sep
        ws.write(32, 11, xlwt.Formula("100-L14"), style3) #Oct
        ws.write(32, 12, xlwt.Formula("100-M14"), style3) #Nov
        ws.write(32, 13, xlwt.Formula("100-N14"), style3) #Dec            
        ws.write(33, 1, "# of 30cm Committed AOIs Rolling Off SLA", style2)
        ws.write(33, 2, numComOver12mos(eaCurrentLST_30cm_C1, eaComp30Com_1, metaDataLst), style2) #Jan
        ws.write(33, 3, numComOver12mos(eaCurrentLST_30cm_C2, eaComp30Com_2, metaDataLst), style2) #Feb
        ws.write(33, 4, numComOver12mos(eaCurrentLST_30cm_C3, eaComp30Com_3, metaDataLst), style2) #Mar
        ws.write(33, 5, numComOver12mos(eaCurrentLST_30cm_C4, eaComp30Com_4, metaDataLst), style2) #Apr
        ws.write(33, 6, numComOver12mos(eaCurrentLST_30cm_C5, eaComp30Com_5, metaDataLst), style2) #May
        ws.write(33, 7, numComOver12mos(eaCurrentLST_30cm_C6, eaComp30Com_6, metaDataLst), style2) #Jun
        ws.write(33, 8, numComOver12mos(eaCurrentLST_30cm_C7, eaComp30Com_7, metaDataLst), style2) #Jul
        ws.write(33, 9, numComOver12mos(eaCurrentLST_30cm_C8, eaComp30Com_8, metaDataLst), style2) #Aug
        ws.write(33, 10, numComOver12mos(eaCurrentLST_30cm_C9, eaComp30Com_9, metaDataLst), style2) #Sep
        ws.write(33, 11, numComOver12mos(eaCurrentLST_30cm_C10, eaComp30Com_10, metaDataLst), style2) #Oct
        ws.write(33, 12, numComOver12mos(eaCurrentLST_30cm_C11, eaComp30Com_11, metaDataLst), style2) #Nov
        ws.write(33, 13, numComOver12mos(eaCurrentLST_30cm_C12, eaComp30Com_12, metaDataLst), style2) #Dec    
        ws.write(33, 14, xlwt.Formula("SUM(C34:N34)"), style3) #Total        
        ws.write(34, 1, "# of Active AOIs (tasking on the deck)", style2)
        ws.write(34, 2, numTasking(eaProdLST, 1), style2) #Jan
        ws.write(34, 3, numTasking(eaProdLST, 2), style2) #Feb
        ws.write(34, 4, numTasking(eaProdLST, 3), style2) #Mar
        ws.write(34, 5, numTasking(eaProdLST, 4), style2) #Apr
        ws.write(34, 6, numTasking(eaProdLST, 5), style2) #May
        ws.write(34, 7, numTasking(eaProdLST, 6), style2) #Jun
        ws.write(34, 8, numTasking(eaProdLST, 7), style2) #Jul
        ws.write(34, 9, numTasking(eaProdLST, 8), style2) #Aug
        ws.write(34, 10, numTasking(eaProdLST, 9), style2) #Sep
        ws.write(34, 11, numTasking(eaProdLST, 10), style2) #Oct
        ws.write(34, 12, numTasking(eaProdLST, 11), style2) #Nov
        ws.write(34, 13, numTasking(eaProdLST, 12), style2) #Dec    
        ws.write(34, 14, xlwt.Formula("SUM(C35:N35)"), style3) #Total
        ws.write(36, 0, "Totals", style0)
        ws.write(36, 1, "Delta target within SLA", style2)
        ws.write(36, 2, xlwt.Formula("SUM(C25:C28)"), style3) #Jan
        ws.write(36, 3, xlwt.Formula("SUM(D25:D28)"), style3) #Feb
        ws.write(36, 4, xlwt.Formula("SUM(E25:E28)"), style3) #Mar
        ws.write(36, 5, xlwt.Formula("SUM(F25:F28)"), style3) #Apr
        ws.write(36, 6, xlwt.Formula("SUM(G25:G28)"), style3) #May
        ws.write(36, 7, xlwt.Formula("SUM(H25:H28)"), style3) #Jun
        ws.write(36, 8, xlwt.Formula("SUM(I25:I28)"), style3) #Jul
        ws.write(36, 9, xlwt.Formula("SUM(J25:J28)"), style3) #Aug
        ws.write(36, 10, xlwt.Formula("SUM(K25:K28)"), style3) #Sep
        ws.write(36, 11, xlwt.Formula("SUM(L25:L28)"), style3) #Oct
        ws.write(36, 12, xlwt.Formula("SUM(M25:M28)"), style3) #Nov
        ws.write(36, 13, xlwt.Formula("SUM(N25:N28)"), style3) #Dec
        ws.write(36, 14, xlwt.Formula("SUM(C37:N37)"), style3) #Total         
        ws.write(37, 1, "Total expired AOIs", style2)       
        ws.write(37, 2, xlwt.Formula("MAX(0,C22-C37)"), style3) #Jan
        ws.write(37, 3, xlwt.Formula("MAX(0,D22-D37)"), style3) #Feb
        ws.write(37, 4, xlwt.Formula("MAX(0,E22-E37)"), style3) #Mar
        ws.write(37, 5, xlwt.Formula("MAX(0,F22-F37)"), style3) #Apr
        ws.write(37, 6, xlwt.Formula("MAX(0,G22-G37)"), style3) #May
        ws.write(37, 7, xlwt.Formula("MAX(0,H22-H37)"), style3) #Jun
        ws.write(37, 8, xlwt.Formula("MAX(0,I22-I37)"), style3) #Jul
        ws.write(37, 9, xlwt.Formula("MAX(0,J22-J37)"), style3) #Aug
        ws.write(37, 10, xlwt.Formula("MAX(0,K22-K37)"), style3) #Sep
        ws.write(37, 11, xlwt.Formula("MAX(0,L22-L37)"), style3) #Oct
        ws.write(37, 12, xlwt.Formula("MAX(0,M22-M37)"), style3) #Nov
        ws.write(37, 13, xlwt.Formula("MAX(0,N22-N37)"), style3) #Dec
        ws.write(37, 14, xlwt.Formula("SUM(C38:N38)"), style3) #Total                 
        
        #Third Header: EUROPE / W AFRICA -- EU
        ws.write(39, 0, "Europe / W Africa", style0)
        ws.write(39, 1, "# of AOIs", style2)
        ws.write(39, 2, numAOIs(euAOIs, 1), style2) #Jan
        ws.write(39, 3, numAOIs(euAOIs, 2), style2) #Feb
        ws.write(39, 4, numAOIs(euAOIs, 3), style2) #Mar
        ws.write(39, 5, numAOIs(euAOIs, 4), style2) #Apr
        ws.write(39, 6, numAOIs(euAOIs, 5), style2) #May
        ws.write(39, 7, numAOIs(euAOIs, 6), style2) #Jun
        ws.write(39, 8, numAOIs(euAOIs, 7), style2) #Jul
        ws.write(39, 9, numAOIs(euAOIs, 8), style2) #Aug
        ws.write(39, 10, numAOIs(euAOIs, 9), style2) #Sep
        ws.write(39, 11, numAOIs(euAOIs, 10), style2) #Oct
        ws.write(39, 12, numAOIs(euAOIs, 11), style2) #Nov
        ws.write(39, 13, numAOIs(euAOIs, 12), style2) #Dec
        ws.write(39, 14, xlwt.Formula("SUM(C40:N40)"), style3) #Total
        ws.write(40, 1, "# of Completed AOIs (Completed this year)", style2)
        ws.write(40, 2, numComplete(euCompLST, 1), style2) #Jan
        ws.write(40, 3, numComplete(euCompLST, 2), style2) #Feb
        ws.write(40, 4, numComplete(euCompLST, 3), style2) #Mar
        ws.write(40, 5, numComplete(euCompLST, 4), style2) #Apr
        ws.write(40, 6, numComplete(euCompLST, 5), style2) #May
        ws.write(40, 7, numComplete(euCompLST, 6), style2) #Jun
        ws.write(40, 8, numComplete(euCompLST, 7), style2) #Jul
        ws.write(40, 9, numComplete(euCompLST, 8), style2) #Aug
        ws.write(40, 10, numComplete(euCompLST, 9), style2) #Sep
        ws.write(40, 11, numComplete(euCompLST, 10), style2) #Oct
        ws.write(40, 12, numComplete(euCompLST, 11), style2) #Nov
        ws.write(40, 13, numComplete(euCompLST, 12), style2) #Dec       
        ws.write(40, 14, xlwt.Formula("SUM(C41:N41)"), style3) #Total
        ws.write(41, 1, "# of Completed 30cm Committed AOIs (Completed this year)", style2)
        ws.write(41, 2, numComplete30cmCom(euProdLST, 1), style2) #Jan
        ws.write(41, 3, numComplete30cmCom(euProdLST, 2), style2) #Feb
        ws.write(41, 4, numComplete30cmCom(euProdLST, 3), style2) #Mar
        ws.write(41, 5, numComplete30cmCom(euProdLST, 4), style2) #Apr
        ws.write(41, 6, numComplete30cmCom(euProdLST, 5), style2) #May
        ws.write(41, 7, numComplete30cmCom(euProdLST, 6), style2) #Jun
        ws.write(41, 8, numComplete30cmCom(euProdLST, 7), style2) #Jul
        ws.write(41, 9, numComplete30cmCom(euProdLST, 8), style2) #Aug
        ws.write(41, 10, numComplete30cmCom(euProdLST, 9), style2) #Sep
        ws.write(41, 11, numComplete30cmCom(euProdLST, 10), style2) #Oct
        ws.write(41, 12, numComplete30cmCom(euProdLST, 11), style2) #Nov
        ws.write(41, 13, numComplete30cmCom(euProdLST, 12), style2) #Dec    
        ws.write(41, 14, xlwt.Formula("SUM(C42:N42)"), style3) #Total
        ws.write(42, 1, "# of Completed Variable AOIs 30cm 1yr (Completed this year)", style2)
        ws.write(42, 2, num12mos(euCurrentLST_30cm_1, euComp30Var_1, metaDataLst), style2) #Jan
        ws.write(42, 3, num12mos(euCurrentLST_30cm_2, euComp30Var_2, metaDataLst), style2) #Feb
        ws.write(42, 4, num12mos(euCurrentLST_30cm_3, euComp30Var_3, metaDataLst), style2) #Mar
        ws.write(42, 5, num12mos(euCurrentLST_30cm_4, euComp30Var_4, metaDataLst), style2) #Apr
        ws.write(42, 6, num12mos(euCurrentLST_30cm_5, euComp30Var_5, metaDataLst), style2) #May
        ws.write(42, 7, num12mos(euCurrentLST_30cm_6, euComp30Var_6, metaDataLst), style2) #Jun
        ws.write(42, 8, num12mos(euCurrentLST_30cm_7, euComp30Var_7, metaDataLst), style2) #Jul
        ws.write(42, 9, num12mos(euCurrentLST_30cm_8, euComp30Var_8, metaDataLst), style2) #Aug
        ws.write(42, 10, num12mos(euCurrentLST_30cm_9, euComp30Var_9, metaDataLst), style2) #Sep
        ws.write(42, 11, num12mos(euCurrentLST_30cm_10, euComp30Var_10, metaDataLst), style2) #Oct
        ws.write(42, 12, num12mos(euCurrentLST_30cm_11, euComp30Var_11, metaDataLst), style2) #Nov
        ws.write(42, 13, num12mos(euCurrentLST_30cm_12, euComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(42, 14, xlwt.Formula("SUM(C43:N43)"), style3) #Total
        ws.write(43, 1, "# of Completed Variable AOIs 30cm 2yr (Completed this year)", style2)
        ws.write(43, 2, num24mos(euCurrentLST_30cm_1, euComp30Var_1, metaDataLst), style2) #Jan
        ws.write(43, 3, num24mos(euCurrentLST_30cm_2, euComp30Var_2, metaDataLst), style2) #Feb
        ws.write(43, 4, num24mos(euCurrentLST_30cm_3, euComp30Var_3, metaDataLst), style2) #Mar
        ws.write(43, 5, num24mos(euCurrentLST_30cm_4, euComp30Var_4, metaDataLst), style2) #Apr
        ws.write(43, 6, num24mos(euCurrentLST_30cm_5, euComp30Var_5, metaDataLst), style2) #May
        ws.write(43, 7, num24mos(euCurrentLST_30cm_6, euComp30Var_6, metaDataLst), style2) #Jun
        ws.write(43, 8, num24mos(euCurrentLST_30cm_7, euComp30Var_7, metaDataLst), style2) #Jul
        ws.write(43, 9, num24mos(euCurrentLST_30cm_8, euComp30Var_8, metaDataLst), style2) #Aug
        ws.write(43, 10, num24mos(euCurrentLST_30cm_9, euComp30Var_9, metaDataLst), style2) #Sep
        ws.write(43, 11, num24mos(euCurrentLST_30cm_10, euComp30Var_10, metaDataLst), style2) #Oct
        ws.write(43, 12, num24mos(euCurrentLST_30cm_11, euComp30Var_11, metaDataLst), style2) #Nov
        ws.write(43, 13, num24mos(euCurrentLST_30cm_12, euComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(43, 14, xlwt.Formula("SUM(C44:N44)"), style3) #Total        
        ws.write(44, 1, "# of Completed Variable AOIs 50cm 1yr (Completed this year)", style2)   
        ws.write(44, 2, num12mos(euCurrentLST_50cm_1, euComp50Var_1, metaDataLst), style2) #Jan
        ws.write(44, 3, num12mos(euCurrentLST_50cm_2, euComp50Var_2, metaDataLst), style2) #Feb
        ws.write(44, 4, num12mos(euCurrentLST_50cm_3, euComp50Var_3, metaDataLst), style2) #Mar
        ws.write(44, 5, num12mos(euCurrentLST_50cm_4, euComp50Var_4, metaDataLst), style2) #Apr
        ws.write(44, 6, num12mos(euCurrentLST_50cm_5, euComp50Var_5, metaDataLst), style2) #May
        ws.write(44, 7, num12mos(euCurrentLST_50cm_6, euComp50Var_6, metaDataLst), style2) #Jun
        ws.write(44, 8, num12mos(euCurrentLST_50cm_7, euComp50Var_7, metaDataLst), style2) #Jul
        ws.write(44, 9, num12mos(euCurrentLST_50cm_8, euComp50Var_8, metaDataLst), style2) #Aug
        ws.write(44, 10, num12mos(euCurrentLST_50cm_9, euComp50Var_9, metaDataLst), style2) #Sep
        ws.write(44, 11, num12mos(euCurrentLST_50cm_10, euComp50Var_10, metaDataLst), style2) #Oct
        ws.write(44, 12, num12mos(euCurrentLST_50cm_11, euComp50Var_11, metaDataLst), style2) #Nov
        ws.write(44, 13, num12mos(euCurrentLST_50cm_12, euComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(44, 14, xlwt.Formula("SUM(C45:N45)"), style3) #Total        
        ws.write(45, 1, "# of Completed Variable AOIs 50cm 2yr (Completed this year)", style2) 
        ws.write(45, 2, num24mos(euCurrentLST_50cm_1, euComp50Var_1, metaDataLst), style2) #Jan
        ws.write(45, 3, num24mos(euCurrentLST_50cm_2, euComp50Var_2, metaDataLst), style2) #Feb
        ws.write(45, 4, num24mos(euCurrentLST_50cm_3, euComp50Var_3, metaDataLst), style2) #Mar
        ws.write(45, 5, num24mos(euCurrentLST_50cm_4, euComp50Var_4, metaDataLst), style2) #Apr
        ws.write(45, 6, num24mos(euCurrentLST_50cm_5, euComp50Var_5, metaDataLst), style2) #May
        ws.write(45, 7, num24mos(euCurrentLST_50cm_6, euComp50Var_6, metaDataLst), style2) #Jun
        ws.write(45, 8, num24mos(euCurrentLST_50cm_7, euComp50Var_7, metaDataLst), style2) #Jul
        ws.write(45, 9, num24mos(euCurrentLST_50cm_8, euComp50Var_8, metaDataLst), style2) #Aug
        ws.write(45, 10, num24mos(euCurrentLST_50cm_9, euComp50Var_9, metaDataLst), style2) #Sep
        ws.write(45, 11, num24mos(euCurrentLST_50cm_10, euComp50Var_10, metaDataLst), style2) #Oct
        ws.write(45, 12, num24mos(euCurrentLST_50cm_11, euComp50Var_11, metaDataLst), style2) #Nov
        ws.write(45, 13, num24mos(euCurrentLST_50cm_12, euComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(45, 14, xlwt.Formula("SUM(C46:N46)"), style3) #Total         
        ws.write(46, 1, "# of AOIs In Production (Ordered)", style2)     
        ws.write(46, 2, numProduction(euProdLST, 1), style2) #Jan
        ws.write(46, 3, numProduction(euProdLST, 2), style2) #Feb
        ws.write(46, 4, numProduction(euProdLST, 3), style2) #Mar
        ws.write(46, 5, numProduction(euProdLST, 4), style2) #Apr
        ws.write(46, 6, numProduction(euProdLST, 5), style2) #May
        ws.write(46, 7, numProduction(euProdLST, 6), style2) #Jun
        ws.write(46, 8, numProduction(euProdLST, 7), style2) #Jul
        ws.write(46, 9, numProduction(euProdLST, 8), style2) #Aug
        ws.write(46, 10, numProduction(euProdLST, 9), style2) #Sep
        ws.write(46, 11, numProduction(euProdLST, 10), style2) #Oct
        ws.write(46, 12, numProduction(euProdLST, 11), style2) #Nov
        ws.write(46, 13, numProduction(euProdLST, 12), style2) #Dec    
        ws.write(46, 14, xlwt.Formula("SUM(C47:N47)"), style3) #Total        
        ws.write(47, 1, "# of AOIs Ready to Order (Fulfilled)", style2)
        ws.write(47, 2, numFulfilled(euProdLST, 1), style2) #Jan
        ws.write(47, 3, numFulfilled(euProdLST, 2), style2) #Feb
        ws.write(47, 4, numFulfilled(euProdLST, 3), style2) #Mar
        ws.write(47, 5, numFulfilled(euProdLST, 4), style2) #Apr
        ws.write(47, 6, numFulfilled(euProdLST, 5), style2) #May
        ws.write(47, 7, numFulfilled(euProdLST, 6), style2) #Jun
        ws.write(47, 8, numFulfilled(euProdLST, 7), style2) #Jul
        ws.write(47, 9, numFulfilled(euProdLST, 8), style2) #Aug
        ws.write(47, 10, numFulfilled(euProdLST, 9), style2) #Sep
        ws.write(47, 11, numFulfilled(euProdLST, 10), style2) #Oct
        ws.write(47, 12, numFulfilled(euProdLST, 11), style2) #Nov
        ws.write(47, 13, numFulfilled(euProdLST, 12), style2) #Dec    
        ws.write(47, 14, xlwt.Formula("SUM(C48:N48)"), style3) #Total         
        ws.write(48, 1, "# of Out of SLA AOIs (Not Completed, Ordered, or Fulfilled this year)", style2)
        ws.write(48, 2, numMiscNoData(euProdLST, 1), style2) #Jan
        ws.write(48, 3, numMiscNoData(euProdLST, 2), style2) #Feb
        ws.write(48, 4, numMiscNoData(euProdLST, 3), style2) #Mar
        ws.write(48, 5, numMiscNoData(euProdLST, 4), style2) #Apr
        ws.write(48, 6, numMiscNoData(euProdLST, 5), style2) #May
        ws.write(48, 7, numMiscNoData(euProdLST, 6), style2) #Jun
        ws.write(48, 8, numMiscNoData(euProdLST, 7), style2) #Jul
        ws.write(48, 9, numMiscNoData(euProdLST, 8), style2) #Aug
        ws.write(48, 10, numMiscNoData(euProdLST, 9), style2) #Sep
        ws.write(48, 11, numMiscNoData(euProdLST, 10), style2) #Oct
        ws.write(48, 12, numMiscNoData(euProdLST, 11), style2) #Nov
        ws.write(48, 13, numMiscNoData(euProdLST, 12), style2) #Dec    
        ws.write(48, 14, xlwt.Formula("SUM(C49:N49)"), style3) #Total         
        ws.write(49, 1, "    % in SLA", style2)   
        ws.write(49, 2, xlwt.Formula("SUM(C7:C10)/C4*100"), style3) #Jan
        ws.write(49, 3, xlwt.Formula("SUM(D7:D10)/D4*100"), style3) #Feb
        ws.write(49, 4, xlwt.Formula("SUM(E7:E10)/E4*100"), style3) #Mar
        ws.write(49, 5, xlwt.Formula("SUM(F7:F10)/F4*100"), style3) #Apr
        ws.write(49, 6, xlwt.Formula("SUM(G7:G10)/G4*100"), style3) #May
        ws.write(49, 7, xlwt.Formula("SUM(H7:H10)/H4*100"), style3) #Jun
        ws.write(49, 8, xlwt.Formula("SUM(I7:I10)/I4*100"), style3) #Jul
        ws.write(49, 9, xlwt.Formula("SUM(J7:J10)/J4*100"), style3) #Aug
        ws.write(49, 10, xlwt.Formula("SUM(K7:K10)/K4*100"), style3) #Sep
        ws.write(49, 11, xlwt.Formula("SUM(L7:L10)/L4*100"), style3) #Oct
        ws.write(49, 12, xlwt.Formula("SUM(M7:M10)/M4*100"), style3) #Nov
        ws.write(49, 13, xlwt.Formula("SUM(N7:N10)/N4*100"), style3) #Dec       
        ws.write(50, 1, "    % out of SLA", style2)
        ws.write(50, 2, xlwt.Formula("100-C14"), style3) #Jan
        ws.write(50, 3, xlwt.Formula("100-D14"), style3) #Feb
        ws.write(50, 4, xlwt.Formula("100-E14"), style3) #Mar
        ws.write(50, 5, xlwt.Formula("100-F14"), style3) #Apr
        ws.write(50, 6, xlwt.Formula("100-G14"), style3) #May
        ws.write(50, 7, xlwt.Formula("100-H14"), style3) #Jun
        ws.write(50, 8, xlwt.Formula("100-I14"), style3) #Jul
        ws.write(50, 9, xlwt.Formula("100-J14"), style3) #Aug
        ws.write(50, 10, xlwt.Formula("100-K14"), style3) #Sep
        ws.write(50, 11, xlwt.Formula("100-L14"), style3) #Oct
        ws.write(50, 12, xlwt.Formula("100-M14"), style3) #Nov
        ws.write(50, 13, xlwt.Formula("100-N14"), style3) #Dec             
        ws.write(51, 1, "# of 30cm Committed AOIs Rolling Off SLA", style2)
        ws.write(51, 2, numComOver12mos(euCurrentLST_30cm_C1, euComp30Com_1, metaDataLst), style2) #Jan
        ws.write(51, 3, numComOver12mos(euCurrentLST_30cm_C2, euComp30Com_2, metaDataLst), style2) #Feb
        ws.write(51, 4, numComOver12mos(euCurrentLST_30cm_C3, euComp30Com_3, metaDataLst), style2) #Mar
        ws.write(51, 5, numComOver12mos(euCurrentLST_30cm_C4, euComp30Com_4, metaDataLst), style2) #Apr
        ws.write(51, 6, numComOver12mos(euCurrentLST_30cm_C5, euComp30Com_5, metaDataLst), style2) #May
        ws.write(51, 7, numComOver12mos(euCurrentLST_30cm_C6, euComp30Com_6, metaDataLst), style2) #Jun
        ws.write(51, 8, numComOver12mos(euCurrentLST_30cm_C7, euComp30Com_7, metaDataLst), style2) #Jul
        ws.write(51, 9, numComOver12mos(euCurrentLST_30cm_C8, euComp30Com_8, metaDataLst), style2) #Aug
        ws.write(51, 10, numComOver12mos(euCurrentLST_30cm_C9, euComp30Com_9, metaDataLst), style2) #Sep
        ws.write(51, 11, numComOver12mos(euCurrentLST_30cm_C10, euComp30Com_10, metaDataLst), style2) #Oct
        ws.write(51, 12, numComOver12mos(euCurrentLST_30cm_C11, euComp30Com_11, metaDataLst), style2) #Nov
        ws.write(51, 13, numComOver12mos(euCurrentLST_30cm_C12, euComp30Com_12, metaDataLst), style2) #Dec    
        ws.write(51, 14, xlwt.Formula("SUM(C52:N52)"), style3) #Total        
        ws.write(52, 1, "# of Active AOIs (tasking on the deck)", style2)
        ws.write(52, 2, numTasking(euProdLST, 1), style2) #Jan
        ws.write(52, 3, numTasking(euProdLST, 2), style2) #Feb
        ws.write(52, 4, numTasking(euProdLST, 3), style2) #Mar
        ws.write(52, 5, numTasking(euProdLST, 4), style2) #Apr
        ws.write(52, 6, numTasking(euProdLST, 5), style2) #May
        ws.write(52, 7, numTasking(euProdLST, 6), style2) #Jun
        ws.write(52, 8, numTasking(euProdLST, 7), style2) #Jul
        ws.write(52, 9, numTasking(euProdLST, 8), style2) #Aug
        ws.write(52, 10, numTasking(euProdLST, 9), style2) #Sep
        ws.write(52, 11, numTasking(euProdLST, 10), style2) #Oct
        ws.write(52, 12, numTasking(euProdLST, 11), style2) #Nov
        ws.write(52, 13, numTasking(euProdLST, 12), style2) #Dec    
        ws.write(52, 14, xlwt.Formula("SUM(C53:N53)"), style3) #Total
        ws.write(54, 0, "Totals", style0)
        ws.write(54, 1, "Delta target within SLA", style2)
        ws.write(54, 2, xlwt.Formula("SUM(C43:C46)"), style3) #Jan
        ws.write(54, 3, xlwt.Formula("SUM(D43:D46)"), style3) #Feb
        ws.write(54, 4, xlwt.Formula("SUM(E43:E46)"), style3) #Mar
        ws.write(54, 5, xlwt.Formula("SUM(F43:F46)"), style3) #Apr
        ws.write(54, 6, xlwt.Formula("SUM(G43:G46)"), style3) #May
        ws.write(54, 7, xlwt.Formula("SUM(H43:H46)"), style3) #Jun
        ws.write(54, 8, xlwt.Formula("SUM(I43:I46)"), style3) #Jul
        ws.write(54, 9, xlwt.Formula("SUM(J43:J46)"), style3) #Aug
        ws.write(54, 10, xlwt.Formula("SUM(K43:K46)"), style3) #Sep
        ws.write(54, 11, xlwt.Formula("SUM(L43:L46)"), style3) #Oct
        ws.write(54, 12, xlwt.Formula("SUM(M43:M46)"), style3) #Nov
        ws.write(54, 13, xlwt.Formula("SUM(N43:N46)"), style3) #Dec
        ws.write(54, 14, xlwt.Formula("SUM(C55:N55)"), style3) #Total        
        ws.write(55, 1, "Total expired AOIs", style2)   
        ws.write(55, 2, xlwt.Formula("MAX(0,C40-C55)"), style3) #Jan
        ws.write(55, 3, xlwt.Formula("MAX(0,D40-D55)"), style3) #Feb
        ws.write(55, 4, xlwt.Formula("MAX(0,E40-E55)"), style3) #Mar
        ws.write(55, 5, xlwt.Formula("MAX(0,F40-F55)"), style3) #Apr
        ws.write(55, 6, xlwt.Formula("MAX(0,G40-G55)"), style3) #May
        ws.write(55, 7, xlwt.Formula("MAX(0,H40-H55)"), style3) #Jun
        ws.write(55, 8, xlwt.Formula("MAX(0,I40-I55)"), style3) #Jul
        ws.write(55, 9, xlwt.Formula("MAX(0,J40-J55)"), style3) #Aug
        ws.write(55, 10, xlwt.Formula("MAX(0,K40-K55)"), style3) #Sep
        ws.write(55, 11, xlwt.Formula("MAX(0,L40-L55)"), style3) #Oct
        ws.write(55, 12, xlwt.Formula("MAX(0,M40-M55)"), style3) #Nov
        ws.write(55, 13, xlwt.Formula("MAX(0,N40-N55)"), style3) #Dec
        ws.write(55, 14, xlwt.Formula("SUM(C56:N56)"), style3) #Total          
        
        #Fourth Header: MIDDLE EAST / E AFRICA -- ME
        ws.write(57, 0, "Middle East / E Africa", style0)
        ws.write(57, 1, "# of AOIs", style2)
        ws.write(57, 2, numAOIs(meAOIs, 1), style2) #Jan
        ws.write(57, 3, numAOIs(meAOIs, 2), style2) #Feb
        ws.write(57, 4, numAOIs(meAOIs, 3), style2) #Mar
        ws.write(57, 5, numAOIs(meAOIs, 4), style2) #Apr
        ws.write(57, 6, numAOIs(meAOIs, 5), style2) #May
        ws.write(57, 7, numAOIs(meAOIs, 6), style2) #Jun
        ws.write(57, 8, numAOIs(meAOIs, 7), style2) #Jul
        ws.write(57, 9, numAOIs(meAOIs, 8), style2) #Aug
        ws.write(57, 10, numAOIs(meAOIs, 9), style2) #Sep
        ws.write(57, 11, numAOIs(meAOIs, 10), style2) #Oct
        ws.write(57, 12, numAOIs(meAOIs, 11), style2) #Nov
        ws.write(57, 13, numAOIs(meAOIs, 12), style2) #Dec
        ws.write(57, 14, xlwt.Formula("SUM(C58:N58)"), style3) #Total
        ws.write(58, 1, "# of Completed AOIs (Completed this year)", style2)
        ws.write(58, 2, numComplete(meCompLST, 1), style2) #Jan
        ws.write(58, 3, numComplete(meCompLST, 2), style2) #Feb
        ws.write(58, 4, numComplete(meCompLST, 3), style2) #Mar
        ws.write(58, 5, numComplete(meCompLST, 4), style2) #Apr
        ws.write(58, 6, numComplete(meCompLST, 5), style2) #May
        ws.write(58, 7, numComplete(meCompLST, 6), style2) #Jun
        ws.write(58, 8, numComplete(meCompLST, 7), style2) #Jul
        ws.write(58, 9, numComplete(meCompLST, 8), style2) #Aug
        ws.write(58, 10, numComplete(meCompLST, 9), style2) #Sep
        ws.write(58, 11, numComplete(meCompLST, 10), style2) #Oct
        ws.write(58, 12, numComplete(meCompLST, 11), style2) #Nov
        ws.write(58, 13, numComplete(meCompLST, 12), style2) #Dec       
        ws.write(58, 14, xlwt.Formula("SUM(C59:N59)"), style3) #Total
        ws.write(59, 1, "# of Completed 30cm Committed AOIs (Completed this year)", style2)
        ws.write(59, 2, numComplete30cmCom(meProdLST, 1), style2) #Jan
        ws.write(59, 3, numComplete30cmCom(meProdLST, 2), style2) #Feb
        ws.write(59, 4, numComplete30cmCom(meProdLST, 3), style2) #Mar
        ws.write(59, 5, numComplete30cmCom(meProdLST, 4), style2) #Apr
        ws.write(59, 6, numComplete30cmCom(meProdLST, 5), style2) #May
        ws.write(59, 7, numComplete30cmCom(meProdLST, 6), style2) #Jun
        ws.write(59, 8, numComplete30cmCom(meProdLST, 7), style2) #Jul
        ws.write(59, 9, numComplete30cmCom(meProdLST, 8), style2) #Aug
        ws.write(59, 10, numComplete30cmCom(meProdLST, 9), style2) #Sep
        ws.write(59, 11, numComplete30cmCom(meProdLST, 10), style2) #Oct
        ws.write(59, 12, numComplete30cmCom(meProdLST, 11), style2) #Nov
        ws.write(59, 13, numComplete30cmCom(meProdLST, 12), style2) #Dec    
        ws.write(59, 14, xlwt.Formula("SUM(C60:N60)"), style3) #Total
        ws.write(60, 1, "# of Completed Variable AOIs 30cm 1yr (Completed this year)", style2)
        ws.write(60, 2, num12mos(meCurrentLST_30cm_1, meComp30Var_1, metaDataLst), style2) #Jan
        ws.write(60, 3, num12mos(meCurrentLST_30cm_2, meComp30Var_2, metaDataLst), style2) #Feb
        ws.write(60, 4, num12mos(meCurrentLST_30cm_3, meComp30Var_3, metaDataLst), style2) #Mar
        ws.write(60, 5, num12mos(meCurrentLST_30cm_4, meComp30Var_4, metaDataLst), style2) #Apr
        ws.write(60, 6, num12mos(meCurrentLST_30cm_5, meComp30Var_5, metaDataLst), style2) #May
        ws.write(60, 7, num12mos(meCurrentLST_30cm_6, meComp30Var_6, metaDataLst), style2) #Jun
        ws.write(60, 8, num12mos(meCurrentLST_30cm_7, meComp30Var_7, metaDataLst), style2) #Jul
        ws.write(60, 9, num12mos(meCurrentLST_30cm_8, meComp30Var_8, metaDataLst), style2) #Aug
        ws.write(60, 10, num12mos(meCurrentLST_30cm_9, meComp30Var_9, metaDataLst), style2) #Sep
        ws.write(60, 11, num12mos(meCurrentLST_30cm_10, meComp30Var_10, metaDataLst), style2) #Oct
        ws.write(60, 12, num12mos(meCurrentLST_30cm_11, meComp30Var_11, metaDataLst), style2) #Nov
        ws.write(60, 13, num12mos(meCurrentLST_30cm_12, meComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(60, 14, xlwt.Formula("SUM(C61:N61)"), style3) #Total
        ws.write(61, 1, "# of Completed Variable AOIs 30cm 2yr (Completed this year)", style2)
        ws.write(61, 2, num24mos(meCurrentLST_30cm_1, meComp30Var_1, metaDataLst), style2) #Jan
        ws.write(61, 3, num24mos(meCurrentLST_30cm_2, meComp30Var_2, metaDataLst), style2) #Feb
        ws.write(61, 4, num24mos(meCurrentLST_30cm_3, meComp30Var_3, metaDataLst), style2) #Mar
        ws.write(61, 5, num24mos(meCurrentLST_30cm_4, meComp30Var_4, metaDataLst), style2) #Apr
        ws.write(61, 6, num24mos(meCurrentLST_30cm_5, meComp30Var_5, metaDataLst), style2) #May
        ws.write(61, 7, num24mos(meCurrentLST_30cm_6, meComp30Var_6, metaDataLst), style2) #Jun
        ws.write(61, 8, num24mos(meCurrentLST_30cm_7, meComp30Var_7, metaDataLst), style2) #Jul
        ws.write(61, 9, num24mos(meCurrentLST_30cm_8, meComp30Var_8, metaDataLst), style2) #Aug
        ws.write(61, 10, num24mos(meCurrentLST_30cm_9, meComp30Var_9, metaDataLst), style2) #Sep
        ws.write(61, 11, num24mos(meCurrentLST_30cm_10, meComp30Var_10, metaDataLst), style2) #Oct
        ws.write(61, 12, num24mos(meCurrentLST_30cm_11, meComp30Var_11, metaDataLst), style2) #Nov
        ws.write(61, 13, num24mos(meCurrentLST_30cm_12, meComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(61, 14, xlwt.Formula("SUM(C62:N62)"), style3) #Total        
        ws.write(62, 1, "# of Completed Variable AOIs 50cm 1yr (Completed this year)", style2)   
        ws.write(62, 2, num12mos(meCurrentLST_50cm_1, meComp50Var_1, metaDataLst), style2) #Jan
        ws.write(62, 3, num12mos(meCurrentLST_50cm_2, meComp50Var_2, metaDataLst), style2) #Feb
        ws.write(62, 4, num12mos(meCurrentLST_50cm_3, meComp50Var_3, metaDataLst), style2) #Mar
        ws.write(62, 5, num12mos(meCurrentLST_50cm_4, meComp50Var_4, metaDataLst), style2) #Apr
        ws.write(62, 6, num12mos(meCurrentLST_50cm_5, meComp50Var_5, metaDataLst), style2) #May
        ws.write(62, 7, num12mos(meCurrentLST_50cm_6, meComp50Var_6, metaDataLst), style2) #Jun
        ws.write(62, 8, num12mos(meCurrentLST_50cm_7, meComp50Var_7, metaDataLst), style2) #Jul
        ws.write(62, 9, num12mos(meCurrentLST_50cm_8, meComp50Var_8, metaDataLst), style2) #Aug
        ws.write(62, 10, num12mos(meCurrentLST_50cm_9, meComp50Var_9, metaDataLst), style2) #Sep
        ws.write(62, 11, num12mos(meCurrentLST_50cm_10, meComp50Var_10, metaDataLst), style2) #Oct
        ws.write(62, 12, num12mos(meCurrentLST_50cm_11, meComp50Var_11, metaDataLst), style2) #Nov
        ws.write(62, 13, num12mos(meCurrentLST_50cm_12, meComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(62, 14, xlwt.Formula("SUM(C63:N63)"), style3) #Total        
        ws.write(63, 1, "# of Completed Variable AOIs 50cm 2yr (Completed this year)", style2) 
        ws.write(63, 2, num24mos(meCurrentLST_50cm_1, meComp50Var_1, metaDataLst), style2) #Jan
        ws.write(63, 3, num24mos(meCurrentLST_50cm_2, meComp50Var_2, metaDataLst), style2) #Feb
        ws.write(63, 4, num24mos(meCurrentLST_50cm_3, meComp50Var_3, metaDataLst), style2) #Mar
        ws.write(63, 5, num24mos(meCurrentLST_50cm_4, meComp50Var_4, metaDataLst), style2) #Apr
        ws.write(63, 6, num24mos(meCurrentLST_50cm_5, meComp50Var_5, metaDataLst), style2) #May
        ws.write(63, 7, num24mos(meCurrentLST_50cm_6, meComp50Var_6, metaDataLst), style2) #Jun
        ws.write(63, 8, num24mos(meCurrentLST_50cm_7, meComp50Var_7, metaDataLst), style2) #Jul
        ws.write(63, 9, num24mos(meCurrentLST_50cm_8, meComp50Var_8, metaDataLst), style2) #Aug
        ws.write(63, 10, num24mos(meCurrentLST_50cm_9, meComp50Var_9, metaDataLst), style2) #Sep
        ws.write(63, 11, num24mos(meCurrentLST_50cm_10, meComp50Var_10, metaDataLst), style2) #Oct
        ws.write(63, 12, num24mos(meCurrentLST_50cm_11, meComp50Var_11, metaDataLst), style2) #Nov
        ws.write(63, 13, num24mos(meCurrentLST_50cm_12, meComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(63, 14, xlwt.Formula("SUM(C64:N64)"), style3) #Total         
        ws.write(64, 1, "# of AOIs In Production (Ordered)", style2)     
        ws.write(64, 2, numProduction(meProdLST, 1), style2) #Jan
        ws.write(64, 3, numProduction(meProdLST, 2), style2) #Feb
        ws.write(64, 4, numProduction(meProdLST, 3), style2) #Mar
        ws.write(64, 5, numProduction(meProdLST, 4), style2) #Apr
        ws.write(64, 6, numProduction(meProdLST, 5), style2) #May
        ws.write(64, 7, numProduction(meProdLST, 6), style2) #Jun
        ws.write(64, 8, numProduction(meProdLST, 7), style2) #Jul
        ws.write(64, 9, numProduction(meProdLST, 8), style2) #Aug
        ws.write(64, 10, numProduction(meProdLST, 9), style2) #Sep
        ws.write(64, 11, numProduction(meProdLST, 10), style2) #Oct
        ws.write(64, 12, numProduction(meProdLST, 11), style2) #Nov
        ws.write(64, 13, numProduction(meProdLST, 12), style2) #Dec    
        ws.write(64, 14, xlwt.Formula("SUM(C65:N65)"), style3) #Total        
        ws.write(65, 1, "# of AOIs Ready to Order (Fulfilled)", style2)
        ws.write(65, 2, numFulfilled(meProdLST, 1), style2) #Jan
        ws.write(65, 3, numFulfilled(meProdLST, 2), style2) #Feb
        ws.write(65, 4, numFulfilled(meProdLST, 3), style2) #Mar
        ws.write(65, 5, numFulfilled(meProdLST, 4), style2) #Apr
        ws.write(65, 6, numFulfilled(meProdLST, 5), style2) #May
        ws.write(65, 7, numFulfilled(meProdLST, 6), style2) #Jun
        ws.write(65, 8, numFulfilled(meProdLST, 7), style2) #Jul
        ws.write(65, 9, numFulfilled(meProdLST, 8), style2) #Aug
        ws.write(65, 10, numFulfilled(meProdLST, 9), style2) #Sep
        ws.write(65, 11, numFulfilled(meProdLST, 10), style2) #Oct
        ws.write(65, 12, numFulfilled(meProdLST, 11), style2) #Nov
        ws.write(65, 13, numFulfilled(meProdLST, 12), style2) #Dec    
        ws.write(65, 14, xlwt.Formula("SUM(C66:N66)"), style3) #Total         
        ws.write(66, 1, "# of Out of SLA AOIs (Not Completed, Ordered, or Fulfilled this year)", style2)
        ws.write(66, 2, numMiscNoData(meProdLST, 1), style2) #Jan
        ws.write(66, 3, numMiscNoData(meProdLST, 2), style2) #Feb
        ws.write(66, 4, numMiscNoData(meProdLST, 3), style2) #Mar
        ws.write(66, 5, numMiscNoData(meProdLST, 4), style2) #Apr
        ws.write(66, 6, numMiscNoData(meProdLST, 5), style2) #May
        ws.write(66, 7, numMiscNoData(meProdLST, 6), style2) #Jun
        ws.write(66, 8, numMiscNoData(meProdLST, 7), style2) #Jul
        ws.write(66, 9, numMiscNoData(meProdLST, 8), style2) #Aug
        ws.write(66, 10, numMiscNoData(meProdLST, 9), style2) #Sep
        ws.write(66, 11, numMiscNoData(meProdLST, 10), style2) #Oct
        ws.write(66, 12, numMiscNoData(meProdLST, 11), style2) #Nov
        ws.write(66, 13, numMiscNoData(meProdLST, 12), style2) #Dec    
        ws.write(66, 14, xlwt.Formula("SUM(C67:N67)"), style3) #Total         
        ws.write(67, 1, "    % in SLA", style2)   
        ws.write(67, 2, xlwt.Formula("SUM(C7:C10)/C4*100"), style3) #Jan
        ws.write(67, 3, xlwt.Formula("SUM(D7:D10)/D4*100"), style3) #Feb
        ws.write(67, 4, xlwt.Formula("SUM(E7:E10)/E4*100"), style3) #Mar
        ws.write(67, 5, xlwt.Formula("SUM(F7:F10)/F4*100"), style3) #Apr
        ws.write(67, 6, xlwt.Formula("SUM(G7:G10)/G4*100"), style3) #May
        ws.write(67, 7, xlwt.Formula("SUM(H7:H10)/H4*100"), style3) #Jun
        ws.write(67, 8, xlwt.Formula("SUM(I7:I10)/I4*100"), style3) #Jul
        ws.write(67, 9, xlwt.Formula("SUM(J7:J10)/J4*100"), style3) #Aug
        ws.write(67, 10, xlwt.Formula("SUM(K7:K10)/K4*100"), style3) #Sep
        ws.write(67, 11, xlwt.Formula("SUM(L7:L10)/L4*100"), style3) #Oct
        ws.write(67, 12, xlwt.Formula("SUM(M7:M10)/M4*100"), style3) #Nov
        ws.write(67, 13, xlwt.Formula("SUM(N7:N10)/N4*100"), style3) #Dec          
        ws.write(68, 1, "    % out of SLA", style2)
        ws.write(68, 2, xlwt.Formula("100-C14"), style3) #Jan
        ws.write(68, 3, xlwt.Formula("100-D14"), style3) #Feb
        ws.write(68, 4, xlwt.Formula("100-E14"), style3) #Mar
        ws.write(68, 5, xlwt.Formula("100-F14"), style3) #Apr
        ws.write(68, 6, xlwt.Formula("100-G14"), style3) #May
        ws.write(68, 7, xlwt.Formula("100-H14"), style3) #Jun
        ws.write(68, 8, xlwt.Formula("100-I14"), style3) #Jul
        ws.write(68, 9, xlwt.Formula("100-J14"), style3) #Aug
        ws.write(68, 10, xlwt.Formula("100-K14"), style3) #Sep
        ws.write(68, 11, xlwt.Formula("100-L14"), style3) #Oct
        ws.write(68, 12, xlwt.Formula("100-M14"), style3) #Nov
        ws.write(68, 13, xlwt.Formula("100-N14"), style3) #Dec          
        ws.write(69, 1, "# of 30cm Committed AOIs Rolling Off SLA", style2)
        ws.write(69, 2, numComOver12mos(meCurrentLST_30cm_C1, meComp30Com_1, metaDataLst), style2) #Jan
        ws.write(69, 3, numComOver12mos(meCurrentLST_30cm_C2, meComp30Com_2, metaDataLst), style2) #Feb
        ws.write(69, 4, numComOver12mos(meCurrentLST_30cm_C3, meComp30Com_3, metaDataLst), style2) #Mar
        ws.write(69, 5, numComOver12mos(meCurrentLST_30cm_C4, meComp30Com_4, metaDataLst), style2) #Apr
        ws.write(69, 6, numComOver12mos(meCurrentLST_30cm_C5, meComp30Com_5, metaDataLst), style2) #May
        ws.write(69, 7, numComOver12mos(meCurrentLST_30cm_C6, meComp30Com_6, metaDataLst), style2) #Jun
        ws.write(69, 8, numComOver12mos(meCurrentLST_30cm_C7, meComp30Com_7, metaDataLst), style2) #Jul
        ws.write(69, 9, numComOver12mos(meCurrentLST_30cm_C8, meComp30Com_8, metaDataLst), style2) #Aug
        ws.write(69, 10, numComOver12mos(meCurrentLST_30cm_C9, meComp30Com_9, metaDataLst), style2) #Sep
        ws.write(69, 11, numComOver12mos(meCurrentLST_30cm_C10, meComp30Com_10, metaDataLst), style2) #Oct
        ws.write(69, 12, numComOver12mos(meCurrentLST_30cm_C11, meComp30Com_11, metaDataLst), style2) #Nov
        ws.write(69, 13, numComOver12mos(meCurrentLST_30cm_C12, meComp30Com_12, metaDataLst), style2) #Dec    
        ws.write(69, 14, xlwt.Formula("SUM(C70:N70)"), style3) #Total        
        ws.write(70, 1, "# of Active AOIs (tasking on the deck)", style2)
        ws.write(70, 2, numTasking(meProdLST, 1), style2) #Jan
        ws.write(70, 3, numTasking(meProdLST, 2), style2) #Feb
        ws.write(70, 4, numTasking(meProdLST, 3), style2) #Mar
        ws.write(70, 5, numTasking(meProdLST, 4), style2) #Apr
        ws.write(70, 6, numTasking(meProdLST, 5), style2) #May
        ws.write(70, 7, numTasking(meProdLST, 6), style2) #Jun
        ws.write(70, 8, numTasking(meProdLST, 7), style2) #Jul
        ws.write(70, 9, numTasking(meProdLST, 8), style2) #Aug
        ws.write(70, 10, numTasking(meProdLST, 9), style2) #Sep
        ws.write(70, 11, numTasking(meProdLST, 10), style2) #Oct
        ws.write(70, 12, numTasking(meProdLST, 11), style2) #Nov
        ws.write(70, 13, numTasking(meProdLST, 12), style2) #Dec    
        ws.write(70, 14, xlwt.Formula("SUM(C71:N71)"), style3) #Total
        ws.write(72, 0, "Totals", style0)
        ws.write(72, 1, "Delta target within SLA", style2)
        ws.write(72, 2, xlwt.Formula("SUM(C61:C64)"), style3) #Jan
        ws.write(72, 3, xlwt.Formula("SUM(D61:D64)"), style3) #Feb
        ws.write(72, 4, xlwt.Formula("SUM(E61:E64)"), style3) #Mar
        ws.write(72, 5, xlwt.Formula("SUM(F61:F64)"), style3) #Apr
        ws.write(72, 6, xlwt.Formula("SUM(G61:G64)"), style3) #May
        ws.write(72, 7, xlwt.Formula("SUM(H61:H64)"), style3) #Jun
        ws.write(72, 8, xlwt.Formula("SUM(I61:I64)"), style3) #Jul
        ws.write(72, 9, xlwt.Formula("SUM(J61:J64)"), style3) #Aug
        ws.write(72, 10, xlwt.Formula("SUM(K61:K64)"), style3) #Sep
        ws.write(72, 11, xlwt.Formula("SUM(L61:L64)"), style3) #Oct
        ws.write(72, 12, xlwt.Formula("SUM(M61:M64)"), style3) #Nov
        ws.write(72, 13, xlwt.Formula("SUM(N61:N64)"), style3) #Dec        
        ws.write(72, 14, xlwt.Formula("SUM(C73:N73)"), style3) #Total # of AOIs within SLA
        ws.write(73, 1, "Total expired AOIs", style2)    
        ws.write(73, 2, xlwt.Formula("MAX(0,C58-C73)"), style3) #Jan
        ws.write(73, 3, xlwt.Formula("MAX(0,D58-D73)"), style3) #Feb
        ws.write(73, 4, xlwt.Formula("MAX(0,E58-E73)"), style3) #Mar
        ws.write(73, 5, xlwt.Formula("MAX(0,F58-F73)"), style3) #Apr
        ws.write(73, 6, xlwt.Formula("MAX(0,G58-G73)"), style3) #May
        ws.write(73, 7, xlwt.Formula("MAX(0,H58-H73)"), style3) #Jun
        ws.write(73, 8, xlwt.Formula("MAX(0,I58-I73)"), style3) #Jul
        ws.write(73, 9, xlwt.Formula("MAX(0,J58-J73)"), style3) #Aug
        ws.write(73, 10, xlwt.Formula("MAX(0,K58-K73)"), style3) #Sep
        ws.write(73, 11, xlwt.Formula("MAX(0,L58-L73)"), style3) #Oct
        ws.write(73, 12, xlwt.Formula("MAX(0,M58-M73)"), style3) #Nov
        ws.write(73, 13, xlwt.Formula("MAX(0,N58-N73)"), style3) #Dec
        ws.write(73, 14, xlwt.Formula("SUM(C74:N74)"), style3) #Total 
        
        #Fifth Header: SOUTH PACIFIC -- SP
        ws.write(75, 0, "South Pacific", style0)
        ws.write(75, 1, "# of AOIs", style2)
        ws.write(75, 2, numAOIs(spAOIs, 1), style2) #Jan
        ws.write(75, 3, numAOIs(spAOIs, 2), style2) #Feb
        ws.write(75, 4, numAOIs(spAOIs, 3), style2) #Mar
        ws.write(75, 5, numAOIs(spAOIs, 4), style2) #Apr
        ws.write(75, 6, numAOIs(spAOIs, 5), style2) #May
        ws.write(75, 7, numAOIs(spAOIs, 6), style2) #Jun
        ws.write(75, 8, numAOIs(spAOIs, 7), style2) #Jul
        ws.write(75, 9, numAOIs(spAOIs, 8), style2) #Aug
        ws.write(75, 10, numAOIs(spAOIs, 9), style2) #Sep
        ws.write(75, 11, numAOIs(spAOIs, 10), style2) #Oct
        ws.write(75, 12, numAOIs(spAOIs, 11), style2) #Nov
        ws.write(75, 13, numAOIs(spAOIs, 12), style2) #Dec
        ws.write(75, 14, xlwt.Formula("SUM(C76:N76)"), style3) #Total
        ws.write(76, 1, "# of Completed AOIs (Completed this year)", style2)
        ws.write(76, 2, numComplete(spCompLST, 1), style2) #Jan
        ws.write(76, 3, numComplete(spCompLST, 2), style2) #Feb
        ws.write(76, 4, numComplete(spCompLST, 3), style2) #Mar
        ws.write(76, 5, numComplete(spCompLST, 4), style2) #Apr
        ws.write(76, 6, numComplete(spCompLST, 5), style2) #May
        ws.write(76, 7, numComplete(spCompLST, 6), style2) #Jun
        ws.write(76, 8, numComplete(spCompLST, 7), style2) #Jul
        ws.write(76, 9, numComplete(spCompLST, 8), style2) #Aug
        ws.write(76, 10, numComplete(spCompLST, 9), style2) #Sep
        ws.write(76, 11, numComplete(spCompLST, 10), style2) #Oct
        ws.write(76, 12, numComplete(spCompLST, 11), style2) #Nov
        ws.write(76, 13, numComplete(spCompLST, 12), style2) #Dec       
        ws.write(76, 14, xlwt.Formula("SUM(C77:N77)"), style3) #Total
        ws.write(77, 1, "# of Completed 30cm Committed AOIs (Completed this year)", style2)
        ws.write(77, 2, numComplete30cmCom(spProdLST, 1), style2) #Jan
        ws.write(77, 3, numComplete30cmCom(spProdLST, 2), style2) #Feb
        ws.write(77, 4, numComplete30cmCom(spProdLST, 3), style2) #Mar
        ws.write(77, 5, numComplete30cmCom(spProdLST, 4), style2) #Apr
        ws.write(77, 6, numComplete30cmCom(spProdLST, 5), style2) #May
        ws.write(77, 7, numComplete30cmCom(spProdLST, 6), style2) #Jun
        ws.write(77, 8, numComplete30cmCom(spProdLST, 7), style2) #Jul
        ws.write(77, 9, numComplete30cmCom(spProdLST, 8), style2) #Aug
        ws.write(77, 10, numComplete30cmCom(spProdLST, 9), style2) #Sep
        ws.write(77, 11, numComplete30cmCom(spProdLST, 10), style2) #Oct
        ws.write(77, 12, numComplete30cmCom(spProdLST, 11), style2) #Nov
        ws.write(77, 13, numComplete30cmCom(spProdLST, 12), style2) #Dec    
        ws.write(77, 14, xlwt.Formula("SUM(C78:N78)"), style3) #Total
        ws.write(78, 1, "# of Completed Variable AOIs 30cm 1yr (Completed this year)", style2)
        ws.write(78, 2, num12mos(spCurrentLST_30cm_1, spComp30Var_1, metaDataLst), style2) #Jan
        ws.write(78, 3, num12mos(spCurrentLST_30cm_2, spComp30Var_2, metaDataLst), style2) #Feb
        ws.write(78, 4, num12mos(spCurrentLST_30cm_3, spComp30Var_3, metaDataLst), style2) #Mar
        ws.write(78, 5, num12mos(spCurrentLST_30cm_4, spComp30Var_4, metaDataLst), style2) #Apr
        ws.write(78, 6, num12mos(spCurrentLST_30cm_5, spComp30Var_5, metaDataLst), style2) #May
        ws.write(78, 7, num12mos(spCurrentLST_30cm_6, spComp30Var_6, metaDataLst), style2) #Jun
        ws.write(78, 8, num12mos(spCurrentLST_30cm_7, spComp30Var_7, metaDataLst), style2) #Jul
        ws.write(78, 9, num12mos(spCurrentLST_30cm_8, spComp30Var_8, metaDataLst), style2) #Aug
        ws.write(78, 10, num12mos(spCurrentLST_30cm_9, spComp30Var_9, metaDataLst), style2) #Sep
        ws.write(78, 11, num12mos(spCurrentLST_30cm_10, spComp30Var_10, metaDataLst), style2) #Oct
        ws.write(78, 12, num12mos(spCurrentLST_30cm_11, spComp30Var_11, metaDataLst), style2) #Nov
        ws.write(78, 13, num12mos(spCurrentLST_30cm_12, spComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(78, 14, xlwt.Formula("SUM(C79:N79)"), style3) #Total
        ws.write(79, 1, "# of Completed Variable AOIs 30cm 2yr (Completed this year)", style2)
        ws.write(79, 2, num24mos(spCurrentLST_30cm_1, spComp30Var_1, metaDataLst), style2) #Jan
        ws.write(79, 3, num24mos(spCurrentLST_30cm_2, spComp30Var_2, metaDataLst), style2) #Feb
        ws.write(79, 4, num24mos(spCurrentLST_30cm_3, spComp30Var_3, metaDataLst), style2) #Mar
        ws.write(79, 5, num24mos(spCurrentLST_30cm_4, spComp30Var_4, metaDataLst), style2) #Apr
        ws.write(79, 6, num24mos(spCurrentLST_30cm_5, spComp30Var_5, metaDataLst), style2) #May
        ws.write(79, 7, num24mos(spCurrentLST_30cm_6, spComp30Var_6, metaDataLst), style2) #Jun
        ws.write(79, 8, num24mos(spCurrentLST_30cm_7, spComp30Var_7, metaDataLst), style2) #Jul
        ws.write(79, 9, num24mos(spCurrentLST_30cm_8, spComp30Var_8, metaDataLst), style2) #Aug
        ws.write(79, 10, num24mos(spCurrentLST_30cm_9, spComp30Var_9, metaDataLst), style2) #Sep
        ws.write(79, 11, num24mos(spCurrentLST_30cm_10, spComp30Var_10, metaDataLst), style2) #Oct
        ws.write(79, 12, num24mos(spCurrentLST_30cm_11, spComp30Var_11, metaDataLst), style2) #Nov
        ws.write(79, 13, num24mos(spCurrentLST_30cm_12, spComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(79, 14, xlwt.Formula("SUM(C80:N80)"), style3) #Total        
        ws.write(80, 1, "# of Completed Variable AOIs 50cm 1yr (Completed this year)", style2)   
        ws.write(80, 2, num12mos(spCurrentLST_50cm_1, spComp50Var_1, metaDataLst), style2) #Jan
        ws.write(80, 3, num12mos(spCurrentLST_50cm_2, spComp50Var_2, metaDataLst), style2) #Feb
        ws.write(80, 4, num12mos(spCurrentLST_50cm_3, spComp50Var_3, metaDataLst), style2) #Mar
        ws.write(80, 5, num12mos(spCurrentLST_50cm_4, spComp50Var_4, metaDataLst), style2) #Apr
        ws.write(80, 6, num12mos(spCurrentLST_50cm_5, spComp50Var_5, metaDataLst), style2) #May
        ws.write(80, 7, num12mos(spCurrentLST_50cm_6, spComp50Var_6, metaDataLst), style2) #Jun
        ws.write(80, 8, num12mos(spCurrentLST_50cm_7, spComp50Var_7, metaDataLst), style2) #Jul
        ws.write(80, 9, num12mos(spCurrentLST_50cm_8, spComp50Var_8, metaDataLst), style2) #Aug
        ws.write(80, 10, num12mos(spCurrentLST_50cm_9, spComp50Var_9, metaDataLst), style2) #Sep
        ws.write(80, 11, num12mos(spCurrentLST_50cm_10, spComp50Var_10, metaDataLst), style2) #Oct
        ws.write(80, 12, num12mos(spCurrentLST_50cm_11, spComp50Var_11, metaDataLst), style2) #Nov
        ws.write(80, 13, num12mos(spCurrentLST_50cm_12, spComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(80, 14, xlwt.Formula("SUM(C81:N81)"), style3) #Total        
        ws.write(81, 1, "# of Completed Variable AOIs 50cm 2yr (Completed this year)", style2) 
        ws.write(81, 2, num24mos(spCurrentLST_50cm_1, spComp50Var_1, metaDataLst), style2) #Jan
        ws.write(81, 3, num24mos(spCurrentLST_50cm_2, spComp50Var_2, metaDataLst), style2) #Feb
        ws.write(81, 4, num24mos(spCurrentLST_50cm_3, spComp50Var_3, metaDataLst), style2) #Mar
        ws.write(81, 5, num24mos(spCurrentLST_50cm_4, spComp50Var_4, metaDataLst), style2) #Apr
        ws.write(81, 6, num24mos(spCurrentLST_50cm_5, spComp50Var_5, metaDataLst), style2) #May
        ws.write(81, 7, num24mos(spCurrentLST_50cm_6, spComp50Var_6, metaDataLst), style2) #Jun
        ws.write(81, 8, num24mos(spCurrentLST_50cm_7, spComp50Var_7, metaDataLst), style2) #Jul
        ws.write(81, 9, num24mos(spCurrentLST_50cm_8, spComp50Var_8, metaDataLst), style2) #Aug
        ws.write(81, 10, num24mos(spCurrentLST_50cm_9, spComp50Var_9, metaDataLst), style2) #Sep
        ws.write(81, 11, num24mos(spCurrentLST_50cm_10, spComp50Var_10, metaDataLst), style2) #Oct
        ws.write(81, 12, num24mos(spCurrentLST_50cm_11, spComp50Var_11, metaDataLst), style2) #Nov
        ws.write(81, 13, num24mos(spCurrentLST_50cm_12, spComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(81, 14, xlwt.Formula("SUM(C82:N82)"), style3) #Total         
        ws.write(82, 1, "# of AOIs In Production (Ordered)", style2)     
        ws.write(82, 2, numProduction(spProdLST, 1), style2) #Jan
        ws.write(82, 3, numProduction(spProdLST, 2), style2) #Feb
        ws.write(82, 4, numProduction(spProdLST, 3), style2) #Mar
        ws.write(82, 5, numProduction(spProdLST, 4), style2) #Apr
        ws.write(82, 6, numProduction(spProdLST, 5), style2) #May
        ws.write(82, 7, numProduction(spProdLST, 6), style2) #Jun
        ws.write(82, 8, numProduction(spProdLST, 7), style2) #Jul
        ws.write(82, 9, numProduction(spProdLST, 8), style2) #Aug
        ws.write(82, 10, numProduction(spProdLST, 9), style2) #Sep
        ws.write(82, 11, numProduction(spProdLST, 10), style2) #Oct
        ws.write(82, 12, numProduction(spProdLST, 11), style2) #Nov
        ws.write(82, 13, numProduction(spProdLST, 12), style2) #Dec    
        ws.write(82, 14, xlwt.Formula("SUM(C83:N83)"), style3) #Total        
        ws.write(83, 1, "# of AOIs Ready to Order (Fulfilled)", style2)
        ws.write(83, 2, numFulfilled(spProdLST, 1), style2) #Jan
        ws.write(83, 3, numFulfilled(spProdLST, 2), style2) #Feb
        ws.write(83, 4, numFulfilled(spProdLST, 3), style2) #Mar
        ws.write(83, 5, numFulfilled(spProdLST, 4), style2) #Apr
        ws.write(83, 6, numFulfilled(spProdLST, 5), style2) #May
        ws.write(83, 7, numFulfilled(spProdLST, 6), style2) #Jun
        ws.write(83, 8, numFulfilled(spProdLST, 7), style2) #Jul
        ws.write(83, 9, numFulfilled(spProdLST, 8), style2) #Aug
        ws.write(83, 10, numFulfilled(spProdLST, 9), style2) #Sep
        ws.write(83, 11, numFulfilled(spProdLST, 10), style2) #Oct
        ws.write(83, 12, numFulfilled(spProdLST, 11), style2) #Nov
        ws.write(83, 13, numFulfilled(spProdLST, 12), style2) #Dec    
        ws.write(83, 14, xlwt.Formula("SUM(C84:N84)"), style3) #Total         
        ws.write(84, 1, "# of Out of SLA AOIs (Not Completed, Ordered, or Fulfilled this year)", style2)
        ws.write(84, 2, numMiscNoData(spProdLST, 1), style2) #Jan
        ws.write(84, 3, numMiscNoData(spProdLST, 2), style2) #Feb
        ws.write(84, 4, numMiscNoData(spProdLST, 3), style2) #Mar
        ws.write(84, 5, numMiscNoData(spProdLST, 4), style2) #Apr
        ws.write(84, 6, numMiscNoData(spProdLST, 5), style2) #May
        ws.write(84, 7, numMiscNoData(spProdLST, 6), style2) #Jun
        ws.write(84, 8, numMiscNoData(spProdLST, 7), style2) #Jul
        ws.write(84, 9, numMiscNoData(spProdLST, 8), style2) #Aug
        ws.write(84, 10, numMiscNoData(spProdLST, 9), style2) #Sep
        ws.write(84, 11, numMiscNoData(spProdLST, 10), style2) #Oct
        ws.write(84, 12, numMiscNoData(spProdLST, 11), style2) #Nov
        ws.write(84, 13, numMiscNoData(spProdLST, 12), style2) #Dec    
        ws.write(84, 14, xlwt.Formula("SUM(C85:N85)"), style3) #Total         
        ws.write(85, 1, "    % in SLA", style2)   
        ws.write(85, 2, xlwt.Formula("SUM(C7:C10)/C4*100"), style3) #Jan
        ws.write(85, 3, xlwt.Formula("SUM(D7:D10)/D4*100"), style3) #Feb
        ws.write(85, 4, xlwt.Formula("SUM(E7:E10)/E4*100"), style3) #Mar
        ws.write(85, 5, xlwt.Formula("SUM(F7:F10)/F4*100"), style3) #Apr
        ws.write(85, 6, xlwt.Formula("SUM(G7:G10)/G4*100"), style3) #May
        ws.write(85, 7, xlwt.Formula("SUM(H7:H10)/H4*100"), style3) #Jun
        ws.write(85, 8, xlwt.Formula("SUM(I7:I10)/I4*100"), style3) #Jul
        ws.write(85, 9, xlwt.Formula("SUM(J7:J10)/J4*100"), style3) #Aug
        ws.write(85, 10, xlwt.Formula("SUM(K7:K10)/K4*100"), style3) #Sep
        ws.write(85, 11, xlwt.Formula("SUM(L7:L10)/L4*100"), style3) #Oct
        ws.write(85, 12, xlwt.Formula("SUM(M7:M10)/M4*100"), style3) #Nov
        ws.write(85, 13, xlwt.Formula("SUM(N7:N10)/N4*100"), style3) #Dec          
        ws.write(86, 1, "    % out of SLA", style2)
        ws.write(86, 2, xlwt.Formula("100-C14"), style3) #Jan
        ws.write(86, 3, xlwt.Formula("100-D14"), style3) #Feb
        ws.write(86, 4, xlwt.Formula("100-E14"), style3) #Mar
        ws.write(86, 5, xlwt.Formula("100-F14"), style3) #Apr
        ws.write(86, 6, xlwt.Formula("100-G14"), style3) #May
        ws.write(86, 7, xlwt.Formula("100-H14"), style3) #Jun
        ws.write(86, 8, xlwt.Formula("100-I14"), style3) #Jul
        ws.write(86, 9, xlwt.Formula("100-J14"), style3) #Aug
        ws.write(86, 10, xlwt.Formula("100-K14"), style3) #Sep
        ws.write(86, 11, xlwt.Formula("100-L14"), style3) #Oct
        ws.write(86, 12, xlwt.Formula("100-M14"), style3) #Nov
        ws.write(86, 13, xlwt.Formula("100-N14"), style3) #Dec           
        ws.write(87, 1, "# of 30cm Committed AOIs Rolling Off SLA", style2)
        ws.write(87, 2, numComOver12mos(spCurrentLST_30cm_C1, spComp30Com_1, metaDataLst), style2) #Jan
        ws.write(87, 3, numComOver12mos(spCurrentLST_30cm_C2, spComp30Com_2, metaDataLst), style2) #Feb
        ws.write(87, 4, numComOver12mos(spCurrentLST_30cm_C3, spComp30Com_3, metaDataLst), style2) #Mar
        ws.write(87, 5, numComOver12mos(spCurrentLST_30cm_C4, spComp30Com_4, metaDataLst), style2) #Apr
        ws.write(87, 6, numComOver12mos(spCurrentLST_30cm_C5, spComp30Com_5, metaDataLst), style2) #May
        ws.write(87, 7, numComOver12mos(spCurrentLST_30cm_C6, spComp30Com_6, metaDataLst), style2) #Jun
        ws.write(87, 8, numComOver12mos(spCurrentLST_30cm_C7, spComp30Com_7, metaDataLst), style2) #Jul
        ws.write(87, 9, numComOver12mos(spCurrentLST_30cm_C8, spComp30Com_8, metaDataLst), style2) #Aug
        ws.write(87, 10, numComOver12mos(spCurrentLST_30cm_C9, spComp30Com_9, metaDataLst), style2) #Sep
        ws.write(87, 11, numComOver12mos(spCurrentLST_30cm_C10, spComp30Com_10, metaDataLst), style2) #Oct
        ws.write(87, 12, numComOver12mos(spCurrentLST_30cm_C11, spComp30Com_11, metaDataLst), style2) #Nov
        ws.write(87, 13, numComOver12mos(spCurrentLST_30cm_C12, spComp30Com_12, metaDataLst), style2) #Dec    
        ws.write(87, 14, xlwt.Formula("SUM(C88:N88)"), style3) #Total        
        ws.write(88, 1, "# of Active AOIs (tasking on the deck)", style2)
        ws.write(88, 2, numTasking(spProdLST, 1), style2) #Jan
        ws.write(88, 3, numTasking(spProdLST, 2), style2) #Feb
        ws.write(88, 4, numTasking(spProdLST, 3), style2) #Mar
        ws.write(88, 5, numTasking(spProdLST, 4), style2) #Apr
        ws.write(88, 6, numTasking(spProdLST, 5), style2) #May
        ws.write(88, 7, numTasking(spProdLST, 6), style2) #Jun
        ws.write(88, 8, numTasking(spProdLST, 7), style2) #Jul
        ws.write(88, 9, numTasking(spProdLST, 8), style2) #Aug
        ws.write(88, 10, numTasking(spProdLST, 9), style2) #Sep
        ws.write(88, 11, numTasking(spProdLST, 10), style2) #Oct
        ws.write(88, 12, numTasking(spProdLST, 11), style2) #Nov
        ws.write(88, 13, numTasking(spProdLST, 12), style2) #Dec    
        ws.write(88, 14, xlwt.Formula("SUM(C89:N89)"), style3) #Total
        ws.write(90, 0, "Totals", style0)
        ws.write(90, 1, "Delta target within SLA", style2)
        ws.write(90, 2, xlwt.Formula("SUM(C79:C82)"), style3) #Jan
        ws.write(90, 3, xlwt.Formula("SUM(D79:D82)"), style3) #Feb
        ws.write(90, 4, xlwt.Formula("SUM(E79:E82)"), style3) #Mar
        ws.write(90, 5, xlwt.Formula("SUM(F79:F82)"), style3) #Apr
        ws.write(90, 6, xlwt.Formula("SUM(G79:G82)"), style3) #May
        ws.write(90, 7, xlwt.Formula("SUM(H79:H82)"), style3) #Jun
        ws.write(90, 8, xlwt.Formula("SUM(I79:I82)"), style3) #Jul
        ws.write(90, 9, xlwt.Formula("SUM(J79:J82)"), style3) #Aug
        ws.write(90, 10, xlwt.Formula("SUM(K79:K82)"), style3) #Sep
        ws.write(90, 11, xlwt.Formula("SUM(L79:L82)"), style3) #Oct
        ws.write(90, 12, xlwt.Formula("SUM(M79:M82)"), style3) #Nov
        ws.write(90, 13, xlwt.Formula("SUM(N79:N82)"), style3) #Dec   
        ws.write(90, 14, xlwt.Formula("SUM(C91:N91)"), style3) #Total  
        ws.write(91, 1, "Total expired AOIs", style2)      
        ws.write(91, 2, xlwt.Formula("MAX(0,C76-C91)"), style3) #Jan
        ws.write(91, 3, xlwt.Formula("MAX(0,D76-D91)"), style3) #Feb
        ws.write(91, 4, xlwt.Formula("MAX(0,E76-E91)"), style3) #Mar
        ws.write(91, 5, xlwt.Formula("MAX(0,F76-F91)"), style3) #Apr
        ws.write(91, 6, xlwt.Formula("MAX(0,G76-G91)"), style3) #May
        ws.write(91, 7, xlwt.Formula("MAX(0,H76-H91)"), style3) #Jun
        ws.write(91, 8, xlwt.Formula("MAX(0,I76-I91)"), style3) #Jul
        ws.write(91, 9, xlwt.Formula("MAX(0,J76-J91)"), style3) #Aug
        ws.write(91, 10, xlwt.Formula("MAX(0,K76-K91)"), style3) #Sep
        ws.write(91, 11, xlwt.Formula("MAX(0,L76-L91)"), style3) #Oct
        ws.write(91, 12, xlwt.Formula("MAX(0,M76-M91)"), style3) #Nov
        ws.write(91, 13, xlwt.Formula("MAX(0,N76-N91)"), style3) #Dec
        ws.write(91, 14, xlwt.Formula("SUM(C92:N92)"), style3) #Total         
        
        #Fifth Header: WA -- WEST ASIA
        ws.write(93, 0, "West Asia", style0)
        ws.write(93, 1, "# of AOIs", style2)
        ws.write(93, 2, numAOIs(waAOIs, 1), style2) #Jan
        ws.write(93, 3, numAOIs(waAOIs, 2), style2) #Feb
        ws.write(93, 4, numAOIs(waAOIs, 3), style2) #Mar
        ws.write(93, 5, numAOIs(waAOIs, 4), style2) #Apr
        ws.write(93, 6, numAOIs(waAOIs, 5), style2) #May
        ws.write(93, 7, numAOIs(waAOIs, 6), style2) #Jun
        ws.write(93, 8, numAOIs(waAOIs, 7), style2) #Jul
        ws.write(93, 9, numAOIs(waAOIs, 8), style2) #Aug
        ws.write(93, 10, numAOIs(waAOIs, 9), style2) #Sep
        ws.write(93, 11, numAOIs(waAOIs, 10), style2) #Oct
        ws.write(93, 12, numAOIs(waAOIs, 11), style2) #Nov
        ws.write(93, 13, numAOIs(waAOIs, 12), style2) #Dec
        ws.write(93, 14, xlwt.Formula("SUM(C94:N94)"), style3) #Total
        ws.write(94, 1, "# of Completed AOIs (Completed this year)", style2)
        ws.write(94, 2, numComplete(waCompLST, 1), style2) #Jan
        ws.write(94, 3, numComplete(waCompLST, 2), style2) #Feb
        ws.write(94, 4, numComplete(waCompLST, 3), style2) #Mar
        ws.write(94, 5, numComplete(waCompLST, 4), style2) #Apr
        ws.write(94, 6, numComplete(waCompLST, 5), style2) #May
        ws.write(94, 7, numComplete(waCompLST, 6), style2) #Jun
        ws.write(94, 8, numComplete(waCompLST, 7), style2) #Jul
        ws.write(94, 9, numComplete(waCompLST, 8), style2) #Aug
        ws.write(94, 10, numComplete(waCompLST, 9), style2) #Sep
        ws.write(94, 11, numComplete(waCompLST, 10), style2) #Oct
        ws.write(94, 12, numComplete(waCompLST, 11), style2) #Nov
        ws.write(94, 13, numComplete(waCompLST, 12), style2) #Dec       
        ws.write(94, 14, xlwt.Formula("SUM(C95:N95)"), style3) #Total
        ws.write(95, 1, "# of Completed 30cm Committed AOIs (Completed this year)", style2)
        ws.write(95, 2, numComplete30cmCom(waProdLST, 1), style2) #Jan
        ws.write(95, 3, numComplete30cmCom(waProdLST, 2), style2) #Feb
        ws.write(95, 4, numComplete30cmCom(waProdLST, 3), style2) #Mar
        ws.write(95, 5, numComplete30cmCom(waProdLST, 4), style2) #Apr
        ws.write(95, 6, numComplete30cmCom(waProdLST, 5), style2) #May
        ws.write(95, 7, numComplete30cmCom(waProdLST, 6), style2) #Jun
        ws.write(95, 8, numComplete30cmCom(waProdLST, 7), style2) #Jul
        ws.write(95, 9, numComplete30cmCom(waProdLST, 8), style2) #Aug
        ws.write(95, 10, numComplete30cmCom(waProdLST, 9), style2) #Sep
        ws.write(95, 11, numComplete30cmCom(waProdLST, 10), style2) #Oct
        ws.write(95, 12, numComplete30cmCom(waProdLST, 11), style2) #Nov
        ws.write(95, 13, numComplete30cmCom(waProdLST, 12), style2) #Dec    
        ws.write(95, 14, xlwt.Formula("SUM(C96:N96)"), style3) #Total
        ws.write(96, 1, "# of Completed Variable AOIs 30cm 1yr (Completed this year)", style2)
        ws.write(96, 2, num12mos(waCurrentLST_30cm_1, waComp30Var_1, metaDataLst), style2) #Jan
        ws.write(96, 3, num12mos(waCurrentLST_30cm_2, waComp30Var_2, metaDataLst), style2) #Feb
        ws.write(96, 4, num12mos(waCurrentLST_30cm_3, waComp30Var_3, metaDataLst), style2) #Mar
        ws.write(96, 5, num12mos(waCurrentLST_30cm_4, waComp30Var_4, metaDataLst), style2) #Apr
        ws.write(96, 6, num12mos(waCurrentLST_30cm_5, waComp30Var_5, metaDataLst), style2) #May
        ws.write(96, 7, num12mos(waCurrentLST_30cm_6, waComp30Var_6, metaDataLst), style2) #Jun
        ws.write(96, 8, num12mos(waCurrentLST_30cm_7, waComp30Var_7, metaDataLst), style2) #Jul
        ws.write(96, 9, num12mos(waCurrentLST_30cm_8, waComp30Var_8, metaDataLst), style2) #Aug
        ws.write(96, 10, num12mos(waCurrentLST_30cm_9, waComp30Var_9, metaDataLst), style2) #Sep
        ws.write(96, 11, num12mos(waCurrentLST_30cm_10, waComp30Var_10, metaDataLst), style2) #Oct
        ws.write(96, 12, num12mos(waCurrentLST_30cm_11, waComp30Var_11, metaDataLst), style2) #Nov
        ws.write(96, 13, num12mos(waCurrentLST_30cm_12, waComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(96, 14, xlwt.Formula("SUM(C97:N97)"), style3) #Total
        ws.write(97, 1, "# of Completed Variable AOIs 30cm 2yr (Completed this year)", style2)
        ws.write(97, 2, num24mos(waCurrentLST_30cm_1, waComp30Var_1, metaDataLst), style2) #Jan
        ws.write(97, 3, num24mos(waCurrentLST_30cm_2, waComp30Var_2, metaDataLst), style2) #Feb
        ws.write(97, 4, num24mos(waCurrentLST_30cm_3, waComp30Var_3, metaDataLst), style2) #Mar
        ws.write(97, 5, num24mos(waCurrentLST_30cm_4, waComp30Var_4, metaDataLst), style2) #Apr
        ws.write(97, 6, num24mos(waCurrentLST_30cm_5, waComp30Var_5, metaDataLst), style2) #May
        ws.write(97, 7, num24mos(waCurrentLST_30cm_6, waComp30Var_6, metaDataLst), style2) #Jun
        ws.write(97, 8, num24mos(waCurrentLST_30cm_7, waComp30Var_7, metaDataLst), style2) #Jul
        ws.write(97, 9, num24mos(waCurrentLST_30cm_8, waComp30Var_8, metaDataLst), style2) #Aug
        ws.write(97, 10, num24mos(waCurrentLST_30cm_9, waComp30Var_9, metaDataLst), style2) #Sep
        ws.write(97, 11, num24mos(waCurrentLST_30cm_10, waComp30Var_10, metaDataLst), style2) #Oct
        ws.write(97, 12, num24mos(waCurrentLST_30cm_11, waComp30Var_11, metaDataLst), style2) #Nov
        ws.write(97, 13, num24mos(waCurrentLST_30cm_12, waComp30Var_12, metaDataLst), style2) #Dec    
        ws.write(97, 14, xlwt.Formula("SUM(C98:N98)"), style3) #Total        
        ws.write(98, 1, "# of Completed Variable AOIs 50cm 1yr (Completed this year)", style2)   
        ws.write(98, 2, num12mos(waCurrentLST_50cm_1, waComp50Var_1, metaDataLst), style2) #Jan
        ws.write(98, 3, num12mos(waCurrentLST_50cm_2, waComp50Var_2, metaDataLst), style2) #Feb
        ws.write(98, 4, num12mos(waCurrentLST_50cm_3, waComp50Var_3, metaDataLst), style2) #Mar
        ws.write(98, 5, num12mos(waCurrentLST_50cm_4, waComp50Var_4, metaDataLst), style2) #Apr
        ws.write(98, 6, num12mos(waCurrentLST_50cm_5, waComp50Var_5, metaDataLst), style2) #May
        ws.write(98, 7, num12mos(waCurrentLST_50cm_6, waComp50Var_6, metaDataLst), style2) #Jun
        ws.write(98, 8, num12mos(waCurrentLST_50cm_7, waComp50Var_7, metaDataLst), style2) #Jul
        ws.write(98, 9, num12mos(waCurrentLST_50cm_8, waComp50Var_8, metaDataLst), style2) #Aug
        ws.write(98, 10, num12mos(waCurrentLST_50cm_9, waComp50Var_9, metaDataLst), style2) #Sep
        ws.write(98, 11, num12mos(waCurrentLST_50cm_10, waComp50Var_10, metaDataLst), style2) #Oct
        ws.write(98, 12, num12mos(waCurrentLST_50cm_11, waComp50Var_11, metaDataLst), style2) #Nov
        ws.write(98, 13, num12mos(waCurrentLST_50cm_12, waComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(98, 14, xlwt.Formula("SUM(C99:N99)"), style3) #Total        
        ws.write(99, 1, "# of Completed Variable AOIs 50cm 2yr (Completed this year)", style2) 
        ws.write(99, 2, num24mos(waCurrentLST_50cm_1, waComp50Var_1, metaDataLst), style2) #Jan
        ws.write(99, 3, num24mos(waCurrentLST_50cm_2, waComp50Var_2, metaDataLst), style2) #Feb
        ws.write(99, 4, num24mos(waCurrentLST_50cm_3, waComp50Var_3, metaDataLst), style2) #Mar
        ws.write(99, 5, num24mos(waCurrentLST_50cm_4, waComp50Var_4, metaDataLst), style2) #Apr
        ws.write(99, 6, num24mos(waCurrentLST_50cm_5, waComp50Var_5, metaDataLst), style2) #May
        ws.write(99, 7, num24mos(waCurrentLST_50cm_6, waComp50Var_6, metaDataLst), style2) #Jun
        ws.write(99, 8, num24mos(waCurrentLST_50cm_7, waComp50Var_7, metaDataLst), style2) #Jul
        ws.write(99, 9, num24mos(waCurrentLST_50cm_8, waComp50Var_8, metaDataLst), style2) #Aug
        ws.write(99, 10, num24mos(waCurrentLST_50cm_9, waComp50Var_9, metaDataLst), style2) #Sep
        ws.write(99, 11, num24mos(waCurrentLST_50cm_10, waComp50Var_10, metaDataLst), style2) #Oct
        ws.write(99, 12, num24mos(waCurrentLST_50cm_11, waComp50Var_11, metaDataLst), style2) #Nov
        ws.write(99, 13, num24mos(waCurrentLST_50cm_12, waComp50Var_12, metaDataLst), style2) #Dec    
        ws.write(99, 14, xlwt.Formula("SUM(C100:N100)"), style3) #Total         
        ws.write(100, 1, "# of AOIs In Production (Ordered)", style2)     
        ws.write(100, 2, numProduction(waProdLST, 1), style2) #Jan
        ws.write(100, 3, numProduction(waProdLST, 2), style2) #Feb
        ws.write(100, 4, numProduction(waProdLST, 3), style2) #Mar
        ws.write(100, 5, numProduction(waProdLST, 4), style2) #Apr
        ws.write(100, 6, numProduction(waProdLST, 5), style2) #May
        ws.write(100, 7, numProduction(waProdLST, 6), style2) #Jun
        ws.write(100, 8, numProduction(waProdLST, 7), style2) #Jul
        ws.write(100, 9, numProduction(waProdLST, 8), style2) #Aug
        ws.write(100, 10, numProduction(waProdLST, 9), style2) #Sep
        ws.write(100, 11, numProduction(waProdLST, 10), style2) #Oct
        ws.write(100, 12, numProduction(waProdLST, 11), style2) #Nov
        ws.write(100, 13, numProduction(waProdLST, 12), style2) #Dec    
        ws.write(100, 14, xlwt.Formula("SUM(C101:N101)"), style3) #Total        
        ws.write(101, 1, "# of AOIs Ready to Order (Fulfilled)", style2)
        ws.write(101, 2, numFulfilled(waProdLST, 1), style2) #Jan
        ws.write(101, 3, numFulfilled(waProdLST, 2), style2) #Feb
        ws.write(101, 4, numFulfilled(waProdLST, 3), style2) #Mar
        ws.write(101, 5, numFulfilled(waProdLST, 4), style2) #Apr
        ws.write(101, 6, numFulfilled(waProdLST, 5), style2) #May
        ws.write(101, 7, numFulfilled(waProdLST, 6), style2) #Jun
        ws.write(101, 8, numFulfilled(waProdLST, 7), style2) #Jul
        ws.write(101, 9, numFulfilled(waProdLST, 8), style2) #Aug
        ws.write(101, 10, numFulfilled(waProdLST, 9), style2) #Sep
        ws.write(101, 11, numFulfilled(waProdLST, 10), style2) #Oct
        ws.write(101, 12, numFulfilled(waProdLST, 11), style2) #Nov
        ws.write(101, 13, numFulfilled(waProdLST, 12), style2) #Dec    
        ws.write(101, 14, xlwt.Formula("SUM(C102:N102)"), style3) #Total         
        ws.write(102, 1, "# of Out of SLA AOIs (Not Completed, Ordered, or Fulfilled this year)", style2)
        ws.write(102, 2, numMiscNoData(waProdLST, 1), style2) #Jan
        ws.write(102, 3, numMiscNoData(waProdLST, 2), style2) #Feb
        ws.write(102, 4, numMiscNoData(waProdLST, 3), style2) #Mar
        ws.write(102, 5, numMiscNoData(waProdLST, 4), style2) #Apr
        ws.write(102, 6, numMiscNoData(waProdLST, 5), style2) #May
        ws.write(102, 7, numMiscNoData(waProdLST, 6), style2) #Jun
        ws.write(102, 8, numMiscNoData(waProdLST, 7), style2) #Jul
        ws.write(102, 9, numMiscNoData(waProdLST, 8), style2) #Aug
        ws.write(102, 10, numMiscNoData(waProdLST, 9), style2) #Sep
        ws.write(102, 11, numMiscNoData(waProdLST, 10), style2) #Oct
        ws.write(102, 12, numMiscNoData(waProdLST, 11), style2) #Nov
        ws.write(102, 13, numMiscNoData(waProdLST, 12), style2) #Dec    
        ws.write(102, 14, xlwt.Formula("SUM(C103:N103)"), style3) #Total         
        ws.write(103, 1, "    % in SLA", style2)   
        ws.write(103, 2, xlwt.Formula("SUM(C7:C10)/C4*100"), style3) #Jan
        ws.write(103, 3, xlwt.Formula("SUM(D7:D10)/D4*100"), style3) #Feb
        ws.write(103, 4, xlwt.Formula("SUM(E7:E10)/E4*100"), style3) #Mar
        ws.write(103, 5, xlwt.Formula("SUM(F7:F10)/F4*100"), style3) #Apr
        ws.write(103, 6, xlwt.Formula("SUM(G7:G10)/G4*100"), style3) #May
        ws.write(103, 7, xlwt.Formula("SUM(H7:H10)/H4*100"), style3) #Jun
        ws.write(103, 8, xlwt.Formula("SUM(I7:I10)/I4*100"), style3) #Jul
        ws.write(103, 9, xlwt.Formula("SUM(J7:J10)/J4*100"), style3) #Aug
        ws.write(103, 10, xlwt.Formula("SUM(K7:K10)/K4*100"), style3) #Sep
        ws.write(103, 11, xlwt.Formula("SUM(L7:L10)/L4*100"), style3) #Oct
        ws.write(103, 12, xlwt.Formula("SUM(M7:M10)/M4*100"), style3) #Nov
        ws.write(103, 13, xlwt.Formula("SUM(N7:N10)/N4*100"), style3) #Dec     
        ws.write(104, 1, "    % out of SLA", style2)
        ws.write(104, 2, xlwt.Formula("100-C14"), style3) #Jan
        ws.write(104, 3, xlwt.Formula("100-D14"), style3) #Feb
        ws.write(104, 4, xlwt.Formula("100-E14"), style3) #Mar
        ws.write(104, 5, xlwt.Formula("100-F14"), style3) #Apr
        ws.write(104, 6, xlwt.Formula("100-G14"), style3) #May
        ws.write(104, 7, xlwt.Formula("100-H14"), style3) #Jun
        ws.write(104, 8, xlwt.Formula("100-I14"), style3) #Jul
        ws.write(104, 9, xlwt.Formula("100-J14"), style3) #Aug
        ws.write(104, 10, xlwt.Formula("100-K14"), style3) #Sep
        ws.write(104, 11, xlwt.Formula("100-L14"), style3) #Oct
        ws.write(104, 12, xlwt.Formula("100-M14"), style3) #Nov
        ws.write(104, 13, xlwt.Formula("100-N14"), style3) #Dec            
        ws.write(105, 1, "# of 30cm Committed AOIs Rolling Off SLA", style2)
        ws.write(105, 2, numComOver12mos(waCurrentLST_30cm_C1, waComp30Com_1, metaDataLst), style2) #Jan
        ws.write(105, 3, numComOver12mos(waCurrentLST_30cm_C2, waComp30Com_2, metaDataLst), style2) #Feb
        ws.write(105, 4, numComOver12mos(waCurrentLST_30cm_C3, waComp30Com_3, metaDataLst), style2) #Mar
        ws.write(105, 5, numComOver12mos(waCurrentLST_30cm_C4, waComp30Com_4, metaDataLst), style2) #Apr
        ws.write(105, 6, numComOver12mos(waCurrentLST_30cm_C5, waComp30Com_5, metaDataLst), style2) #May
        ws.write(105, 7, numComOver12mos(waCurrentLST_30cm_C6, waComp30Com_6, metaDataLst), style2) #Jun
        ws.write(105, 8, numComOver12mos(waCurrentLST_30cm_C7, waComp30Com_7, metaDataLst), style2) #Jul
        ws.write(105, 9, numComOver12mos(waCurrentLST_30cm_C8, waComp30Com_8, metaDataLst), style2) #Aug
        ws.write(105, 10, numComOver12mos(waCurrentLST_30cm_C9, waComp30Com_9, metaDataLst), style2) #Sep
        ws.write(105, 11, numComOver12mos(waCurrentLST_30cm_C10, waComp30Com_10, metaDataLst), style2) #Oct
        ws.write(105, 12, numComOver12mos(waCurrentLST_30cm_C11, waComp30Com_11, metaDataLst), style2) #Nov
        ws.write(105, 13, numComOver12mos(waCurrentLST_30cm_C12, waComp30Com_12, metaDataLst), style2) #Dec    
        ws.write(105, 14, xlwt.Formula("SUM(C106:N106)"), style3) #Total        
        ws.write(106, 1, "# of Active AOIs (tasking on the deck)", style2)
        ws.write(106, 2, numTasking(waProdLST, 1), style2) #Jan
        ws.write(106, 3, numTasking(waProdLST, 2), style2) #Feb
        ws.write(106, 4, numTasking(waProdLST, 3), style2) #Mar
        ws.write(106, 5, numTasking(waProdLST, 4), style2) #Apr
        ws.write(106, 6, numTasking(waProdLST, 5), style2) #May
        ws.write(106, 7, numTasking(waProdLST, 6), style2) #Jun
        ws.write(106, 8, numTasking(waProdLST, 7), style2) #Jul
        ws.write(106, 9, numTasking(waProdLST, 8), style2) #Aug
        ws.write(106, 10, numTasking(waProdLST, 9), style2) #Sep
        ws.write(106, 11, numTasking(waProdLST, 10), style2) #Oct
        ws.write(106, 12, numTasking(waProdLST, 11), style2) #Nov
        ws.write(106, 13, numTasking(waProdLST, 12), style2) #Dec    
        ws.write(106, 14, xlwt.Formula("SUM(C107:N107)"), style3) #Total
        ws.write(108, 0, "Totals", style0)
        ws.write(108, 1, "Delta target within SLA", style2)
        ws.write(108, 2, xlwt.Formula("SUM(C97:C100)"), style3) #Jan
        ws.write(108, 3, xlwt.Formula("SUM(D97:D100)"), style3) #Feb
        ws.write(108, 4, xlwt.Formula("SUM(E97:E100)"), style3) #Mar
        ws.write(108, 5, xlwt.Formula("SUM(F97:F100)"), style3) #Apr
        ws.write(108, 6, xlwt.Formula("SUM(G97:G100)"), style3) #May
        ws.write(108, 7, xlwt.Formula("SUM(H97:H100)"), style3) #Jun
        ws.write(108, 8, xlwt.Formula("SUM(I97:I100)"), style3) #Jul
        ws.write(108, 9, xlwt.Formula("SUM(J97:J100)"), style3) #Aug
        ws.write(108, 10, xlwt.Formula("SUM(K97:K100)"), style3) #Sep
        ws.write(108, 11, xlwt.Formula("SUM(L97:L100)"), style3) #Oct
        ws.write(108, 12, xlwt.Formula("SUM(M97:M100)"), style3) #Nov
        ws.write(108, 13, xlwt.Formula("SUM(N97:N100)"), style3) #Dec    
        ws.write(108, 14, xlwt.Formula("SUM(C109:N109)"), style3) #Total 
        ws.write(109, 1, "Total expired AOIs", style2)     
        ws.write(109, 2, xlwt.Formula("MAX(0,C94-C109)"), style3) #Jan
        ws.write(109, 3, xlwt.Formula("MAX(0,D94-D109)"), style3) #Feb
        ws.write(109, 4, xlwt.Formula("MAX(0,E94-E109)"), style3) #Mar
        ws.write(109, 5, xlwt.Formula("MAX(0,F94-F109)"), style3) #Apr
        ws.write(109, 6, xlwt.Formula("MAX(0,G94-G109)"), style3) #May
        ws.write(109, 7, xlwt.Formula("MAX(0,H94-H109)"), style3) #Jun
        ws.write(109, 8, xlwt.Formula("MAX(0,I94-I109)"), style3) #Jul
        ws.write(109, 9, xlwt.Formula("MAX(0,J94-J109)"), style3) #Aug
        ws.write(109, 10, xlwt.Formula("MAX(0,K94-K109)"), style3) #Sep
        ws.write(109, 11, xlwt.Formula("MAX(0,L94-L109)"), style3) #Oct
        ws.write(109, 12, xlwt.Formula("MAX(0,M94-M109)"), style3) #Nov
        ws.write(109, 13, xlwt.Formula("MAX(0,N94-N109)"), style3) #Dec
        ws.write(109, 14, xlwt.Formula("SUM(C110:N110)"), style3) #Total        
        
        wb.save(excelOutput)