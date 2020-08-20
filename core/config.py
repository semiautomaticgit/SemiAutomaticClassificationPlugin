# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2018 by Luca Congedo
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
# training layer
shpLay = None
# training layer name
trnLay = None
# signature file path
sigFile= None
mskFlPath = ""
mskFlState = 0
# ROI click
clickROI = None
pntPrvw = None
lstROI = None
lstROI2 = None
sctrROIID = None
sctrROIID_h = {}
pntROI = None
origPoint = None
ROITime = None
lstPrvw = None
prvwSz = None
lastVrt = []
# band list
bndMdl = None
bndMdls = None
bndMdls2 = None
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
ROISigTypeNm = "B"
ROITypeNm = "R"
SIGTypeNm = "S"
tblOut = None
reportPth = None
errMtrxPth = None
bndSetMaskList = None
mnlROI = None
regionROI = None
allSignCheck = "No"
allSignCheck2 = "No"
allSignCheck3 = "No"
signList = {}
signIDs = {}
undoIDList = {}
undoSpectrPlotList = {}
ROI_SCP_UID = {}
MCID_List = {}
# spectral plot
spectrPlotList = {}
signPlotIDs = {}
scatterPlotIDs = {}
scatterPlotList = {}
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
ScatterTabEdited = "No"
ReclassTabEdited = "No"
# classification variables
# threshold
algThrshld = 0
# LC Signature threshold
tableMCID = "MC ID"
tableCID = "C ID"
tableMCInfo = "MC Info"
tableCInfo = "C Info"
tableColor = "Color [overlap MC_ID-C_ID]"
tableColor2 = "Color"
tableMin = "Min B"
tableMax = "Max B"
# set vector output variable
vectorOutputCheck = "No"
reportCheck = "No"
# raster band unique values
rasterBandUniqueVal = None
# raster band pixel count
rasterBandPixelCount = None
# raster pixel count for PCA
rasterPixelCountPCA = {}
# raster clustering
rasterClusteringrasterClustering = {}
# raster class signature
rasterClassSignature = {}
classSignatureNm = "Class signature"
# remaining time
remainingTime = 0
# set variable for standard deviation plot
sigmaCheck = "Yes"
# numpy
numpyn = "cfg.np."
# numpy logarithm
logn = "cfg.np.log"
# numpy logarithm
numpySqrt = "cfg.np.sqrt"
# numpy cos
numpyCos = "cfg.np.cos"
# numpy acos
numpyArcCos = "cfg.np.arccos"
# numpy sin
numpySin = "cfg.np.sin"
# numpy asin
numpyArcSin = "cfg.np.arcsin"
# numpy tan
numpyTan = "cfg.np.tan"
# numpy atan
numpyArcTan = "cfg.np.arctan"
# numpy exp
numpyExp = "cfg.np.exp"
# numpy pi
numpyPi = "cfg.np.pi"
# numpy where
numpyWhere = "cfg.np.where"
# land cover change variables	
unchngMaskCheck = True
# scatter plot variables
scatterBandX = 1
scatterBandY = 2
# fill plot
pF = []
# virtual raster
landsatVrtNm = "landsat"
sentinel2VrtNm = "sentinel2"
tmpVrtNm = "vrt_temp_"
bndSetVrtNm = "Virtual Band Set "
tmpVrt = None
# scp input directory
inptDir = None
scpFlPath = None
backupNm = "backup"
skipProjectSaved = "No"
# pixel signature names
pixelNm = "pixel"
pixelCoords = "Coords"
# temp ROI
tempROINm = "tempROI"
# temp scatter
tempScatterNm = "tempScatter"
# empty field name
emptyFN = "DN"
# band number variable
BLUEBand = None
REDBand = None
NIRBand = None
GREENBand = None
SWIR1Band = None
SWIR2Band = None
BLUECenterBand = 0.475
BLUEThreshold = 0.2
GREENCenterBand = 0.56
GREENThreshold = 0.03
REDCenterBand = 0.65
REDThreshold = 0.04
NIRCenterBand = 0.85
NIRThreshold = 0.15
SWIR1CenterBand = 1.61
SWIR1Threshold = 0.2
SWIR2CenterBand = 2.2
SWIR2Threshold = 0.2
# pansharpening type
IHS_panType = "Intensity-Hue-Saturation"
BT_panType = "Brovey Transform"
# contrast type
cumulativeCutContrast = "cumulativeCut"
stdDevContrast = "stdDev"
defaultContrast = cumulativeCutContrast
# settings
testGDALV = None
testMatplotlibV = None
testScipyV = None
testNumpyV = None
# debug
debugRasterPath = "/debug/roi_raster.tif"
absolutePath = False
ctrlClick = None
previewSliderActive = None
previewSliderArray = None
msgWar8check = "No"
lastSaveDir = ""
skipRegistry = True
# band calc
bandCalcIndex = 0
dockIndex = 0
# SCP kml name
kmlNm = "SCP_kml"

