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
		copyright			: (C) 2012-2015 by Luca Congedo
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
menu = None
tools_menu = None
preprocessing_menu = None
postprocessing_menu = None
settings_menu = None
toolBar = None
projPath = ""
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
# GDAL path
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
origPoint = None
ROITime = None
lstPrvw = None
prvwSz = None
lastVrt = []
# band list
bndMdl = None
bndMdls = None
newClssfctnNm = None
refClssfctnNm = None
rbbrBnd = None
rbbrBndPol = None
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
regionROI = None
allSignCheck = "No"
signList = {}
signIDs = {}
# spectral plot
spectrPlotList = {}
signPlotIDs = {}
tmpROIID = None
tmpROIColor = None
# weights
algBandWeigths = {}
# set classification path
clssPth = None
arrayUnitMemory = 0.000016
tableColString = "ID"
ROITabEdited = "No"
SigTabEdited = "No"
ReclassTabEdited = "No"
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
# numpy logarithm
numpySqrt = "np.sqrt"
# numpy cos
numpyCos = "np.cos"
# numpy acos
numpyArcCos = "np.arccos"
# numpy sin
numpySin = "np.sin"
# numpy asin
numpyArcSin = "np.arcsin"
# numpy tan
numpyTan = "np.tan"
# numpy atan
numpyArcTan = "np.arctan"
# numpy exp
numpyExp = "np.exp"
# numpy pi
numpyPi = "np.pi"
# land cover change variables	
unchngMaskCheck = True
# scatter plot variables
scatterBandX = 1
scatterBandY = 2
# fill plot
pF = []
# virtual raster
landsatVrtNm = "landsat"
tmpVrtNm = "band_set"
tmpVrt = None
# pixel signature names
pixelNm = "pixel"
pixelCoords = "Coords"
# empty field name
emptyFN = "DN"
# band number variable
BLUEBand = None
REDBand = None
NIRBand = None
BLUECenterBand = 0.475
BLUEThreshold = 0.2
REDCenterBand = 0.65
REDThreshold = 0.04
NIRCenterBand = 0.85
NIRThreshold = 0.15
# settings
testGDALV = None
testMatplotlibV = None
testScipyV = None
testNumpyV = None
# debug
debugRasterPath = "/debug/roi_raster.tif"
absolutePath = False

""" Project variables """
qmlFl = None
sigClcCheck = None
rpdROICheck = None
vegIndexCheck = None
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
# RGB list
RGBList = str(["-", "3-2-1", "4-3-2"])
# Landsat image database
LandsatImageDatabase = None

