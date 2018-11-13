import arcpy

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
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
ScratchGDB = arcpy.env.scratchGDB

outputMessage("Scratch folder is: {}".format(ScratchGDB))        

inSHP = 777 #Input shapefile that needs to be re-sorted
shpFields = ['tex','rose','betty','ted','angel'] #Input shapefile fields raw

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

def someFunction():
    pass

def alphabetize(rawLst):
    return sorted(rawLst)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Start calling functions 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

cleanLst = alphabetize(shpFields)
outputMessage(cleanLst)