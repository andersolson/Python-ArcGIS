# Name: FACILITIES_STREETS_TO_REPLICA.py

# Import system modules
import arcpy
from arcpy import env

# Compress C3GIS
arcpy.Compress_management("E:\ConnectionFiles\C3GIS.sde")

# Set workspace
env.workspace = "E:\ConnectionFiles"

# Set local variables
replica_gdb1 = "C3GIS.sde"
replica_gdb2 = "C3GISR.sde"
replica_name = "FACILITIES_STREETS_TO_REPLICA"
sync_direction = "FROM_GEODATABASE1_TO_2"
conflict_policy = "" 	    # Not applicable for one way replicas, there is not conflict detection.
conflict_detection = ""     # Not applicable for one way replicas, there is not conflict detection.
reconcile = ""              # Only applicable for Checkout replicas

# Execute SynchronizeChanges
arcpy.SynchronizeChanges_management(replica_gdb1, replica_name, replica_gdb2, sync_direction, conflict_policy, \
conflict_detection, reconcile)
