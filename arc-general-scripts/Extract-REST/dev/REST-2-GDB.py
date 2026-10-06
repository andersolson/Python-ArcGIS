'''
I am going to fucking murder AI, 8hrs for 280 lines of pagination bullshit that could be done in 12 lines!!!! Fuckkkkkkk
'''


import arcpy

service_layer = "https://services3.arcgis.com/4PNQOtAivErR7nbT/ArcGIS/rest/services/Parcels/FeatureServer/0"
out_fc = r"C:\Users\is_olson\Documents\Projects\ParcelsQAQC\ParcelsQAQC.gdb\Parcels_All"

# Allow overwrite if you rerun
arcpy.env.overwriteOutput = True

# Copy features and attributes straight into a FGDB feature class
arcpy.management.CopyFeatures(service_layer, out_fc)
