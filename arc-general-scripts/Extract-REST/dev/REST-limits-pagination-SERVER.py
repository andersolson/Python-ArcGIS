#-----------------------------------------------------------------------------
# REST-limits-pagination.py
#
# Author: Anders Olson 2026
#
# Usage: Script is stand alone
#
# Description: Script pulls json data from a REST url and decifers properties
#              related to the service's metadata. Uses logic to detect layer
#              request limits and uses pagination
#-------------------------------------------------------------------------------

import urllib.parse
import urllib.request
import json
import arcpy
import time

# ---------- arcpy messaging helpers ----------
def msg(s):
    """Info-level message to console and ArcGIS."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    text = f"[{timestamp}] {s}"
    print(text)
    try:
        arcpy.AddMessage(text)
    except Exception:
        pass

def warn(s):
    """Warning-level message."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    text = f"[{timestamp}] WARNING: {s}"
    print(text)
    try:
        arcpy.AddWarning(text)
    except Exception:
        pass

def err(s):
    """Error-level message."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    text = f"[{timestamp}] ERROR: {s}"
    print(text)
    try:
        arcpy.AddError(text)
    except Exception:
        pass

# ---------- arcpy environment variables ----------

# Allow geoprocessing tools to overwrite existing outputs
arcpy.env.overwriteOutput = True

# The root of REST service URL
root = "https://services3.arcgis.com/4PNQOtAivErR7nbT/ArcGIS/rest/services/Parcels/FeatureServer"

# Variables for navigating to layers and query/metadata of REST service URL
layer = 0
meta_url = f'{root}/{layer}?f=pjson'
query_url = f'{root}/{layer}/query?'

start_time = time.time()
msg("Starting REST download with pagination/chunking")
msg(f"Service root: {root}")
msg(f"Target layer index: {layer}")

# --- Read metadata for the desired layer ---

try:
    metaD = json.loads(urllib.request.urlopen(meta_url).read())
except Exception as e:
    err(f"Failed to read layer metadata: {e}")
    raise

# The 2000 is a fallback default count in case service does not have a max defined
max_recCount    = metaD.get("maxRecordCount", 2000)
adv             = metaD.get("advancedQueryCapabilities", {})
# If pagination not supported script fallback to chunking by ObjectID rather than attempting pagination
supports_paging = adv.get("supportsPagination", False)
oid_field       = metaD.get("objectIdField", "OBJECTID")
layer_name      = metaD.get("name", f"Layer {layer}")
geom_type       = metaD.get("geometryType", "Unknown")

msg(f"Layer name: {layer_name}")
msg(f"ObjectID field: {oid_field}")
msg(f"Geometry type: {geom_type}")
msg(f"Reported maxRecordCount: {max_recCount}")
msg(f"Supports pagination: {supports_paging}")

# --- Define base parameters for URL request ---

request_params = {
    "where": "1=1",
    "outFields": "*",
    "returnGeometry": "true",
    "f": "json",
    "orderByFields": f"{metaD.get('objectIdField', 'OBJECTID')} ASC",
    "outSR": 2877
}

# Define a few variables for running the functions
all_features   = []
last_fields    = None
last_geom_type = None

# Try to get total count of records for progress estimation
expected_total = None
try:
    # Define variable for the count of records
    count_params = {**request_params, "returnCountOnly": "true"}

    # Define variable for encoding the url request properly for http url call
    encoded = urllib.parse.urlencode(count_params).encode("utf-8")

    # Loop to collect a count of records to use for tracking progress later in script
    with urllib.request.urlopen(query_url, encoded) as resp:
        count_data = json.loads(resp.read())
        # A count of the anticipated number of records in the download
        expected_total = count_data.get("count")
        if expected_total is not None:
            msg(f"Expected total feature count (service reported): {expected_total:,}")
except Exception as e:
    warn(f"Could not retrieve a total count (returnCountOnly). Continuing without it. ({e})")

# Define a function to run the REST url query and return a json response
def run_query(params):
    # urlencode(): percent‑encode parameters as a query string so the server parses them correctly
    # .encode("utf-8"): turn the string into bytes for urlopen’s POST body and ensure non‑ASCII is correctly represented.
    encoded = urllib.parse.urlencode(params).encode("utf-8")
    try:
        with urllib.request.urlopen(query_url, encoded) as resp:
            return json.loads(resp.read())
    except Exception as e:
        err(f"Query failed (params: {list(params.keys())}): {e}")
        raise


# Logic to make REST url request and only download data if pagination is supported by the service. Otherwise, run
# fallback download method.
if supports_paging:
    # Page with resultOffset/resultRecordCount
    msg("Using pagination (resultOffset/resultRecordCount).")
    offset = 0
    page_num = 0

    while True:
        # Start a count of page number to track progress
        page_num += 1

        # Define new parameters for URL request to use record count and offset
        params = {**request_params,
                  "resultRecordCount": max_recCount,
                  "resultOffset": offset}
        msg(f"Requesting page {page_num} | offset={offset:,} | batch={max_recCount} ...")

        # Execute REST query and request
        data = run_query(params)

        # Define geometry features returned from REST url request as a list or empty list if there is nothing
        # left to return
        feats = data.get("features", [])

        # If no features are returned then exit the while loop, this is when pagination has finished returning
        # all of the features available from the service
        if not feats:
            msg(f"No features returned at offset {offset:,}. Pagination complete.")
            break

        # Add the request result to the running list of output features
        all_features.extend(feats)

        # Define the fields and geometry type schemas for each page in pagination until the end so the results
        # stay consistent while building the final JSON response
        last_fields = data.get("fields", last_fields)
        last_geom_type = data.get("geometryType", last_geom_type)

        # Progress reporting
        total = len(all_features)
        flag = data.get("exceededTransferLimit", False)
        msg(f"Page {page_num} returned {len(feats):,} features | exceededTransferLimit={flag} | cumulative={total:,}")

        # Advance the offset by the maximum allowable amount
        offset += max_recCount

        # Stop when final partial page and transfer limit has nothing left
        if not data.get("exceededTransferLimit", False) and len(feats) < max_recCount:
            break

# When pagination is not supported by REST service use a 'chunking' method by tracking ObjectIDs to make requests
# until no data is left to request
else:
    msg("Pagination not supported. Using ObjectID chunking strategy.")

    # Define new parameters for URL request to return record Ids
    id_params = {**request_params,
                 "returnIdsOnly": "true",
                 "orderByFields": ""}
    msg("Requesting full ObjectID list ...")

    # Execute REST query and request
    id_data = run_query(id_params)

    # Create a list of object ids returned from the url request
    oids = id_data.get("objectIds", [])
    msg(f"Received {len(oids):,} ObjectIDs.")

    if not oids:
        warn("No ObjectIDs returned. Nothing to download.")
    else:
        # Find the number of chunks needed to complete the download without pagination
        num_chunks = (len(oids) + max_recCount - 1) // max_recCount
        msg(f"Downloading in {num_chunks} chunk(s), chunk size up to {max_recCount}.")

        # Chunk request response by max_recCount
        for i in range(0, len(oids), max_recCount):
            # Define a variable that computes how many chunks have been processed
            chunk_index = (i // max_recCount) + 1

            # Define the size of the chunk using oids
            chunk = oids[i:i+max_recCount]

            # Define new parameters for URL request to return record Ids
            params = {**request_params,
                      "objectIds": ",".join(map(str, chunk))}

            msg(f"Chunk {chunk_index}/{num_chunks}: objectIds[{i}:{i + len(chunk)}] ...")

            # Execute REST query and request
            data = run_query(params)

            # Define geometry features returned from REST url request as a list
            feats = data.get("features", [])

            # Add the request result to the running list of output features
            all_features.extend(feats)

            # Define the fields and geometry type schemas for each page in pagination until the end so the results
            # stay consistent while building the final JSON response
            last_fields    = data.get("fields", last_fields)
            last_geom_type = data.get("geometryType", last_geom_type)

            msg(f"Chunk {chunk_index} returned {len(feats):,} features | cumulative={len(all_features):,}")

# --- Write a final Esri FeatureSet JSON for arcpy ---

final_json = {
    "displayFieldName": "",
    "fields": last_fields,
    "geometryType": last_geom_type,
    "features": all_features
}

# Define an output location for json file
# json_out = r'C:\Users\is_olson\Documents\Projects\ParcelsQAQC\scratch' # Local
json_out = r'C:\Task_Scheduler_Scripts\ADCO_Parcels_Update\output' # Server
out_json = f'{json_out}\\parcels_all.json'

# Write the results for REST url requests to a final json file
msg(f"Writing final JSON to: {out_json}")
try:
    with open(out_json, "w") as f:
        json.dump(final_json, f)
    msg(f"JSON written successfully. Total features: {len(all_features):,}")
except Exception as e:
    err(f"Failed to write JSON: {e}")
    raise

# --- convert json to shapefile ---

shp_out = f"{json_out}\\parcelservice_all.shp"
msg(f"Converting JSON to shapefile: {shp_out}")
try:
    arcpy.conversion.JSONToFeatures(out_json, shp_out, "POLYGON")
    msg("Shapefile conversion complete.")
except Exception as e:
    err(f"JSONToFeatures failed: {e}")
    raise

elapsed = time.time() - start_time
msg(f"Done. Total features: {len(all_features):,} | Elapsed: {elapsed:0.1f}s")
