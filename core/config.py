# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin
								 A QGIS plugin
 A plugin which allows for the semi-automatic supervised classification of remote sensing images, 
 providing a tool for the region growing of image pixels, creating polygon shapefiles intended for
 the collection of training areas (ROIs), and rapidly performing the classification process (or a preview).
							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012 by Luca Congedo
		email				: ing.congedoluca@gmail.com
**************************************************************************************************************************/
 
/**************************************************************************************************************************
 *
 * This file is part of Semi-Automatic Classification Plugin
 * 
 * Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License as published by the Free Software Foundation, 
 * version 3 of the License.
 * 
 * Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 * FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
 * 
**************************************************************************************************************************/

"""

""" Init """
iface = None
cnvs = None
mainAction = None
# main interface
ui = None
dlg = None
# roi dock
uid = None
dockdlg = None
# classification dock
uidc = None
dockclassdlg = None
# spectral signature plot
uisp = None
# welcome
wlcmdlg = None
spectralplotdlg = None
SpectralSignaturePlot = None
scatterplotdlg = None
uiscp = None
# USGS spectral Library
usgsLib = None
# input
ipt = None
# legend
lgnd = None
# plugin dir
plgnDir = None
# temp dir
tmpDir = None
tmpExtDir = None
# messages
mx = None
# utils
utls = None
# ui utils
uiUtls = None
# accuracy
acc = None
# system platform
sys64bit = None
sysNm = None
gdalPath = ""
# signature importer
sigImport = None
QGISVer = None
sysInfo = None
scipyCheck = None
actionCheck = "No"
progressBar = None
fSEnc = None
logFile = None
toolPan = None
pntCheck = None
lstPnt = None
imgNm = None
rLay = None
shpLay = None
trnLay = None
mskFlPath = ""
mskFlState = 0
# ROI click
clickROI = None
pntPrvw = None
lstROI = None
pntROI = None
lstPrvw = None
prvwSz = None
lastVrt = []
# band list
bndMdl = None
bndMdls = None
newClssfctnNm = None
refClssfctnNm = None
rbbrBnd = None
ROISigNm = None
ROI_MC_ID = None
ROI_MC_Info = None
ROI_C_ID = None
ROI_C_Info = None
ROI_Count = None
ROI_ShapeID = None
tblOut = None
reportPth = None
errMtrxPth = None
bndSetMaskList = None
mnlROI = None
allSignCheck = "No"
signList = {}
signIDs = {}
# spectral plot
spectrPlotList = {}
signPlotIDs = {}
# set classification path
clssPth = None
arrayUnitMemory = 0.000016
tableColString = "ID"
ROITabEdited = "No"
SigTabEdited = "No"
# classification variables
# threshold
algThrshld = 0
# set vector output variable
vectorOutputCheck = "No"
reportCheck = "No"
# raster band unique values
rasterBandUniqueVal = None
# raster pixel sum
rasterPixelSum = 0
# remaining time
remainingTime = 0
# set variable for standard deviation plot
sigmaCheck = "No"
# numpy logarithm
logn = "np.log"
# land cover change variables	
unchngMaskCheck = True
# scatter plot variables
scatterBandX = 1
scatterBandY = 2
# fill plot
pF = []
# virtual raster
landsatVrtNm = "landsat"
# empty field name
emptyFN = "DN"

""" Project variables """
qmlFl = None
sigClcCheck = None
rpdROICheck = None
bndSet = {}
bndSetWvLn = {}
bndSetPresent = None
rasterName = None
cmplClsNm = None
cmplMClsNm = None
ROIband = 1
maxROIWdth = 100
minROISz = 60
rngRad = 0.01
ROIID = 1
ROIInfo = "Class_1"
ROIMacroClassInfo = "Macroclass_1"
ROIMacroID = 1

""" QGIS variables """
# registry key for log setting
regLogKey = "SemiAutomaticClassificationPlugin/logSetting"
logSetVal = "No"
# registry key for sound
regSound = "SemiAutomaticClassificationPlugin/useSound"
soundVal = "Yes"
# registry key for ROI color setting
regROIClr = "SemiAutomaticClassificationPlugin/ROIColour"
ROIClrVal = "#ffaa00"
# registry key for ROI transparency setting
regROITransp = "SemiAutomaticClassificationPlugin/ROITransparency"
# registry key for algorithm files
regAlgFiles = "SemiAutomaticClassificationPlugin/algFiles"
algFilesCheck = "No"
ROITrnspVal = 20
# registry key for RAM value setting
regRAMValue = "SemiAutomaticClassificationPlugin/RAMValue"
RAMValue = 512
# field names for shapefile
regIDFieldName = "SemiAutomaticClassificationPlugin/IDFieldName"
fldID_class = "C_ID"
# macroclass ID
regMacroIDFieldName = "SemiAutomaticClassificationPlugin/MCIDFieldName"
fldMacroID_class = "MC_ID"
# macroclass check
regConsiderMacroclass = "SemiAutomaticClassificationPlugin/ConsiderMacroclass"
macroclassCheck = "No"
# info field
regInfoFieldName = "SemiAutomaticClassificationPlugin/InfoFieldName"
regMCInfoFieldName = "SemiAutomaticClassificationPlugin/MCInfoFieldName"
fldROI_info = "C_info"
fldROIMC_info = "MC_info"
# band set name
regBandSetName = "SemiAutomaticClassificationPlugin/BandSetName"
bndSetNm = "<< band set >>"
# plot variables
regRoundCharList = "SemiAutomaticClassificationPlugin/roundCharList"
roundCharList=25
# group name for temp ROI and Preview
regGroupName = "SemiAutomaticClassificationPlugin/groupName"
grpNm = "Class_temp_group"
# clip prefix
clipNm = "clip"

""" Names """
uncls = "Unclassified"
algRasterNm = "alg_raster"
errMatrixNm = "_error_matrix.csv"
tempMtrxNm = "tmp_error_matrix"
reportNm = "_report.csv"
sigRasterNm = "sig"
prvwTempNm = "previewtemp.tif"
rclssTempNm = "temporary_ref_reclass"
maskRasterNm = "mskRstr.tif"
subsROINm = "subset_ROI_temp.tif"
subsTmpRaster = "subset_temp_b"
subsTmpROI = "ROI_tmp_copy"
copyTmpROI = "ROI_rast_temp"
tmpRegionNm = "region_temp"
reflectanceRasterNm = "reflectance_temp"
NoDataVal = -999
maxLikeNoDataVal = -999999999900000
referenceLayer = None
rstrNm = None
# alg name
algName = "Minimum Distance"
algMinDist = "Minimum Distance"
algML = "Maximum Likelihood"
algSAM = "Spectral Angle Mapping"
# set mask variable
maskCheck = "No"
# prefix for ROI signature fields
ROIFieldMean = "ROIm_b"
ROISigma = "ROIs_b"
ROINBands = "ROI_NBands"

""" band set """
bndSetUnit = None
# list of satellites for wavelength
NoSatellite = "Band order"
satLandsat8 = "Landsat 8 OLI [bands 2, 3, 4, 5, 6, 7]"
satLandsat7 = "Landsat 7 ETM+ [bands 1, 2, 3, 4, 5, 7]"
satLandsat45 = "Landsat 4-5 TM [bands 1, 2, 3, 4, 5, 7]"
satRapidEye = "RapidEye [bands 1, 2, 3, 4, 5]"
satSPOT4 = "SPOT 4 [bands 1, 2, 3, 4]"
satSPOT5 = "SPOT 5 [bands 1, 2, 3, 4]"
satSPOT6 = "SPOT 6 [bands 1, 2, 3, 4]"
satPleiades = "Pleiades [bands 1, 2, 3, 4]"
satQuickBird = "QuickBird [bands 1, 2, 3, 4]"
satWlList = ["", NoSatellite, satLandsat8, satLandsat7, satLandsat45, satPleiades, satQuickBird, satRapidEye, satSPOT4, satSPOT5, satSPOT6]
# unit list
noUnit = "band number"
wlMicro = u"µm (1 E-6m)"
wlNano = "nm (1 E-9m)"
unitNano = "E-9m"
unitMicro = "E-6m"
unitList = [noUnit, wlMicro, wlNano]
BandTabEdited = "Yes"
rasterComboEdited = "Yes"
tempDirName = "semiautomaticclassification"
# USGS spectral library
usgs_C1 = "Chapter 1: Minerals"
usgs_C2 = "Chapter 2: Mixtures"
usgs_C3 = "Chapter 3: Coatings"
usgs_C4 = "Chapter 4: Volatiles"
usgs_C5 = "Chapter 5: Man-Made"
usgs_C6 = "Chapter 6: Plants, Vegetation Communities, Mixtures with Vegetation, and Microorganisms"
usgs_lib_list = ["", usgs_C1,usgs_C2,usgs_C3,usgs_C4,usgs_C5,usgs_C6]
usgs_C1p = None
usgs_C2p = None
usgs_C3p = None
usgs_C4p = None
usgs_C5p = None
usgs_C6p = None

""" Input toolbar """
raster_name_combo = None
toolButton_reload = None
main_toolButton = None
bandset_toolButton = None
ROItools_toolButton = None
preprocessing_toolButton = None
postprocessing_toolButton = None
settings_toolButton = None
settings_toolButton = None