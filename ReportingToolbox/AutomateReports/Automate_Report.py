# ----------------------------------------------------------------------------------------------------------------------------------
# Automate_SLA_Report.py
# Created on: 2017-02-02
# Version: SCM008.2017.xxx.xxx
# Usage: Run on SCM server. Run tool using ArcGIS software: ArcMap or ArcCatalog
# Description: 
#   This python script is run on a daily schedule on the SCM server to populate the Report table in the 
#   Metro 2.0 database. 
# ----------------------------------------------------------------------------------------------------------------------------------

import arcpy
from arcpy import env
import sys
import datetime

#Import excel write tools
import xlwt
ezxf = xlwt.easyxf

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

outputMessage("Running: " + sys.argv[0])

#Text doc log file
messagesTxt    = r"E:\PlusMetro20\SLA_Report_Messages.txt" #Text file for recording messages

#Open text file for writing messages
writeTo = open(messagesTxt,'w')

outputMessage("Running: " + sys.argv[0])
writeTo.write("Running: " + sys.argv[0] + "\n")

now = datetime.datetime.today()

#Start a timer
startTime = datetime.datetime.today()

outputMessage("Today's date is: {0}".format(str(now)))
writeTo.write("Today's date is: {0}\n".format(str(now)))

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

outputMessage("Scratch GDB is: {}".format(ScratchGDB))
writeTo.write("Scratch GDB is: {0}\n".format(ScratchGDB))

inMetadata   = "Database Connections\\METRO_2o.sde\\METRO_2o.DBO.MetroFD\\METRO_2o.DBO.Metadata_Current"
inCurrentTbl = "Database Connections\\METRO_2o.sde\\METRO_2o.DBO.CompletedTable"
reportTable  = "Database Connections\\METRO_2o.sde\\METRO_2o.DBO.Report"
excelOutput  = "E:\\PlusMetro20\\MetroReport.xls"
tempTable    = ScratchGDB + "\SLA_Report"

outputMessage("Output file is: {}".format(excelOutput))
writeTo.write("Output file is: {0}\n".format(excelOutput))


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
            yLst.append(metaTable[x][1])
            yLst.append(metaTable[x][2])
            yLst.append(metaTable[x][3])
            yLst.append(metaTable[x][4])
            yLst.append(metaTable[x][5])
            outLst.append(yLst)    

#Function to find the refresh age bucket
def refreshAge(pDate):
    #Get today's date
    today = datetime.now()  
    
    #Get production date
    prodDate = pDate[0]
    
    if prodDate is None:
        pass
    else:
        # Get image age in days
        age     = abs(today-prodDate)
        ageDays = age.days
        #outputMessage(age)
        #outputMessage(ageDays)
        
        if age <= timedelta(days=365): 
            outputMessage("Age is <= 365: {0}".format(age))
            #return(age)
        elif age > timedelta(days=365):
            outputMessage("Age is > 365: {0}".format(age))
            #return(age)
        else:
            outputMessage("You summoned a demon. Hail Satan 666")
            #return('NA')      
    
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
hdngs = ['City_Name','Country','Prod_Name','ftp_Folder','GSD','Prod_Run',
         'isHVA', 'OldestDate', 'NewestDate', 'Area_sqkm',
         'Prod_Date','RollOff','Months12','Months24','Refresh',
         'Accuracy','Avg_CC','Max_ONA','Min_SunEl','Category']
# The different format types/'kinds' for each column !!!ORDER MATTERS!!! ORDER IS
# SUPER FUCKING IMPORTANT, BUT I DON"T KNOW WHY"
kinds =  'text text text text text int1 text date date int2 date text int2 int2 text int2 int2 int2 int2 text'.split()
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

#Step One: Make an index list (cityNames) of all the City Names found in the Completed table
outputMessage("Building City Name index...")
writeTo.write("Building City Name index...\n")
for row in arcpy.da.SearchCursor(inCurrentTbl, ['City_Name']):
    if row[0] in cityTracker:
        pass
    elif row[0] not in cityTracker:
        cityNames.append(row[0])
        cityTracker.append(row[0])
    else:
        outputMessage("Error building city name index...")   
outputMessage("City Name index built...")
writeTo.write("City Name index built...\n")
#outputMessage(cityNames)

#Step Two: Make an index list of all the required report attributes found in the Current Metadata table
outputMessage("Building Completed Table index...")
writeTo.write("Building Completed Table index...\n")
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

outputMessage("Completed Table index built...")
writeTo.write("Completed Table index built...\n")
#outputMessage(compTable)

outputMessage("Building current product index...")
writeTo.write("Building current product index...\n")
#Step Three: Make a list of the product names that are the most current product for each city
for i in cityNames:
    findCurrentProducts(i,compTable,productNames)
outputMessage("Current product index built...")
writeTo.write("Current product index built...\n")
#outputMessage(productNames)

#Step Four: Use list of current products to select metadata attributes
outputMessage("Building metadata product index...")     
writeTo.write("Building metadata product index...\n")
for row in arcpy.da.SearchCursor(inMetadata, ['Prod_Name','Acq_Date','AREA_KM2',
                                              'ACCURACY','ONA','SUNEL']):
    tmpLst = []
    tmpLst.append(row[0])
    tmpLst.append(row[1])
    tmpLst.append(row[2])
    tmpLst.append(row[3])
    tmpLst.append(row[4])
    tmpLst.append(row[5])

    metaTable.append(tmpLst)

outputMessage("Metadata product index built...")
writeTo.write("Metadata product index built...\n")
#outputMessage(metaTable)  

#Create a copy feature layer of current metadata
arcpy.MakeFeatureLayer_management(inMetadata, "inMetadata_lyr")        

#Step Five: Use list of current products to select metadata features
outputMessage("Calculating report fields...")
writeTo.write("Calculating report fields...\n")
for product in productNames:
    name = product[0]
    
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
    #percent12Mos(prodDate,xLst) #<12 mon
    #percent24Mos(prodDate,xLst) #<24 mon
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
    
    #Populate 24 month field
    if prodDate[0] is None:
        nestLst.append('Missing Data')
    else:
        nestLst.append(twentyMonths) #<24 mon
    
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
writeTo.write("Calculating report fields complete...\n")

outputMessage("Writing to excel...")
writeTo.write("Writing to excel...\n")
write_xls(excelOutput, wb, '+Metro 2.0', hdngs, reportLst, heading_xf, data_xfs)
outputMessage("Write to excel complete...")
writeTo.write("Write to excel complete...\n")

outputMessage("Converting XLS to DBF...")
writeTo.write("Converting XLS to DBF...\n")
arcpy.ExcelToTable_conversion(excelOutput,tempTable,"+Metro 2.0")
outputMessage("Convertion complete...")
writeTo.write("Convertion complete...\n")

#Delete all rows in the SLA report
outputMessage("Delete SLA table...")
writeTo.write("Delete SLA table...\n")
arcpy.DeleteRows_management(reportTable)
writeTo.write("Delete complete...\n")
outputMessage("Delete complete...")

outputMessage("Appending DBF table...")
writeTo.write("Appending DBF table...\n")
arcpy.Append_management(tempTable,reportTable,"NO_TEST","","")
writeTo.write("Append complete...\n")
outputMessage("Append complete...")

writeTo.write("Task COMPLETED!\n")
writeTo.close()
outputMessage("Task COMPLETED!")
