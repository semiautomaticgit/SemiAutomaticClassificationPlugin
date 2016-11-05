# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2016 by Luca Congedo
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
bandsetCount = 0
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
tmpVrtNm = "band_set"
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
BLUECenterBand = 0.475
BLUEThreshold = 0.2
GREENCenterBand = 0.56
GREENThreshold = 0.03
REDCenterBand = 0.65
REDThreshold = 0.04
NIRCenterBand = 0.85
NIRThreshold = 0.15
# pansharpening type
IHS_panType = "Intensity-Hue-Saturation"
BT_panType = "Brovey Transform"
# contrast type
cumulativeCutContrast = "cumulativeCut"
stdDevContrast =  "stdDev"
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
msgWar8check = "No"
lastSaveDir = ""
# band calc
bandCalcIndex = 0

""" Project variables """
qmlFl = None
sigClcCheck = None
rpdROICheck = None
vegIndexCheck = None
bndSet = {}
bndSetWvLn = {}
bndSetMultiFactors = {}
bndSetAddFactors = {}
bndSetMultiFactorsList = []
bndSetAddFactorsList = []
bndSetMultAddFactorsList = []
multiAddFactorsVar = "multiplicativeAdditiveFactorsVar"
bndSetPresent = None
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
regUSGSPassASTER= "SemiAutomaticClassificationPlugin/USGSPassASTER"
USGSPassASTER = ""
regSciHubUser = "SemiAutomaticClassificationPlugin/SciHubUser"
SciHubUser = ""
regSciHubService = "SemiAutomaticClassificationPlugin/SciHubService2"
SciHubServiceNm = "https://scihub.copernicus.eu/dhus"
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
variableBandsetName_def = "bandset"
variableBlueName_def = "#BLUE#"
variableGreenName_def = "#GREEN#"
variableRedName_def = "#RED#"
variableNIRName_def = "#NIR#"
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
# variable band set name
regVariableBandsetName = "SemiAutomaticClassificationPlugin/VariableBandsetName"
variableBandsetName = variableBandsetName_def
variableBlueName = variableBlueName_def
variableGreenName = variableGreenName_def
variableRedName = variableRedName_def
variableNIRName = variableNIRName_def
# band set name
regBandSetName = "SemiAutomaticClassificationPlugin/BandSetName"
bndSetNm = "<< band set >>"
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
expressionListBCbase = [['NDVI', '( "#NIR#" - "#RED#" ) / ( "#NIR#" + "#RED#" ) @NDVI'], ['EVI', '2.5 * ( "#NIR#" - "#RED#" ) / ( "#NIR#" + 6 * "#RED#" - 7.5 * "#BLUE#" + 1) @EVI']]
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
PCANm = "PCA_band_"
PCAReportNm = "PCA_report.txt"
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
mapExtent = '"Map extent"'
pixelExtent = '"Pixel extent"'
splitBndNm = "splitBand_"
reflectanceRasterNm = "reflectance_temp"
NoDataVal = -999
unclassifiedVal = -1000
maxLikeNoDataVal = -999999999900000
maxValDt = 999999999900000
unclassValue = None
referenceLayer = None
rstrNm = None
prvwSz = 200
# alg name
algName = "Minimum Distance"
algLCS = "Land Cover Signature"
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
bndSetUnit = None
# list of satellites for wavelength
NoSatellite = "Band order"
satGeoEye1 = "GeoEye-1 [bands 1, 2, 3, 4]"
satLandsat8 = "Landsat 8 OLI [bands 2, 3, 4, 5, 6, 7]"
satLandsat7 = "Landsat 7 ETM+ [bands 1, 2, 3, 4, 5, 7]"
satLandsat45 = "Landsat 4-5 TM [bands 1, 2, 3, 4, 5, 7]"
satLandsat13 = "Landsat 1-3 MSS [bands 4, 5, 6, 7]"
satRapidEye = "RapidEye [bands 1, 2, 3, 4, 5]"
satSentinel2 = "Sentinel-2 [bands 2, 3, 4, 5, 6, 7, 8, 8A, 11, 12]"
satASTER = "ASTER [bands 1, 2, 3N, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]"
satSPOT4 = "SPOT 4 [bands 1, 2, 3, 4]"
satSPOT5 = "SPOT 5 [bands 1, 2, 3, 4]"
satSPOT6 = "SPOT 6 [bands 1, 2, 3, 4]"
satPleiades = "Pleiades [bands 1, 2, 3, 4]"
satQuickBird = "QuickBird [bands 1, 2, 3, 4]"
satWorldView23 = "WorldView-2 -3 Multispectral [bands 1, 2, 3, 4, 5, 6, 7, 8]"
satWlList = ["", NoSatellite, satASTER, satGeoEye1, satLandsat8, satLandsat7, satLandsat45, satLandsat13, satPleiades, satQuickBird, satRapidEye, satSentinel2, satSPOT4, satSPOT5, satSPOT6, satWorldView23]
usgsLandsat8 = "L8 OLI/TIRS"
usgsLandsat7 = "L7 ETM+"
usgsLandsat45 = "L4-5 TM"
usgsLandsat15 = "L1-5 MSS"
usgsASTER = "ASTER Level 1T"
usgsLandsat8Collection = "4923"
usgsLandsat7slcoffCollection = "3373"
usgsLandsat7slconCollection = "3372"
usgsLandsat45Collection = "3119"
usgsLandsat15Collection = "3120"
usgsASTERCollection = "9380"
NASAASTERCollection = "C1000000320-LPDAAC_ECS"
NASALandsat8Collection = "C185174181-USGS_EROS"
NASALandsat7Collection = "C179001725-USGS_EROS"
NASALandsat45Collection = "C179872799-USGS_EROS"
NASALandsat15Collection = "C179872798-USGS_EROS"
satLandsatList = [usgsLandsat8, usgsLandsat7, usgsLandsat45, usgsLandsat15]
satASTERtList = [usgsASTER]
indNDVI = "NDVI"
indEVI = "EVI"
indicesList = ["", indNDVI, indEVI]
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

