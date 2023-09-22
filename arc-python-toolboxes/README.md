# Python Toolboxes

My collection of custom toolboxes for various geoprocessing tasks not readily available in standard ArcPro tools.

Source: [ESRI Python Toolboxes](https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/a-quick-tour-of-python-toolboxes.htm)

Python toolboxes are geoprocessing toolboxes that are created entirely in Python. A Python toolbox and the tools contained within look, act, and work just like toolboxes and tools created in any other way. A Python toolbox is a Python file with a .pyt extension that defines a toolbox and one or more tools.

Once created, tools in a Python toolbox provide many advantages:

* A script tool that you create is an integral part of geoprocessing, just like a system tool—you can open it from the Catalog pane, use it in ModelBuilder and the Python window, and call it from another script.
* You can write messages to the Geoprocessing history window and tool dialog box.
* Using built-in documentation tools, you can provide documentation.
* When the script is run as a script tool, arcpy is fully aware of the application it was called from. Settings made in the application, such as arcpy.env.overwriteOutput and arcpy.env.scratchWorkspace, are available from ArcPy in your script tool.
Collection of tools and scripts that use arcpy.
