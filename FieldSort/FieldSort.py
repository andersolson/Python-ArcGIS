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

inSHP = parameters[0].valueAsText #Input shapefile that needs to be re-sorted

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define functions
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

def someFunction():
    pass

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Start calling functions 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##