""" Project variables """
qmlFl = None
sigClcCheck = None
saveInputCheck = None
rpdROICheck = None
vegIndexCheck = None
multiAddFactorsVar = "multiplicativeAdditiveFactorsVar"
bandSetsList = []
bndSetNumber = 0
bndSetTabList = []
bndSetWidgetReset = "No"
rasterName = None
cmplClsNm = None
cmplMClsNm = None
ROIband = 1
maxROIWdth = 100
minROISz = 60
rngRad = 0.01
ROIID = 1
ROIInfo = "C 1"
ROIMacroClassInfo = "MC 1"
ROIMacroID = 1
customExpression = ""
# RGB list
RGBListDef = str(["-", "3-2-1", "4-3-2"])
RGBList = RGBListDef
# Landsat image database
LandsatImageDatabase = None
Landsat7OnImageDatabase = None
Landsat7OffImageDatabase = None
LandsatTM80ImageDatabase = None
LandsatTM90ImageDatabase = None
LandsatTM00ImageDatabase = None
LandsatTM10ImageDatabase = None
Landsat8ImageDatabase = None
LandsatTMImageDatabase2010 = None
RADIANCE_UNITS = None
expressionDict = {}

""" QGIS variables """
# registry key for first installation
regFirstInstall = "SemiAutomaticClassificationPlugin/firstInstall"
firstInstallVal = "Yes"
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
# registry key for download news
downNewsKey = "SemiAutomaticClassificationPlugin/downloadNews"
downNewsVal = "Yes"
# registry key for algorithm files
regAlgFiles = "SemiAutomaticClassificationPlugin/algFiles"
algFilesCheck = "No"
ROITrnspValDefault = 45
ROITrnspVal = ROITrnspValDefault
# registry key for temporary raster format
regTempRasterFormat = "SemiAutomaticClassificationPlugin/tempRastFormat"
# registry key for raster compression
regRasterCompression = "SemiAutomaticClassificationPlugin/rasterCompression"
# registry key for RAM value setting
regRAMValue = "SemiAutomaticClassificationPlugin/RAMValue"
RAMValue = 512
# smtp server
regSMTPCheck = "SemiAutomaticClassificationPlugin/SMTPCheck"
SMTPCheck = "Yes"
regSMTPServer = "SemiAutomaticClassificationPlugin/SMTPServer"
SMTPServer = ""
regSMTPtoEmails = "SemiAutomaticClassificationPlugin/SMTPtoEmails"
SMTPtoEmails = ""
regSMTPUser = "SemiAutomaticClassificationPlugin/SMTPUser"
SMTPUser = ""
regSMTPPassword = "SemiAutomaticClassificationPlugin/SMTPPassword"
SMTPPassword = ""
# field names for shapefile
regIDFieldName = "SemiAutomaticClassificationPlugin/IDFieldName"
# registry key for temporary directory
regTmpDir = "SemiAutomaticClassificationPlugin/TmpDir"
regUSGSUser = "SemiAutomaticClassificationPlugin/USGSUser"
USGSUser = ""
regUSGSPass= "SemiAutomaticClassificationPlugin/USGSPass"
USGSPass = ""
regUSGSUserASTER = "SemiAutomaticClassificationPlugin/USGSUserASTER"
USGSUserASTER = ""
regUSGSPassASTER = "SemiAutomaticClassificationPlugin/USGSPassASTER"
USGSPassASTER = ""
regSciHubUser = "SemiAutomaticClassificationPlugin/SciHubUser"
SciHubUser = ""
regSciHubService = "SemiAutomaticClassificationPlugin/SciHubService_5_2"
SciHubServiceNm = "https://scihub.copernicus.eu/apihub"
SciHubService = SciHubServiceNm
regSciHubPass = "SemiAutomaticClassificationPlugin/SciHubPass"
SciHubPass = ""
fldMacroID_class_def = "MC_ID"
fldID_class_def = "C_ID"
fldROI_info_def = "C_info"
fldROIMC_info_def = "MC_info"
ROI_Size_info_def = "ROI_size"
fldSCP_UID_def= "SCP_UID"
variableName_def = "raster"
vectorVariableName_def = "vector"
variableBandsetName_def = "bandset"
variableBlueName_def = "#BLUE#"
variableGreenName_def = "#GREEN#"
variableRedName_def = "#RED#"
variableNIRName_def = "#NIR#"
variableSWIR1Name_def = "#SWIR1#"
variableSWIR2Name_def = "#SWIR2#"
variableOutputNameBandset_def = "#BANDSET#"
variableOutputNameDate_def = "#DATE#"
merged_name = "merged_"
fldID_class = fldID_class_def
# macroclass ID
regMacroIDFieldName = "SemiAutomaticClassificationPlugin/MCIDFieldName"
fldMacroID_class = fldMacroID_class_def
# macroclass check
regConsiderMacroclass = "SemiAutomaticClassificationPlugin/ConsiderMacroclass"
macroclassCheck = "No"
# LCS
regLCSignature = "SemiAutomaticClassificationPlugin/LCSignature"
LCsignatureCheckBox = "No"
# info field
regInfoFieldName = "SemiAutomaticClassificationPlugin/InfoFieldName"
regMCInfoFieldName = "SemiAutomaticClassificationPlugin/MCInfoFieldName"
fldROI_info = fldROI_info_def
fldROIMC_info = fldROIMC_info_def
ROI_Size_info = ROI_Size_info_def
fldSCP_UID = fldSCP_UID_def
# variable name
regVariableName = "SemiAutomaticClassificationPlugin/VariableName"
variableName = variableName_def
# variable name
regVectorVariableName = "SemiAutomaticClassificationPlugin/vectorVariableName"
vectorVariableName = vectorVariableName_def
# variable band set name
regVariableBandsetName = "SemiAutomaticClassificationPlugin/VariableBandsetName"
variableBandsetName = variableBandsetName_def
variableBlueName = variableBlueName_def
variableGreenName = variableGreenName_def
variableRedName = variableRedName_def
variableNIRName = variableNIRName_def
variableSWIR1Name = variableSWIR1Name_def
variableSWIR2Name = variableSWIR2Name_def
variableOutputNameBandset = variableOutputNameBandset_def
variableOutputNameDate = variableOutputNameDate_def
# band set name
regBandSetName = "SemiAutomaticClassificationPlugin/BandSetName"
bandSetName = "Band set "
# plot variables
#regRoundCharList = "SemiAutomaticClassificationPlugin/roundCharList"
roundCharList = 15
# group name for temp ROI and Preview
regGroupName = "SemiAutomaticClassificationPlugin/groupName"
grpNm_def = "Class_temp_group"
grpNm = grpNm_def
lastPrev = None
lastScattRaster = None
prevList = []
# clip prefix
clipNm = "clip"
# output temp raster format
outTempRastFormat = "GTiff"
rasterCompression = "Yes"
# raster data type
regRasterDataType = "SemiAutomaticClassificationPlugin/rasterDataTypeNew"
rasterDataType = "Float32"
# raster data type
regExpressionListBC= "SemiAutomaticClassificationPlugin/expressionListBC"
expressionListBCbase = [['NDVI', '( "#NIR#" - "#RED#" ) / ( "#NIR#" + "#RED#" ) @NDVI'], ['EVI', '2.5 * ( "#NIR#" - "#RED#" ) / ( "#NIR#" + 6 * "#RED#" - 7.5 * "#BLUE#" + 1) @EVI'], ['NBR', '( "#NIR#" - "#SWIR2#" ) / ( "#NIR#" + "#SWIR2#" )  @NBR']]
expressionListBC = expressionListBCbase

