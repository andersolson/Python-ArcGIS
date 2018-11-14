import arcpy
import sys

def outputMessage(msg):
    #print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    #print(msg)
    arcpy.AddError(msg)

outputMessage("Running: {0}".format(sys.argv[0]))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define variables and environments
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  

# Set the overwriteOutput ON
arcpy.gp.overwriteOutput = True

# Set the workspace
arcpy.env.workspace = "in_memory"
#ScratchGDB = arcpy.env.scratchGDB
#outputMessage("Scratch folder is: {}".format(ScratchGDB))        

inSHP = r'U:\AOLSON\Working\temp\system_valves.gdb\valves\SystemValves'#Input shapefile that needs to be re-sorted
capitals = True

#================================#
#Create a test list to simulate user input
testLst = []
fields = arcpy.ListFields(inSHP)
for field in fields:
    fieldName = (field.name)
    testLst.append(fieldName)
userList = sorted(testLst)
#outputMessage(userList)
#================================#

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

"""
This function stores the original field properties of the input shapefile
in a list. The "field-properties-list" is used to add new fields to the shapefile
that follow the same properties as the original fields.

Inputs:
inShp -- Input shapefile that will have fields re-sorted

Outputs:
outLst -- A nested list output of all the fields and their properties
"""
def storeFieldProperties(inShp):
    
    outLst = []
    
    # Create a list of fields using the ListFields function
    fields = arcpy.ListFields(inSHP)
    
    # Iterate through the list of fields
    for field in fields:
        
        #Temporary list for storing properties
        tmpLst = []
        
        #name variables to append to list
        tmpLst.append(field.name)         #[0]    
        tmpLst.append(field.aliasName)    #[1]
        tmpLst.append(field.domain)       #[2]
        tmpLst.append(field.length)       #[3]
        tmpLst.append(field.precision)    #[4]
        tmpLst.append(field.scale)        #[5]

        #Fix the field.type to match field types for AddField_management 
        if field.type == 'String':        #[6]
            tmpLst.append('TEXT')
        elif field.type == 'Single':
            tmpLst.append('FLOAT')        
        elif field.type == 'Double':
            tmpLst.append('DOUBLE')
        elif field.type == 'SmallInteger':
            tmpLst.append('SHORT')    
        elif field.type == 'Integer':
            tmpLst.append('LONG')     
        elif field.type == 'Date':
            tmpLst.append('DATE')
        elif field.type == 'Blob':
            tmpLst.append('BLOB')
        elif field.type == 'Raster':
            tmpLst.append('RASTER')   
        elif field.type == 'Guid':
            tmpLst.append('GUID')
        else:
            tmpLst.append(field.type)     
        
        outLst.append(tmpLst)

    #Delete any OID-type from the final list
    for item in outLst:
        if item[6] == 'OID': 
            outLst.remove(item)
    
    #Delete any Geometry-type from the final list
    for item in outLst:
        if item[6] == 'Geometry':
            outLst.remove(item)
            
    #Output is a cleaned up list
    return outLst