""" Batch """
workingDirNm = "!working_dir!"
workingDir = None
functionNames = []
functionNames.append([['add_raster', 'cfg.batchT.performAddRaster',  'cfg.utls.addRasterLayer', ["input_raster_path : ''", "input_raster_name : ''"]]])
functionNames.append([['accuracy', 'cfg.batchT.performAccuracy',  'cfg.acc.errorMatrix', ["classification_file_path : ''", "reference_file_path : ''", "shapefile_field_name : ''", "output_raster_path : ''"]]])
functionNames.append([['aster_conversion', 'cfg.batchT.performASTERConversion', 'cfg.ASTERT.ASTER', ["input_raster_path : ''", "celsius_temperature : 0", "apply_dos1 : 0", "use_nodata : 1", "nodata_value : 0", "create_bandset : 1", "output_dir : ''"]]])
functionNames.append([['band_calc', 'cfg.batchT.performBandCalc',  'cfg.bCalc.calculate', ["expression : ''", "output_raster_path : ''", "extent_same_as_raster_name : ''", "align : 1", "extent_intersection : 1", "set_nodata : 0", "nodata_value : 0"]]])
functionNames.append([['classification', 'cfg.batchT.performClassification', 'cfg.classD.runClassification', ["use_macroclass : 0", "algorithm_name  : 'Minimum Distance'", "use_lcs : 0", "use_lcs_algorithm : 0", "use_lcs_only_overlap : 0", "apply_mask : 0",  "mask_file_path : ''", "vector_output : 0",  "classification_report : 0",  "save_algorithm_files : 0", "output_classification_path : ''"]]])
functionNames.append([['classification_dilation', 'cfg.batchT.performClassificationDilation', 'cfg.dltnRstr.dilationClassification', ["input_raster_path : ''", "class_values : ''", "size_in_pixels : 1", "pixel_connection : 4", "output_raster_path : ''"]]])
functionNames.append([['classification_erosion', 'cfg.batchT.performClassificationErosion', 'cfg.ersnRstr.erosionClassification', ["input_raster_path : ''", "class_values : ''", "size_in_pixels : 1", "pixel_connection : 4", "output_raster_path : ''"]]])
functionNames.append([['classification_report', 'cfg.batchT.performClassificationReport',  'cfg.classRep.calculateClassificationReport', ["input_raster_path : ''", "use_nodata : 0", "nodata_value : 0", "output_report_path : ''"]]])
functionNames.append([['classification_sieve', 'cfg.batchT.performClassificationSieve',  'cfg.sieveRstr.sieveClassification', ["input_raster_path : ''", "size_threshold : 2", "pixel_connection : 4", "output_raster_path : ''"]]])
functionNames.append([['classification_to_vector', 'cfg.batchT.performClassificationToVector', 'cfg.classVect.convertClassificationToVector', ["input_raster_path : ''", "use_signature_list_code : 1", "code_field : 'C_ID'", "output_vector_path : ''"]]]) 
functionNames.append([['clip_multiple_rasters', 'cfg.batchT.performClipRasters',  'cfg.clipMulti.clipRasters', ["input_raster_path : ''", "output_dir : ''", "use_shapefile : 0", "shapefile_path : ''", "ul_x : ''", "ul_y : ''", "lr_x : ''", "lr_y : ''", "nodata_value : 0", "output_name_prefix : 'clip'"]]])
functionNames.append([['create_bandset', 'cfg.batchT.performBandSetCreation',  'cfg.bst.addFileToBandSet', ["raster_path_list : ''", "center_wavelength : ''", "wavelength_unit : 1", "multiplicative_factor : ''", "additive_factor : ''"]]])
functionNames.append([['edit_raster_using_shapefile', 'cfg.batchT.performEditRasterUsingShapefile', 'cfg.editRstr.setRasterValue', ["input_raster_path : ''", "input_vector_path : ''", "vector_field_name : ''", "constant_value : 0", "expression :  'where(raster == 1, 2, raster)'"]]])
functionNames.append([['land_cover_change', 'cfg.batchT.performLandCoverChange',  'cfg.landCC.landCoverChange', ["reference_raster_path : ''", "new_raster_path : ''", "output_raster_path : ''"]]])
functionNames.append([['landsat_conversion', 'cfg.batchT.performLandsatConversion',  'cfg.landsatT.landsat', ["input_dir : ''", "mtl_file_path : ''", "celsius_temperature : 0", "apply_dos1 : 0", "use_nodata : 1", "nodata_value : 0", "pansharpening : 0", "create_bandset : 1", "output_dir : ''"]]])
functionNames.append([['open_training_input', 'cfg.batchT.performOpenTrainingInput',  'cfg.classD.openInput', ["training_file_path : ''"]]])
functionNames.append([['pca', 'cfg.batchT.performPCA',  'cfg.pcaT.calculatePCA', ["use_number_of_components : 0"", number_of_components : 2", "use_nodata : 1", "nodata_value : 0", "output_dir : ''"]]])
functionNames.append([['reclassification', 'cfg.batchT.performReclassification', 'cfg.reclassification.reclassify', ["input_raster_path : ''", "value_list : 'oldVal-newVal;oldVal-newVal'", "use_signature_list_code : 1", "code_field : 'MC_ID'", "output_raster_path : ''"]]])
functionNames.append([['sentinel_conversion', 'cfg.batchT.performSentinelConversion', 'cfg.sentinel2T.sentinel2', ["input_dir : ''", "mtd_safl1c_file_path : ''", "apply_dos1 : 0", "use_nodata : 1", "nodata_value : 0", "create_bandset : 1", "output_dir : ''"]]])
functionNames.append([['split_raster_bands', 'cfg.batchT.performSplitRaster', 'cfg.splitT.splitRasterToBands', ["input_raster_path : ''",   "output_dir : ''", "output_name_prefix : 'split'"]]])
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