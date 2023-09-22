'''****************************************************************

Author:          Anders Olson

Revision History:

Date         By            Remarks
-----------  ------------  ----------------------------------
03 Dec 2013  AOlson        Initial Release
10 JUN 2014  AOlson        Modified processing extent
22 JUL 2014  AOlson        Tested and modified to work in a Toolbox
18 AUG 2014  AOlson        Added vector export functionality

****************************************************************'''

# Import the arcgisscripting module
import arcpy, os, sys
from arcpy import env
from arcpy.sa import *

def outputMessage(msg):
    print msg
    arcpy.AddMessage(msg)

def outputError(msg):
    print msg
    arcpy.AddError(msg)

outputMessage("Running: " + sys.argv[0])

# Set the overwriteOutput ON
arcpy.gp.overwriteOutput = True

# Set the workspace
ScratchFolder = arcpy.env.scratchFolder	
arcpy.env.workspace = ScratchFolder

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Get parameters and Set local Variables
InputData = arcpy.GetParameterAsText(0)
pixelSize = arcpy.GetParameterAsText(1)
OutName = arcpy.GetParameterAsText(2)
Projected = "PointsProjected_z.shp"
Kernel = "kernel_z.img"
Buffer = "Buffer_z.shp"
Null = "Null"


arcpy.AddMessage("ScratchFolder is:  " + ScratchFolder)
arcpy.AddMessage("Output Vector is:  " + OutName)

# Process: Project - Points need EQUIDISTANT projection for ANN.
try:
    #Set output coordinate system to be equidistant for ANN
    outCS = arcpy.SpatialReference('Equidistant Cylindrical (world)')

    #Run Project tool 
    arcpy.Project_management(InputData, "PointsProjected_z.shp", outCS)
    
    print (arcpy.GetMessages(0))

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])

# Process: Run ANN and Run Kernel Density from results (input is "PointsProjected_z.shp") 
try:
    # Obtain Nearest Neighbor Ratio and z-score
    ann_output = arcpy.AverageNearestNeighbor_stats(Projected, "EUCLIDEAN_DISTANCE", "NO_REPORT", "#")
    
    arcpy.AddMessage("The nearest neighbor index is: " + str(ann_output[0]))
    arcpy.AddMessage("The z-score of the nearest neighbor index is: " + str(ann_output[1]))
    arcpy.AddMessage("The p-value of the nearest neighbor index is: " + str(ann_output[2]))
    arcpy.AddMessage("The expected mean distance is: " + str(ann_output[3]))
    arcpy.AddMessage("The observed mean distance is: " + str(ann_output[4]))

    #dist = float(ann_output[4]) #observed mean distance
    dist = float(ann_output[3]) #expected mean distance

    print (arcpy.GetMessages(0))

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])

# Process: Create a buffer extent for points
try:
    buff_dist = str(dist) + " METERS"
    
    arcpy.Buffer_analysis(Projected, Buffer,buff_dist,"FULL","ROUND","ALL","#")
    
    print (arcpy.GetMessages(0))

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])   

# Process: Find and print the extent for the buffered points
try:
    shape = Buffer
    extent = arcpy.Describe(shape).extent
    west = extent.XMin
    south = extent.YMin
    east = extent.XMax
    north = extent.YMax
    width = extent.width
    height = extent.height
    
    print west, south, east, north, width, height
    
    print (arcpy.GetMessages(0))

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])      

# Process: Create kernel density raster image and set envirnment extent
try:
    arcpy.env.extent = arcpy.Extent(west, south, east, north)
    
    # Execute KernelDensity
    outKernelDensity = KernelDensity(Projected, "NONE", pixelSize, dist, "SQUARE_METERS")

    # Save the output
    outKernelDensity.save(Kernel)
    
    print (arcpy.GetMessages(0))

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])    

# Process: Set the NULL value for Raster image
try:
    
    # Execute Set NULL
    outSetNull = SetNull(Kernel, Kernel, "VALUE = 0")

    # Save the output
    outSetNull.save(Null)
    
    # Execute conversion 
    arcpy.RasterToOtherFormat_conversion(Null,ScratchFolder,"TIFF")
    
    # Create a raster with 6 Natural class breaks using Slice module
    outSlice = Slice(Null,"3","NATURAL_BREAKS","1")
    #outSlice.save(Slice)
    outSlice.save("Slice")
    
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])

try:
    # Create a polygon from the raster with class breaks
    #arcpy.RasterToPolygon_conversion(Slice, Reclass,"NO_SIMPLIFY","VALUE")
    arcpy.RasterToPolygon_conversion("Slice", "classPoly.shp","NO_SIMPLIFY","VALUE")

except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])

try:
    # Dissolve polygons based on classes
    #arcpy.Dissolve_management(Reclass,OutName,"GRIDCODE","#","MULTI_PART","DISSOLVE_LINES")
    arcpy.Dissolve_management("classPoly.shp",OutName,"GRIDCODE","#","MULTI_PART","DISSOLVE_LINES")
    
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
    
except Exception as ex:
    print(ex.args[0])

# Delete extraneous Temp files
def DelTemp(w, x, y, z):
        try:
                arcpy.Delete_management(w)
                print(arcpy.GetMessages(0))
                arcpy.Delete_management(x)
                print(arcpy.GetMessages(0))
                arcpy.Delete_management(y)
                print(arcpy.GetMessages(0))
                arcpy.Delete_management(z)
                print(arcpy.GetMessages(0))
                #arcpy.Delete_management(a)
                #print(arcpy.GetMessages(0))
                #arcpy.Delete_management(b)
                #print(arcpy.GetMessages(0))
                #arcpy.Delete_management(c)
                #print(arcpy.GetMessages(0))                 
        
        except arcpy.ExecuteError:
                print(arcpy.GetMessages(2))
        
        except Exception as ex:
                print(ex.args[0])

DelTemp(Projected, Kernel, Buffer, Null)