"""
This function adds new fields to the input dataset in the order that
the user wants the fields re-sorted. The input list is the result from
storeFieldProperties(). This result defines properties for creating the new 
fields.

Inputs:
inShp -- Input shapefile that will have fields re-sorted
inLst -- Input the "field-properties-list" result from the storeFieldProperties() function. 

Outputs:
None -- The input shapefile has fields updated as the function runs through input list
"""
def addNewFields(inShp,inLst):
    tmpCounter = 0
    for item in inLst:
        outputMessage("Sorting field: {0}...".format(item[0]))
        tmpName = "tmp{0}".format(tmpCounter)
        tmpCounter += 1
        
        # Add field named "tmp#" to create a holding spot for new field order
        arcpy.AddField_management(inShp, tmpName,"{0}".format(item[6]),"{0}".format(item[4]),
                                  "{0}".format(item[5]),"{0}".format(item[3]),"{0}".format(item[0]),
                                  "NULLABLE","NON_REQUIRED","{0}".format(item[2]))
        
        # Calculate values for "tmp#" from the associated field
        arcpy.CalculateField_management(inShp,tmpName,"!{0}!".format(item[0]),"PYTHON_9.3") 
        
        outputMessage("\t...Deleting field")
        # Delete the original field 
        arcpy.DeleteField_management(inShp,"{0}".format(item[0]))
        
        outputMessage("\t...Adding new field")
        # Add field with the new name and with proper formating
        arcpy.AddField_management(inShp, "{0}".format(item[0]),"{0}".format(item[6]),"{0}".format(item[4]),
                                  "{0}".format(item[5]),"{0}".format(item[3]),tmpName,
                                  "NULLABLE","NON_REQUIRED","{0}".format(item[2]))   
        
        outputMessage("\t...Populating new field")
        # Calculate values for the newly added field by 
        arcpy.CalculateField_management(inShp,"{0}".format(item[0]),"!{0}!".format(tmpName),"PYTHON_9.3")    
        
        outputMessage("\t...Deleting temp field")
        # Delete the temp field 
        arcpy.DeleteField_management(inShp,tmpName)             

"""
This function re-sorts the fields of an input list to match a user defined sorting.

Inputs:
userLst -- Input is a list of the field names arranged in the order that 
           the user wants them changed
oldLst  -- Input is the list result from storeFieldProperties(). This is the list of fields
           and their properties as-is before any changes
Outputs:
correctLst -- The output list is a corrected list of fields and their properties arranged
              in the order that the user wants them disaplayed.
"""
def re_sortFieldOrder(userLst, oldLst):
    
    correctLst = []
    
    for field in userLst:
        tmpLst = []
        #outputMessage("Processing Field: {0}".format(field))
        
        #Loop through the old list and arrange a new list the way the user wants it arranged
        fName       = [oldLst[x][0] for x in range(len(oldLst)) if oldLst[x][0] == field] 
        fAlias      = [oldLst[x][1] for x in range(len(oldLst)) if oldLst[x][0] == field]
        fDomain     = [oldLst[x][2] for x in range(len(oldLst)) if oldLst[x][0] == field]
        fLength     = [oldLst[x][3] for x in range(len(oldLst)) if oldLst[x][0] == field]
        fPrecision  = [oldLst[x][4] for x in range(len(oldLst)) if oldLst[x][0] == field]
        fScale      = [oldLst[x][5] for x in range(len(oldLst)) if oldLst[x][0] == field]
        fType       = [oldLst[x][6] for x in range(len(oldLst)) if oldLst[x][0] == field]
        #outputMessage("{0}-{1}-{2}-{3}-{4}-{5}-{6}".format(fName,fAlias,fDomain,fLength,fPrecision,fScale,fType))
        
        #Try to append the index content to another list, skip any fields that are 
        #empty or do not match the desired pattern
        try:
            #Append to temp list
            tmpLst.append(fName[0])
            tmpLst.append(fAlias[0])
            tmpLst.append(fDomain[0])
            tmpLst.append(fLength[0])
            tmpLst.append(fPrecision[0])
            tmpLst.append(fScale[0])
            tmpLst.append(fType[0])
            #Append to the corrected list
            correctLst.append(tmpLst)
        except:
            pass
    
    #outputMessage(correctLst)
    return correctLst     

"""
This function re-sorts the fields of an input shapefile to match a user defined sorting.

Inputs:
inShp --

Outputs:
None -- 
"""
def capitalize():
    if capitals is True:
        fName = field.name
        fieldName = fName.upper()
    else:
        fieldName = field.name    

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Start calling functions 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#Build a list of fields and their properties as they exist now
outputMessage("Creating current field list...")
lstProperties = storeFieldProperties(inSHP)
#outputMessage(lstProperties)

#Build a list of fields and their properties arranged the way 
# the user wants them arranged.
outputMessage("Creating user defined field list...")
fixedLst = re_sortFieldOrder(userList, lstProperties)
#outputMessage(fixedLst)

outputMessage("Field sorting in progress...")
addNewFields(inSHP,fixedLst)
    