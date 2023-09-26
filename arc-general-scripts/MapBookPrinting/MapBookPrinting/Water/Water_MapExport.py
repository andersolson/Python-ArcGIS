"""Water Map Books
export to PDFs,
including Detail
Sheets
07/26/18
"""


import arcpy, os

#Export Water By Status Data Driven Pages to PDF for selected Map Pages:

import_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_ByStatus.mxd"   # Path of .mxd
export_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Mapbook_ByStatus\Water_ByStatus"   # Path of output file
field_name = "MAP_NO" # Name of field used to sort DDP
pg_name = "MAP_NO" # Name of field used in PDF file name
 
mxd = arcpy.mapping.MapDocument(import_path) 
for i in(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,90,91,92,93,94,96,97,98,100,102,103,104,105,106,107,111,112,113,114,115,120,121,125,127,131,132,133,138,139,140,145,148,149,150,152,158,159,160,161,167,168,174,180,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248):
    mxd.dataDrivenPages.currentPageID = i
    row = mxd.dataDrivenPages.pageRow
    arcpy.mapping.ExportToPDF(mxd, export_path + "_" + row.getValue(pg_name) + ".pdf") 
del mxd

#Export Water By Zone Data Driven Pages to PDF for selected Map Pages:

import_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_ByZone.mxd"   # Path of .mxd
export_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Mapbook_ByZone\Water_ByZone"   # Path of output file
field_name = "MAP_NO" # Name of field used to sort DDP
pg_name = "MAP_NO" # Name of field used in PDF file name
 
mxd = arcpy.mapping.MapDocument(import_path) 
for i in(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,90,91,92,93,94,96,97,98,100,102,103,104,105,106,107,111,112,113,114,115,120,121,125,127,131,132,133,138,139,140,145,148,149,150,152,158,159,160,161,167,168,174,180,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248):
    mxd.dataDrivenPages.currentPageID = i
    row = mxd.dataDrivenPages.pageRow
    arcpy.mapping.ExportToPDF(mxd, export_path + "_" + row.getValue(pg_name) + ".pdf") 
del mxd

#Export Water By Material Data Driven Pages to PDF for selected Map Pages:

import_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_ByMaterial.mxd"   # Path of .mxd
export_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Mapbook_ByMaterial\Water_ByMaterial"   # Path of output file
field_name = "MAP_NO" # Name of field used to sort DDP
pg_name = "MAP_NO" # Name of field used in PDF file name
 
mxd = arcpy.mapping.MapDocument(import_path) 
for i in(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,90,91,92,93,94,96,97,98,100,102,103,104,105,106,107,111,112,113,114,115,120,121,125,127,131,132,133,138,139,140,145,148,149,150,152,158,159,160,161,167,168,174,180,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248):
    mxd.dataDrivenPages.currentPageID = i
    row = mxd.dataDrivenPages.pageRow
    arcpy.mapping.ExportToPDF(mxd, export_path + "_" + row.getValue(pg_name) + ".pdf") 
del mxd

#Export Water By PipesOnly Data Driven Pages to PDF for all Map Pages:

import_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_PipesOnly.mxd"   # Path of .mxd
export_path = r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Mapbook_PipesOnly\Water_PipesOnly"   # Path of output file
##field_name = "MAP_NO" # Name of field used to sort DDP
##pg_name = "MAP_NO" # Name of field used in PDF file name

mxd = arcpy.mapping.MapDocument(import_path)
mxd.dataDrivenPages.exportToPDF(export_path, "ALL", "", "PDF_MULTIPLE_FILES_PAGE_NAME")
del mxd
 
##mxd = arcpy.mapping.MapDocument(import_path) 
##for i in(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,90,91,92,93,94,96,97,98,100,102,103,104,105,106,107,111,112,113,114,115,120,121,125,127,131,132,133,138,139,140,145,148,149,150,152,158,159,160,161,167,168,174,180,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248):
##    mxd.dataDrivenPages.currentPageID = i
##    row = mxd.dataDrivenPages.pageRow
##    arcpy.mapping.ExportToPDF(mxd, export_path + "_" + row.getValue(pg_name) + ".pdf") 
##del mxd

#Export Water Detail sheets into By Material, By Status, and By Zone folders

arcpy.env.workspace = r"G:\Field_Assets\Water\MapBookPrinting\MXD"
arcpy.env.overwriteOutput = True

#List of mxds to loop thru
mxd_list = [r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Detail_Sheet_D1.mxd",
                r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Detail_Sheet_D2.mxd",
                r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Detail_Sheet_D3.mxd",
                r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Detail_Sheet_D4.mxd"]

#List of folders to export pdfs to
export_list = [r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Mapbook_ByMaterial\Detail_Sheets",
                   r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Mapbook_ByStatus\Detail_Sheets",
                   r"G:\Field_Assets\Water\MapBookPrinting\MXD\Water_Mapbook_ByZone\Detail_Sheets"]

#For each mxd export a pdf to each folder
try:
    for mxd in mxd_list:
        mxd = arcpy.mapping.MapDocument(mxd)
        for folder in export_list:
            arcpy.mapping.ExportToPDF(mxd, folder + '\\' + os.path.basename(mxd.filePath)[:-4] + '.pdf')

except:
    print(arcpy.GetMessages())
