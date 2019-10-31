'''****************************************************************
sewer_mapbook_process.py

Author(s): Alex Buchans, Connor Paige, Anders Olson

Usage: Run script using python IDE or similar

Description: This python script is run on a monthly basis to 
             generate map book pages of the waste water network. 
             AKA - Sewer Map Book Label Setup Code and PDF exporting

Revision History:

Date         By            Remarks
-----------  ------------  ----------------------------------
25 JUL 2018  ABuchans      Initial Release
01 FEB 2019                New Version Release

****************************************************************'''
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Import modules and packages
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  

import arcpy

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Define variables and environments
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  

# Set the over write output ON
arcpy.gp.overwriteOutput = True

# Set the workspace
#arcpy.env.workspace = r'G:\Field_Assets\Wastewater\MapBookPrinting\GEODB\FeatureDistance.gdb'
arcpy.env.workspace = r'U:\AOLSON\Working\MapBookProject\Workspace.gdb'
arcpy.env.overwriteOutput = True
gisWorkspace = arcpy.env.workspace

# Define error message functions
def outputMessage(msg):
    print(msg)
    arcpy.AddMessage(msg)

def outputError(msg):
    print(msg)
    arcpy.AddError(msg)

outputMessage("Running: {0}".format(sys.argv[0]))    
outputMessage("Workspace folder is: {0}".format(gisWorkspace))

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##   
#================================#
# Execute script
#================================# 
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##  

#--- label clustering setup, used in sewermapbook mxd ---
#set mxd
mxd = arcpy.mapping.MapDocument(r'G:\Field_Assets\Wastewater\MapBookPrinting\MXD\Sewer_MapBooks.mxd')
lyrs = ['CleanOuts', 'Fittings', 'GreaseTraps', 'LiftStation', 'Manholes', 'MeterStation', 'NetworkStructures', 'PumpStation']

#create 25ft buffer fcs
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name in lyrs:
        fc_name = lyr.name + '_buff'
        arcpy.Buffer_analysis(lyr, fc_name, "25 feet", "", "", "ALL", "", "PLANAR")

#merge all buffer fcs
if arcpy.Exists('AllFeatures_Merge'):
    arcpy.Delete_management('AllFeatures_Merge')
if arcpy.Exists('AllFeatures_Dissolve'):
    arcpy.Delete_management('AllFeatures_Dissolve')
if arcpy.Exists('AllFeatures_Dissolve_Multi'):
    arcpy.Delete_management('AllFeatures_Dissolve_Multi')

arcpy.Merge_management([fc for fc in arcpy.ListFeatureClasses(feature_type='Polygon')], 'AllFeatures_Merge')

#dissolve merge fc from previous step
arcpy.Dissolve_management('AllFeatures_Merge', 'AllFeatures_Dissolve', "", "", "SINGLE_PART")

#def query for dissolve layer
arcpy.MakeFeatureLayer_management('AllFeatures_Dissolve', 'AllFeatures_Dissolve_Large', '"Shape_Area" > 1964')
arcpy.SelectLayerByAttribute_management('AllFeatures_Dissolve_Large', "", '"Shape_Area" > 1964')
arcpy.CopyFeatures_management('AllFeatures_Dissolve_Large', 'AllFeatures_Dissolve_Multi')

#spatial join to dissolve layer
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name in ['Manholes', 'Fittings', 'CleanOuts']:
        fc_name = lyr.name + '_join'
        arcpy.SpatialJoin_analysis(lyr, 'AllFeatures_Dissolve_Multi', fc_name, "", "", "", "CLOSEST", "50 Feet", "DISTANCE")

print("Finished with labeling setup...")
print("Starting map book exports...")

#--- export to PDF process ---
y = [20,59,70,81,86,95,97,98,99,106,107,108,109,114,115,116,117,118,119,122,123,124,128,129,130,134,135,136,140,141,
    142,143,146,147,151,153,154,155,156,160,162,163,164,165,166,169,
    170,171,172,173,175,176,177,178,179,181,182,183,184,185,186,187,188]

# str of all pages except above list of excluded
pgs_include = ','.join([str(i) for i in range(1,249) if i not in y])

import_path = r"G:\Field_Assets\Wastewater\MapBookPrinting\MXD\Sewer_MapBooks.mxd"   # Path of .mxd
export_path = r"G:\Field_Assets\Wastewater\MapBookPrinting\MXD\Sewer_Mapbook\Sewer"   # Path of output file

try:
    mxd = arcpy.mapping.MapDocument(import_path)
    mxd.dataDrivenPages.exportToPDF(export_path, "RANGE", pgs_include, "PDF_MULTIPLE_FILES_PAGE_NAME")
    del mxd

except:
    print(arcpy.GetMessages())

print("Finished map book exports")
