import arcpy

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
        tmpLst.append(field.name)
        tmpLst.append(field.aliasName)
        tmpLst.append(field.baseName)
        tmpLst.append(field.defaultValue)
        tmpLst.append(field.domain)
        tmpLst.append(field.editable)
        tmpLst.append(field.isNullable)
        tmpLst.append(field.length)
        tmpLst.append(field.precision)
        tmpLst.append(field.required)
        tmpLst.append(field.scale)
        tmpLst.append(field.type)
        outLst.append(tmpLst)
    
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
        tmpName = "tmp{0}".format(tmpCounter)
        #outputMessage(tmpName)
        #outputMessage(item)
        tmpCounter += 1
        
        ## Add field named "tmp" to store attribute
        #arcpy.AddField_management(inShp, tmpName,"TEXT","#","#","254",tmpName,"NULLABLE")
        
        ## Calculate values for "tmp" from !stripDesc!
        #arcpy.CalculateField_management(joinOut,"tmp","!stripDesc!","PYTHON_9.3","#")  
        ## Delete the original field 
        #arcpy.DeleteField_management(joinOut,"tmp")         
        ## Add field named with proper formating
        #arcpy.AddField_management(joinOut,"CatID","TEXT","#","#","254","CatID","NULLABLE","NON_REQUIRED","#")    
        ## Calculate values for "CatID" from !tmp!
        #arcpy.CalculateField_management(joinOut,"CatID","!tmp!","PYTHON_9.3","#")    
        ## Delete the temp field 
        #arcpy.DeleteField_management(joinOut,"tmp")             

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

addNewFields(inSHP,lstProperties)
    
'''
# Get a list of all the field names found in the dataset
fieldNames = [f.name for f in arcpy.ListFields(inSHP)]

# Create an alphabetized list of the field names for a test
sortedLst = sorted(fieldNames)

re_sortFieldOrder(inSHP, sortedLst)
'''