""" Names """
uncls = "Unclassified"
clasfd = "Classified"
overlap = "Class Overlap"
algRasterNm = "alg_raster"
classRasterNm = "class_raster"
calcRasterNm = "calc_raster"
scatterRasterNm = "scatter_raster"
polyRasterNm = "polyr_raster"
stackRasterNm = "stack_raster"
virtualRasterNm = "virt_rast"
errMatrixNm = "_error_matrix.csv"
crossClassNm = "_cross_classification.csv"
PCANm = "PCA_band_"
PCAReportNm = "PCA_report.txt"
kmeansNm = "kmeans_"
kmeansReportNm = "kmeans_report.txt"
tempMtrxNm = "tmp_error_matrix"
reportNm = "_report.csv"
sigRasterNm = "sig"
prvwTempNm = "previewtemp.tif"
rclssTempNm = "temporary_ref_reclass"
bsCombTempNm = "temporary_band_set_comb"
maskRasterNm = "mskRstr.tif"
subsROINm = "subset_ROI_temp.tif"
subsTmpRaster = "subset_temp_b"
subsTmpROI = "ROI_tmp_copy"
copyTmpROI = "ROI_rast_temp"
tmpRegionNm = "region_temp"
tmpROINm = "temp_ROI"
mapExtent = '"Map extent"'
pixelExtent = '"Pixel extent"'
splitBndNm = "splitBand_"
spectralDistNm = "SpectralDistanceBandSets_"
reflectanceRasterNm = "reflectance_temp"
NoDataVal = -999
unclassifiedVal = -1000
maxLikeNoDataVal = -999999999900000
maxValDt = 999999999900000
unclassValue = None
referenceLayer = None
prvwSz = 200
# alg name
algName = "Minimum Distance"
kmeansAlgName = "Minimum Distance"
algLCS = "Land Cover Signature"
algKmeans = "K-means"
algISODATA = "ISODATA"
# type of conversion
convCenterPixels = "Center of pixels"
convAllPixelsTouch ="All pixels touched"
#index name
indName = "NDVI"
indNDVI = "NDVI"
indEVI = "EVI"
indCustom = "Custom"
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
# list of satellites for wavelength
NoSatellite = "Band order"
satGeoEye1 = "GeoEye-1 [bands 1, 2, 3, 4]"
satLandsat8 = "Landsat 8 OLI [bands 2, 3, 4, 5, 6, 7]"
satLandsat7 = "Landsat 7 ETM+ [bands 1, 2, 3, 4, 5, 7]"
satLandsat45 = "Landsat 4-5 TM [bands 1, 2, 3, 4, 5, 7]"
satLandsat13 = "Landsat 1-3 MSS [bands 4, 5, 6, 7]"
satRapidEye = "RapidEye [bands 1, 2, 3, 4, 5]"
satSentinel2 = "Sentinel-2 [bands 2, 3, 4, 5, 6, 7, 8, 8A, 11, 12]"
satSentinel3 = "Sentinel-3 [bands 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]"
satASTER = "ASTER [bands 1, 2, 3N, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]"
satMODIS = "MODIS [bands 3, 4, 1, 2, 5, 6, 7]"
satMODIS2 = "MODIS [bands 1, 2]"
satSPOT4 = "SPOT 4 [bands 1, 2, 3, 4]"
satSPOT5 = "SPOT 5 [bands 1, 2, 3, 4]"
satSPOT6 = "SPOT 6 [bands 1, 2, 3, 4]"
satPleiades = "Pleiades [bands 1, 2, 3, 4]"
satQuickBird = "QuickBird [bands 1, 2, 3, 4]"
satWorldView23 = "WorldView-2 -3 Multispectral [bands 1, 2, 3, 4, 5, 6, 7, 8]"
satWlList = ["", NoSatellite, satASTER, satGeoEye1, satLandsat8, satLandsat7, satLandsat45, satLandsat13, satMODIS, satMODIS2, satPleiades, satQuickBird, satRapidEye, satSentinel2, satSentinel3, satSPOT4, satSPOT5, satSPOT6, satWorldView23]
usgsLandsat8 = "L8 OLI/TIRS"
usgsLandsat7 = "L7 ETM+"
usgsLandsat45 = "L4-5 TM"
usgsLandsat15 = "L1-5 MSS"
esaSentinel2 = "Sentinel-2"
esaSentinel3 = "Sentinel-3"
usgsASTER = "ASTER Level 1T"
usgsMODIS_MOD09GQ = "MOD09GQ_V6"
usgsMODIS_MYD09GQ = "MYD09GQ_V6"
usgsMODIS_MOD09GA = "MOD09GA_V6"
usgsMODIS_MYD09GA = "MYD09GA_V6"
usgsMODIS_MOD09Q1 = "MOD09Q1_V6"
usgsMODIS_MYD09Q1 = "MYD09Q1_V6"
usgsMODIS_MOD09A1 = "MOD09A1_V6"
usgsMODIS_MYD09A1 = "MYD09A1_V6"
usgsLandsat8Collection = "12864"
usgsLandsat7Collection = "12267"
usgsLandsat45Collection = "12266"
usgsLandsat15Collection = "3120"
usgsASTERCollection = "9380"
NASAMOD09GQCollection = "C193529903-LPDAAC_ECS"
NASAMYD09GQCollection = "C193529460-LPDAAC_ECS"
NASAMOD09GACollection = "C193529902-LPDAAC_ECS"
NASAMYD09GACollection = "C193529459-LPDAAC_ECS"
NASAMOD09Q1Collection = "C193529944-LPDAAC_ECS"
NASAMYD09Q1Collection = "C193529461-LPDAAC_ECS"
NASAMOD09A1Collection = "C193529899-LPDAAC_ECS"
NASAMYD09A1Collection = "C193529457-LPDAAC_ECS"
NASAASTERCollection = "C1000000320-LPDAAC_ECS"
NASALandsat8Collection = "C1427461962-USGS_EROS"
NASALandsat7Collection = "C1427459680-USGS_EROS"
NASALandsat45Collection = "C1427462674-USGS_EROS"
NASALandsat15Collection = "C179872798-USGS_EROS"
satSentinelList = [esaSentinel2]
satSentinel3List = [esaSentinel3]
satLandsatList = [usgsLandsat8, usgsLandsat7, usgsLandsat45, usgsLandsat15]
satASTERtList = [usgsASTER]
satMODIStList = [usgsMODIS_MOD09GQ, usgsMODIS_MYD09GQ, usgsMODIS_MOD09GA, usgsMODIS_MYD09GA, usgsMODIS_MOD09Q1, usgsMODIS_MYD09Q1, usgsMODIS_MOD09A1, usgsMODIS_MYD09A1]
downProductList = satSentinelList + satSentinel3List + satLandsatList + satASTERtList + satMODIStList
indNDVI = "NDVI"
indEVI = "EVI"
indicesList = ["", indNDVI, indEVI]
# unit list
noUnit = "band number"
wlMicro = "µm (1 E-6m)"
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

