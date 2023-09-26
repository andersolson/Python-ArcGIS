#-------------------------------------------------------------------------------
# Name:        Tif Shape Builder
# Purpose:
#
#
# Created:     02/06/2014
# Purpose:     Takes an input and output file folder. For all .tiff files in
#              input folder, creates and empty shapefile in output folder for
#              creating exclusion polygons.
#-------------------------------------------------------------------------------
import arcpy, os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Build_Shape_from_tif"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Shape_builder"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Tif Folder",
            name="tif_folder",
            datatype="DEFOLDER",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName = "Output Folder",
            name="out_folder",
            datatype="DEFOLDER",
            parameterType="Required",
            direction="Input")

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        input_tif_folder = parameters[0].valueAsText
        output_shape_folder = parameters[1].valueAsText

        sr = arcpy.SpatialReference(4326)

        counter = 0
        for filename in os.listdir(input_tif_folder):
            if filename.endswith(".tiff") or filename.endswith(".tif"):
                string = '.'
                out_name = filename.split(string, 1)[0]
                full_path = output_shape_folder + "\\" + out_name + ".shp"
                if arcpy.Exists(full_path):
                    continue
                else:
                    arcpy.CreateFeatureclass_management(output_shape_folder, out_name, 'POLYGON',"", "", "", sr)
                    counter += 1

        arcpy.AddMessage(str(counter) + " shapefiles created in: " + str(output_shape_folder) + ".")

        return