""" QGIS variables """
# registry key for log setting
regLogKey = "SemiAutomaticClassificationPlugin/logSetting"
logSetVal = "No"
# registry key for sound
regSound = "SemiAutomaticClassificationPlugin/useSound"
soundVal = "Yes"
# registry key for ROI color setting
regROIClr = "SemiAutomaticClassificationPlugin/ROIColour"
ROIClrValDefault = "#ffaa00"
ROIClrOutlineValDefault = "#53d4e7"
ROIClrVal = ROIClrValDefault
# registry key for ROI transparency setting
regROITransp = "SemiAutomaticClassificationPlugin/ROITransparency4"
# registry key for algorithm files
regAlgFiles = "SemiAutomaticClassificationPlugin/algFiles"
algFilesCheck = "No"
ROITrnspValDefault = 45
ROITrnspVal = ROITrnspValDefault
# registry key for temporary raster format
regTempRasterFormat = "SemiAutomaticClassificationPlugin/tempRastFormat"
# registry key for RAM value setting
regRAMValue = "SemiAutomaticClassificationPlugin/RAMValue"
RAMValue = 512
# field names for shapefile
regIDFieldName = "SemiAutomaticClassificationPlugin/IDFieldName"
fldMacroID_class_def = "MC_ID"
fldID_class_def = "C_ID"
fldROI_info_def = "C_info"
fldROIMC_info_def = "MC_info"
variableName_def = "raster"
variableBandsetName_def = "bandset"
merged_name = "merged_"
fldID_class = fldID_class_def
# macroclass ID
regMacroIDFieldName = "SemiAutomaticClassificationPlugin/MCIDFieldName"
fldMacroID_class = fldMacroID_class_def
# macroclass check
regConsiderMacroclass = "SemiAutomaticClassificationPlugin/ConsiderMacroclass"
macroclassCheck = "No"
# info field
regInfoFieldName = "SemiAutomaticClassificationPlugin/InfoFieldName"
regMCInfoFieldName = "SemiAutomaticClassificationPlugin/MCInfoFieldName"
fldROI_info = fldROI_info_def
fldROIMC_info = fldROIMC_info_def
# variable name
regVariableName = "SemiAutomaticClassificationPlugin/VariableName"
variableName = variableName_def
# variable band set name
regVariableBandsetName = "SemiAutomaticClassificationPlugin/VariableBandsetName"
variableBandsetName = variableBandsetName_def
# band set name
regBandSetName = "SemiAutomaticClassificationPlugin/BandSetName"
bndSetNm = "<< band set >>"
# plot variables
regRoundCharList = "SemiAutomaticClassificationPlugin/roundCharList"
roundCharList = 25
# group name for temp ROI and Preview
regGroupName = "SemiAutomaticClassificationPlugin/groupName"
grpNm_def = "Class_temp_group"
grpNm = grpNm_def
# clip prefix
clipNm = "clip"
# output temp raster format
outTempRastFormat = "GTiff"

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
tmpROINm = "temp_ROI"
splitBndNm = "splitBand_"
reflectanceRasterNm = "reflectance_temp"
NoDataVal = -999
unclassifiedVal = -1000
maxLikeNoDataVal = -999999999900000
maxValDt = 999999999900000
referenceLayer = None
rstrNm = None
# alg name
algName = "Minimum Distance"
algMinDist = "Minimum Distance"
algML = "Maximum Likelihood"
algSAM = "Spectral Angle Mapping"
#index name
indName = "NDVI"
indNDVI = "NDVI"
indEVI = "EVI"
# set mask variable
maskCheck = "No"
# prefix for ROI signature fields
ROIFieldMean = "ROIm_b"
ROISigma = "ROIs_b"
ROINBands = "ROI_NBands"
# spectral plot
wavelenNm = "Wavelength"
valNm = "Values"
standDevNm = "Standard deviation"
# distances
euclideanDistNm = "Euclidean distance"
brayCurtisSimNm = "Bray-Curtis similarity [%]"
spectralAngleNm = "Spectral angle"
jeffriesMatusitaDistNm = "Jeffries-Matusita distance"
transformedDivergenceNm = "Transformed divergence"
notAvailable = "n/a"

""" band set """
bndSetUnit = None
# list of satellites for wavelength
NoSatellite = "Band order"
satGeoEye1 = "GeoEye-1 [bands 1, 2, 3, 4]"
satLandsat8 = "Landsat 8 OLI [bands 2, 3, 4, 5, 6, 7]"
satLandsat7 = "Landsat 7 ETM+ [bands 1, 2, 3, 4, 5, 7]"
satLandsat45 = "Landsat 4-5 TM [bands 1, 2, 3, 4, 5, 7]"
satRapidEye = "RapidEye [bands 1, 2, 3, 4, 5]"
satSPOT4 = "SPOT 4 [bands 1, 2, 3, 4]"
satSPOT5 = "SPOT 5 [bands 1, 2, 3, 4]"
satSPOT6 = "SPOT 6 [bands 1, 2, 3, 4]"
satPleiades = "Pleiades [bands 1, 2, 3, 4]"
satQuickBird = "QuickBird [bands 1, 2, 3, 4]"
satWorldView23 = "WorldView-2 -3 Multispectral [bands 1, 2, 3, 4, 5, 6, 7, 8]"
satWlList = ["", NoSatellite, satGeoEye1, satLandsat8, satLandsat7, satLandsat45, satPleiades, satQuickBird, satRapidEye, satSPOT4, satSPOT5, satSPOT6, satWorldView23]
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