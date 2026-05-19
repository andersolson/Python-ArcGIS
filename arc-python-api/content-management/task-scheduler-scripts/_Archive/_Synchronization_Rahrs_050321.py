# Name: C3GIS Replica to C3GISR.py
# Created by Robert Rahrs - 05/03/2021
# Updated 7/7/21


# Import system modules
import arcpy
from arcpy import env

# Compress C3GIS
arcpy.Compress_management("C:\Users\IS_RAHRS\AppData\Roaming\ESRI\Desktop10.7\ArcCatalog\Connection to C3GIS.sde")

# Set workspace
env.workspace = "C:\Users\IS_RAHRS\AppData\Roaming\ESRI\Desktop10.7\ArcCatalog"

# Set local variables
replica_gdb1 = "Connection to C3GIS.sde"
replica_gdb2 = "Connection to C3GISR.sde"
replica_name = "C3_TO_C3GISR"
sync_direction = "FROM_GEODATABASE1_TO_2"
conflict_policy = "" 						# Not applicable for one way replicas, there is not conflict detection.
conflict_detection = ""    # Not applicable for one way replicas, there is not conflict detection.
reconcile = ""             # Only applicable for Checkout replicas

# Execute SynchronizeChanges
arcpy.SynchronizeChanges_management(replica_gdb1, replica_name, replica_gdb2, sync_direction, conflict_policy, \
conflict_detection, reconcile)
