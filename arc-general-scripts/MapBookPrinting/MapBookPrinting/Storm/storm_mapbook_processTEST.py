'''****************************************************************
storm_mapbook_process.py

Author(s): Anders Olson

Usage: Run script using python IDE or similar

Description: Storm Map Book Label Setup and PDF Exporting script
              
Initial Release Date: 7/25/18
Last Edit:

****************************************************************'''

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Import modules and packages
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  

import arcpy

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Configure Messenger 
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

outputMessage("Running: " + sys.argv[0])

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define environment
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

'''WTF is this environment?'''    
arcpy.env.workspace = r'G:\Field_Assets\Storm\MapBookPrinting\GEODB\FeatureDistance.gdb' 
arcpy.env.overwriteOutput = True

outputMessage("Workspace is: {}".format(arcpy.env.workspace))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Execute process
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

# --- Storm Map Book Label Setup: 
# Label clustering setup using buffers. Used in stormmapbook mxd.

# Define variable 'mxd' as the Storm Mapbook mxd
mxd = arcpy.mapping.MapDocument(r'G:\Field_Assets\Storm\MapBookPrinting\MXD\Storm_Mapbook.mxd')
lyrs = ['NetworkStructures', 'Ceptors', 'CleanOuts', 'ControlValves', 'PipeIns', 'PipeOuts', 'PipeEnds', 'Plugs',
        'irManholes', 'swManholes', 'udManholes', 'swInlets', 'AreaDrains', 'udAccessPoints']

# Create a 25ft buffer for every fcs
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name in lyrs:
        fc_name = lyr.name + '_buff'
        arcpy.Buffer_analysis(lyr, fc_name, "25 feet", "", "", "ALL", "", "PLANAR")
        outputMessage(fc_name + " buffer created.")

# Delete any intermediate datasets that were created in last run of script
if arcpy.Exists('AllFeatures_Merge'):
    arcpy.Delete_management('AllFeatures_Merge')
if arcpy.Exists('AllFeatures_Dissolve'):
    arcpy.Delete_management('AllFeatures_Dissolve')
if arcpy.Exists('AllFeatures_Dissolve_Multi'):
    arcpy.Delete_management('AllFeatures_Dissolve_Multi')

# Merge all the buffered fcs
arcpy.Merge_management([fc for fc in arcpy.ListFeatureClasses(feature_type='Polygon')], 'AllFeatures_Merge')

outputMessage("Merge Complete!")

# Dissolve merge fc from previous step
arcpy.Dissolve_management('AllFeatures_Merge', 'AllFeatures_Dissolve', "", "", "SINGLE_PART")

outputMessage("Dissolve Complete!")

# Make a feature later from the Dissolve output that is a selection of polygons with an area larger than 1964... WHY THE FUCK? 
arcpy.MakeFeatureLayer_management('AllFeatures_Dissolve', 'AllFeatures_Dissolve_Large', '"Shape_Area" > 1964')
arcpy.CopyFeatures_management('AllFeatures_Dissolve_Large', 'AllFeatures_Dissolve_Multi')

outputMessage("Dissolve Definition Query Complete!")

# Select Layer by Attribute was used in the earlier version of this script, but is not needed now since there is a def-query
# in the MakeFeatureLayer process. The other scripts use the SelectLayerByAttribute process instead.
#arcpy.SelectLayerByAttribute_management('AllFeatures_Dissolve_Large', "", '"Shape_Area" > 1964')


# Spatial join to dissolve layer
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name in ['swInlets', 'irManholes', 'swManholes', 'udManholes', 'Ceptors']:
        fc_name = lyr.name + '_join'
        arcpy.SpatialJoin_analysis(lyr, 'AllFeatures_Dissolve_Multi', fc_name, "", "", "", "CLOSEST", "50 Feet", "DISTANCE")

outputMessage("Completed labeling setup!")
outputMessage("Starting map book exports...")

#--- Export MXD maps to PDF:
# Process to iterate through a range of numbers (1 to 249) and 
# export a pdf map page for each number map grid.

# Define a list variable of all the grid numbers to EXCLUDE from the range
y = [81, 87, 98, 99, 103, 107, 108, 109, 110, 111, 115, 116, 117, 
     118, 119, 122, 123, 124, 128, 129, 130, 134, 135, 136, 137, 140,
     143, 144, 146, 147, 149, 150, 153, 154, 155, 156, 157, 158, 159, 
     162, 163, 164, 165, 166, 167, 169, 171, 172, 173, 175, 176, 177, 
     178, 181, 182, 183, 184, 185, 186, 187]

# String of all map grid pages excluding the above list
pgs_include = ','.join([str(i) for i in range(1,249) if i not in y])

#outputMessage(pgs_include)

import_path = r"G:\Field_Assets\Storm\MapBookPrinting\MXD\Storm_Mapbook.mxd"   # Path of mxd
#export_path = r"G:\Field_Assets\Storm\MapBookPrinting\MXD\Storm_Mapbook\Storm"   # Name of output pdf
export_path = r"U:\AOLSON\Working\temp\PDF_Maps\Storm"

try:
    mxd = arcpy.mapping.MapDocument(import_path)
    mxd.dataDrivenPages.exportToPDF(export_path, "RANGE", pgs_include, "PDF_MULTIPLE_FILES_PAGE_NAME")
    del mxd

except:
    outputMessage(arcpy.GetMessages())

outputMessage("Storm Map Book Export COMPLETE!!!")
