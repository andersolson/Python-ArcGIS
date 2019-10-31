'''****************************************************************
storm_mapbook_process.py

Author(s): Anders Olson

Usage: Run script using python IDE or similar

Description: Storm Map Book Label Setup Code and PDF exporting
              
Initial Release Date: 7/25/18
Last Edit:

****************************************************************'''

import arcpy
arcpy.env.workspace = r'G:\Field_Assets\Storm\MapBookPrinting\GEODB\FeatureDistance.gdb'
arcpy.env.overwriteOutput = True

#--- label clustering setup, used in stormmapbook mxd ---
#set mxd
mxd = arcpy.mapping.MapDocument(r'G:\Field_Assets\Storm\MapBookPrinting\MXD\Storm_Mapbook.mxd')
lyrs = ['NetworkStructures', 'Ceptors', 'CleanOuts', 'ControlValves', 'PipeIns', 'PipeOuts', 'PipeEnds', 'Plugs',
        'irManholes', 'swManholes', 'udManholes', 'swInlets', 'AreaDrains', 'udAccessPoints']

#create 25ft buffer fcs
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name in lyrs:
        fc_name = lyr.name + '_buff'
        arcpy.Buffer_analysis(lyr, fc_name, "25 feet", "", "", "ALL", "", "PLANAR")
        print(fc_name + " buffer created.")


#merge all buffer fcs
if arcpy.Exists('AllFeatures_Merge'):
    arcpy.Delete_management('AllFeatures_Merge')
if arcpy.Exists('AllFeatures_Dissolve'):
    arcpy.Delete_management('AllFeatures_Dissolve')
if arcpy.Exists('AllFeatures_Dissolve_Multi'):
    arcpy.Delete_management('AllFeatures_Dissolve_Multi')

arcpy.Merge_management([fc for fc in arcpy.ListFeatureClasses(feature_type='Polygon')], 'AllFeatures_Merge')

print("Merge Complete")

#dissolve merge fc from previous step
arcpy.Dissolve_management('AllFeatures_Merge', 'AllFeatures_Dissolve', "", "", "SINGLE_PART")

print("Dissolve Complete")

#def query for dissolve layer
arcpy.MakeFeatureLayer_management('AllFeatures_Dissolve', 'AllFeatures_Dissolve_Large', '"Shape_Area" > 1964')
#Select Layer by Attribute should not need to be used because the Make Feature Layer should already be doing this selection. Other scripts do have this tool running successfully, however.
#arcpy.SelectLayerByAttribute_management('AllFeatures_Dissolve_Large', "", '"Shape_Area" > 1964')
arcpy.CopyFeatures_management('AllFeatures_Dissolve_Large', 'AllFeatures_Dissolve_Multi')

print("Dissolve Definition Query Complete")

#spatial join to dissolve layer
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name in ['swInlets', 'irManholes', 'swManholes', 'udManholes', 'Ceptors']:
        fc_name = lyr.name + '_join'
        arcpy.SpatialJoin_analysis(lyr, 'AllFeatures_Dissolve_Multi', fc_name, "", "", "", "CLOSEST", "50 Feet", "DISTANCE")


print("Finished with labeling setup...")
print("Starting map book exports...")

#--- export to PDF process ---
y = [81, 87, 98, 99, 103, 107, 108, 109, 110, 111, 115, 116, 117, 118, 119, 122, 123, 124, 128, 129, 130, 134, 135, 136, 137, 140,
     143, 144, 146, 147, 149, 150, 153, 154, 155, 156, 157, 158, 159, 162, 163, 164, 165, 166, 167, 169, 171, 172, 173, 175, 176, 177, 178, 181, 182, 183, 184, 185, 186, 187]

# str of all pages except above list of excluded
pgs_include = ','.join([str(i) for i in range(1,249) if i not in y])



import_path = r"G:\Field_Assets\Storm\MapBookPrinting\MXD\Storm_Mapbook.mxd"   # Path of .mxd
export_path = r"G:\Field_Assets\Storm\MapBookPrinting\MXD\Storm_Mapbook\Storm"   # Path of output file

try:
    mxd = arcpy.mapping.MapDocument(import_path)
    mxd.dataDrivenPages.exportToPDF(export_path, "RANGE", pgs_include, "PDF_MULTIPLE_FILES_PAGE_NAME")
    del mxd

except:
    print(arcpy.GetMessages())

print("Finished map book exports")
