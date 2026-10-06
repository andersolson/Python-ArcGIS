#-----------------------------------------------------------------------------
# REST-2-shape.py
#
# Author: Anders Olson 2026
#
# Usage: Script is stand alone
#
# Description: Script pulls json data from REST end point and converts it
#              into a shapefile/feature class
#-------------------------------------------------------------------------------

import urllib.parse
import urllib.request
import os
import arcpy
import json

# Specify desired URL for Query. For ADCO parcels no authentication should be required. Add '/query?' to the end
# of the url
qUrl = "https://services3.arcgis.com/4PNQOtAivErR7nbT/ArcGIS/rest/services/Parcels/FeatureServer/0/query?"

# Query the parameters
params = {'where': '1=1',
          'geometryType': 'esriGeometryEnvelope',
          'spatialRel': 'esriSpatialRelIntersects',
          'relationParam': '',
          'outFields': '*',
          'returnGeometry': 'true',
          'geometryPrecision':'',
          'outSR': '',
          'returnIdsOnly': 'false',
          'returnCountOnly': 'false',
          'orderByFields': '',
          'groupByFieldsForStatistics': '',
          'returnZ': 'false',
          'returnM': 'false',
          'returnDistinctValues': 'false',
          'f': 'json'}

encode_params = urllib.parse.urlencode(params).encode("utf-8")

# Create a request and read it using urllib
response = urllib.request.urlopen(url,encode_params)
json = response.read()

# Write the json response to a text file
with open("parcelsservice.json", "wb") as ms_json:
    ms_json.write(json)

# Convert JSON to shapefile using the JSONToFeatures function
ws = os.getcwd() + os.sep
arcpy.conversion.JSONToFeatures("parcelsservice.json", ws + "parcelservice.shp", "POLYGON")