""" Batch """
workingDirNm = "!working_dir!"
workingDir = None
functionNames = []
functionNames.append([['accuracy', 'cfg.batchT.performAccuracy',  'cfg.acc.errorMatrix', ["classification_file_path : ''", "reference_file_path : ''", "vector_field_name : ''", "output_raster_path : ''"]]])
functionNames.append([['add_new_bandset', 'cfg.batchT.performAddNewBandSet',  'cfg.bst.addBandSetTab', [""]]])
functionNames.append([['add_raster', 'cfg.batchT.performAddRaster',  'cfg.utls.addRasterLayer', ["input_raster_path : ''", "input_raster_name : ''"]]])
functionNames.append([['aster_conversion', 'cfg.batchT.performASTERConversion', 'cfg.ASTERT.ASTER', ["input_raster_path : ''", "celsius_temperature : 0", "apply_dos1 : 0", "dos1_only_green : 1", "use_nodata : 1", "nodata_value : 0", "create_bandset : 1", "output_dir : ''", "band_set : 1"]]])
functionNames.append([['band_calc', 'cfg.batchT.performBandCalc',  'cfg.bCalc.calculate', ["expression : ''", "output_raster_path : ''", "extent_same_as_raster_name : ''", "align : 1", "extent_intersection : 1", "set_nodata : 0", "nodata_value : 0", "band_set : 1"]]])
functionNames.append([['band_combination', 'cfg.batchT.performBandCombination',  'cfg.bsComb.bandSetCombination', ["band_set : 1", "output_raster_path : ''"]]])
functionNames.append([['class_signature', 'cfg.batchT.performClassSignature',  'cfg.classSigT.calculateClassSignature', ["input_raster_path : ''", "band_set : 1", "save_signatures : 1", "output_text_path : ''"]]])
functionNames.append([['classification', 'cfg.batchT.performClassification', 'cfg.SCPD.runClassification', ["band_set : 1", "use_macroclass : 0", "algorithm_name  : 'Minimum Distance'", "use_lcs : 0", "use_lcs_algorithm : 0", "use_lcs_only_overlap : 0", "apply_mask : 0",  "mask_file_path : ''", "vector_output : 0",  "classification_report : 0",  "save_algorithm_files : 0", "output_classification_path : ''"]]])
functionNames.append([['classification_dilation', 'cfg.batchT.performClassificationDilation', 'cfg.dltnRstr.dilationClassification', ["input_raster_path : ''", "class_values : ''", "size_in_pixels : 1", "pixel_connection : 4", "output_raster_path : ''"]]])
functionNames.append([['classification_erosion', 'cfg.batchT.performClassificationErosion', 'cfg.ersnRstr.erosionClassification', ["input_raster_path : ''", "class_values : ''", "size_in_pixels : 1", "pixel_connection : 4", "output_raster_path : ''"]]])
functionNames.append([['classification_report', 'cfg.batchT.performClassificationReport',  'cfg.classRep.calculateClassificationReport', ["input_raster_path : ''", "use_nodata : 0", "nodata_value : 0", "output_report_path : ''"]]])
functionNames.append([['classification_sieve', 'cfg.batchT.performClassificationSieve',  'cfg.sieveRstr.sieveClassification', ["input_raster_path : ''", "size_threshold : 2", "pixel_connection : 4", "output_raster_path : ''"]]])
functionNames.append([['classification_to_vector', 'cfg.batchT.performClassificationToVector', 'cfg.classVect.convertClassificationToVector', ["input_raster_path : ''", "use_signature_list_code : 1", "code_field : 'C_ID'", "output_vector_path : ''"]]]) 
functionNames.append([['clip_multiple_rasters', 'cfg.batchT.performClipRasters',  'cfg.clipMulti.clipRasters', ["band_set : 1", "output_dir : ''", "use_vector : 0", "vector_path : ''", "use_vector_field : 0", "vector_field : ''", "ul_x : ''", "ul_y : ''", "lr_x : ''", "lr_y : ''", "nodata_value : 0", "output_name_prefix : 'clip'"]]])
functionNames.append([['cloud_masking', 'cfg.batchT.performCloudMasking',  'cfg.cloudMsk.cloudMaskingBandSet', ["band_set : 1", "input_raster_path : ''", "class_values : ''", "use_buffer : 1", "size_in_pixels : 1", "nodata_value : 0", "output_name_prefix : 'mask'", "output_dir : ''"]]])
functionNames.append([['clustering', 'cfg.batchT.performClustering',  'cfg.clusteringT.calculateClustering', ["band_set : 1","clustering_method : 1", "use_distance_threshold : 1", "threshold_value : 0.0001", "number_of_classes : 10", "max_iterations : 10", "isodata_max_std_dev : 0.0001", "isodata_min_class_size : 10", "use_nodata : 0", "nodata_value : 0", "seed_signatures : 1", "distance_algorithm : 1", "save_signatures : 0", "output_raster_path : ''"]]])
functionNames.append([['create_bandset', 'cfg.batchT.performBandSetCreation',  'cfg.bst.addFileToBandSet', ["raster_path_list : ''", "center_wavelength : ''", "wavelength_unit : 1", "multiplicative_factor : ''", "additive_factor : ''"]]])
functionNames.append([['cross_classification', 'cfg.batchT.performCrossClassification',  'cfg.crossC.crossClassification', ["classification_file_path : ''", "use_nodata : 0", "nodata_value : 0", "reference_file_path : ''", "vector_field_name : ''", "output_raster_path : ''"]]])
functionNames.append([['edit_raster_using_vector', 'cfg.batchT.performEditRasterUsingVector', 'cfg.editRstr.setRasterValue', ["input_raster_path : ''", "input_vector_path : ''", "vector_field_name : ''", "constant_value : 0", "expression :  'where(raster == 1, 2, raster)'"]]])
functionNames.append([['land_cover_change', 'cfg.batchT.performLandCoverChange',  'cfg.landCC.landCoverChange', ["reference_raster_path : ''", "new_raster_path : ''", "output_raster_path : ''"]]])
functionNames.append([['landsat_conversion', 'cfg.batchT.performLandsatConversion',  'cfg.landsatT.landsat', ["input_dir : ''", "mtl_file_path : ''", "celsius_temperature : 0", "apply_dos1 : 0", "dos1_only_blue_green : 1", "use_nodata : 1", "nodata_value : 0", "pansharpening : 0", "create_bandset : 1", "output_dir : ''", "band_set : 1"]]])
functionNames.append([['modis_conversion', 'cfg.batchT.performMODISConversion', 'cfg.MODIST.MODIS', ["input_raster_path : ''", "reproject_wgs84 : 1", "use_nodata : 1", "nodata_value : -999", "create_bandset : 1", "output_dir : ''", "band_set : 1"]]])
functionNames.append([['mosaic_bandsets', 'cfg.batchT.performMosaicBandSets', 'cfg.mosaicBS.mosaicBandSets', ["band_set_list : ''", "output_dir : ''", "output_name_prefix : 'mosaic'"]]])
functionNames.append([['open_training_input', 'cfg.batchT.performOpenTrainingInput',  'cfg.SCPD.openInput', ["training_file_path : ''"]]])
functionNames.append([['pca', 'cfg.batchT.performPCA',  'cfg.pcaT.calculatePCA', ["band_set : 1", "use_number_of_components : 0", "number_of_components : 2", "use_nodata : 1", "nodata_value : 0", "output_dir : ''"]]])
functionNames.append([['reclassification', 'cfg.batchT.performReclassification', 'cfg.reclassification.reclassify', ["input_raster_path : ''", "value_list : 'oldVal_newVal,oldVal_newVal'", "use_signature_list_code : 1", "code_field : 'MC_ID'", "output_raster_path : ''"]]])
functionNames.append([['remove_bandset', 'cfg.batchT.performRemoveBandSet',  'cfg.bst.removeBandSetTab', ["band_set : 1"]]])
functionNames.append([['select_bandset', 'cfg.batchT.performBandSetSelection',  'cfg.bst.selectBandSetTab', ["band_set : 1"]]])
functionNames.append([['sentinel2_conversion', 'cfg.batchT.performSentinel2Conversion', 'cfg.sentinel2T.sentinel2', ["input_dir : ''", "mtd_safl1c_file_path : ''", "apply_dos1 : 0", "dos1_only_blue_green : 1", "use_nodata : 1", "nodata_value : 0", "create_bandset : 1", "output_dir : ''", "band_set : 1"]]])
functionNames.append([['sentinel3_conversion', 'cfg.batchT.performSentinel3Conversion', 'cfg.sentinel3T.sentinel3', ["input_dir : ''", "apply_dos1 : 0", "dos1_only_blue_green : 1", "use_nodata : 1", "nodata_value : 0", "create_bandset : 1", "output_dir : ''", "band_set : 1"]]])
functionNames.append([['spectral_distance', 'cfg.batchT.performSpectralDistance', 'cfg.spclDstBS.spectralDistBandSets', ["first_band_set : 1", "second_band_set : 2", "distance_algorithm  : 1", "use_distance_threshold : 1", "threshold_value : 0.1", "output_dir : ''"]]])
functionNames.append([['split_raster_bands', 'cfg.batchT.performSplitRaster', 'cfg.splitT.splitRasterToBands', ["input_raster_path : ''", "output_dir : ''", "output_name_prefix : 'split'"]]])
functionNames.append([['stack_raster_bands', 'cfg.batchT.performStackRaster', 'cfg.stackRstr.stackRasters', ["band_set : 1", "output_raster_path : ''"]]])
functionNames.append([['vector_to_raster', 'cfg.batchT.performVectorToRaster', 'cfg.vctRstrT.convertToRaster', ["vector_file_path : ''", "use_value_field : 1", "vector_field_name : ''", "constant_value : 1", "reference_raster_path : ''",  "type_of_conversion : 'Center of pixels'", "output_raster_path : ''"]]])
functionNames.append([[workingDirNm, 'cfg.batchT.workingDirectory', '', ["''"]]])

""" Scatter plot """
scatterColorMap = ['rainbow', 'gist_rainbow', 'jet', 'afmhot', 'bwr', 'gnuplot', 'gnuplot2', 'BrBG', 'coolwarm', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'seismic', 'ocean', 'terrain', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']

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