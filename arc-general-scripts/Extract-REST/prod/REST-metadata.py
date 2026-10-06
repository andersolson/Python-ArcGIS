#-----------------------------------------------------------------------------
# REST-metadata.py
#
# Author: Anders Olson 2026
#
# Usage: Script is stand alone
#
# Description: Script pulls json data from a REST url and decifers properties
#              related to the service's metadata
#-------------------------------------------------------------------------------

import json
import urllib.request

# Service-level metadata is retrieved from the service root or a specific service layer using the url
# ending ?f=pjson
metaUrl = "https://services3.arcgis.com/4PNQOtAivErR7nbT/ArcGIS/rest/services/Parcels/FeatureServer/0?f=pjson"

# Define a variable -metaData- containing all metadata properties from a url request
with urllib.request.urlopen(metaUrl) as resp:
    metaData = json.loads(resp.read())

# Find the record count limit for the service. Primary limit (layer-level)
max_record_count = metaData.get("maxRecordCount")
print(max_record_count)

# Find extended properties from the feature service
standard_max = metaData.get("standardMaxRecordCount") # May be None
tile_max     = metaData.get("tileMaxRecordCount") # May be None
factor       = metaData.get("maxRecordCountFactor") # May be None

# Find advanced properties for service capabilities like pagination and sort ordering
adv              = metaData.get("advancedQueryCapabilities", {})
supports_paging  = adv.get("supportsPagination")
supports_orderby = adv.get("supportsOrderBy")

print("Layer maxRecordCount:", max_record_count)
print("standardMaxRecordCount:", standard_max)
print("tileMaxRecordCount:", tile_max)
print("supportsPagination:", supports_paging)
print("supportsOrderby:", supports_orderby)
