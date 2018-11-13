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
        
        if capitals is True:
            fName = field.name
            fieldName = fName.upper()
        else:
            fieldName = field.name

        #name variables to append to list
        tmpLst.append(fieldName)         #[0]    
        tmpLst.append(field.aliasName)    #[1]
        tmpLst.append(field.baseName)     #[2]
        tmpLst.append(field.defaultValue) #[3]
        tmpLst.append(field.domain)       #[4]
        tmpLst.append(field.editable)     #[5]
        tmpLst.append(field.isNullable)   #[6]
        tmpLst.append(field.length)       #[7]
        tmpLst.append(field.precision)    #[8]
        tmpLst.append(field.required)     #[9]
        tmpLst.append(field.scale)        #[10]
        
        #Fix the field.type to match field types for AddField_management 
        if field.type == 'String':
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
            tmpLst.append(field.type)     #[11]
        
        outLst.append(tmpLst)
    
    
    #Delete any OID-type from the final list
    for item in outLst:
        if item[11] == 'OID': 
            outLst.remove(item)
    
    #Delete any Geometry-type from the final list
    for item in outLst:
        if item[11] == 'Geometry':
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
        
        '''
        outputMessage(item[11])
        outputMessage(item[8])
        outputMessage(item[10])
        outputMessage(item[7])
        outputMessage(item[1]) 
        outputMessage(item[4])
        outputMessage(item[0])
        '''
        
        # Add field named "tmp#" to create a holding spot for new field order
        arcpy.AddField_management(inShp, tmpName,"{0}".format(item[11]),"{0}".format(item[8]),
                                  "{0}".format(item[10]),"{0}".format(item[7]),tmpName,
                                  "NULLABLE","NON_REQUIRED","{0}".format(item[4]))
        
        # Calculate values for "tmp#" from the associated field
        arcpy.CalculateField_management(inShp,tmpName,"!{0}!".format(item[0]),"PYTHON_9.3") 
        
        outputMessage("\t...Deleting field")
        # Delete the original field 
        arcpy.DeleteField_management(inShp,"{0}".format(item[0]))
        
        outputMessage("\t...Adding new field")
        # Add field named with proper formating
        arcpy.AddField_management(inShp, "{0}".format(item[0]),"{0}".format(item[11]),"{0}".format(item[8]),
                                  "{0}".format(item[10]),"{0}".format(item[7]),tmpName,
                                  "NULLABLE","NON_REQUIRED","{0}".format(item[4]))   
        
        outputMessage("\t...Populating new field")
        # Calculate values for the newly added field by 
        arcpy.CalculateField_management(inShp,"{0}".format(item[0]),"!{0}!".format(tmpName),"PYTHON_9.3")    
        
        outputMessage("\t...Deleting temp field")
        # Delete the temp field 
        arcpy.DeleteField_management(inShp,tmpName)             

"""
This function re-sorts the fields of an input shapefile to match a user defined sorting.

Inputs:
inShp -- Input shapefile that will have fields re-sorted
inFieldNames -- Input a sorted list of field names. The field names should be
                sorted the way the user wants their stuff sorted.

Outputs:
None -- The input shapefile has fields updated as the function runs through input list
"""
def re_sortFieldOrder(inShp, inFieldNames):
    #Loop through field names in the list and update the shapefile
    for field in inFieldNames:
        outputMessage(field)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Start calling functions 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

lstProperties = storeFieldProperties(inSHP)
#outputMessage(lstProperties)

#addNewFields(inSHP,lstProperties)

outputMessage("Field sorting in progress...")
try:
    outputMessage("...")
    addNewFields(inSHP,lstProperties)
except:
    outputError("Error encountered during field sort!")
    sys.exit(".Process Terminated.")
    