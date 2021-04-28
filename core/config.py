# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''

''' Init '''
iface = None
cnvs = None
mainAction = None
menu = None
tools_menu = None
preprocessing_menu = None
postprocessing_menu = None
settings_menu = None
toolBar = None
projPath = ''
# main interface
ui = None
dlg = None
currentTab = 'bandSetTab'
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
tmpList = []
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
# signature importer
sigImport = None
QGISVer = None
sysInfo = None
scipyCheck = None
actionCheck = 'No'
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
mskFlPath = ''
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
ROISigTypeNm = 'R&S'
ROITypeNm = 'ROI'
SIGTypeNm = 'Sig'
tblOut = None
reportPth = None
errMtrxPth = None
bndSetMaskList = None
mnlROI = None
regionROI = None
allSignCheck = 'No'
allSignCheck2 = 'No'
allSignCheck3 = 'No'
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
tableColString = 'ID'
ROITabEdited = 'No'
SigTabEdited = 'No'
ScatterTabEdited = 'No'
ReclassTabEdited = 'No'
# classification variables
# threshold
algThrshld = 0
# LC Signature threshold
tableMCID = 'MC ID'
tableCID = 'C ID'
tableMCInfo = 'MC Name'
tableCInfo = 'C Name'
tableColor = 'Color [overlap MC_ID-C_ID]'
tableColor2 = 'Color'
tableMin = 'Min B'
tableMax = 'Max B'
# set vector output variable
vectorOutputCheck = 'No'
reportCheck = 'No'
# raster band pixel count
rasterBandPixelCount = None
# raster pixel count for PCA
rasterPixelCountPCA = {}
# raster clustering
rasterClusteringrasterClustering = {}
# raster class signature
classSignatureNm = 'Class signature'
# remaining time
remainingTime = 0
# set variable for standard deviation plot
sigmaCheck = 'Yes'
# forbandsinbandset
forbandsinbandset = 'forbandsinbandset'
# forbandsets
forbandsets = 'forbandsets'
# forbsdates
forbsdates = 'forbsdates'
# numpy
numpyn = 'cfg.np.'
# numpy logarithm
logn = 'cfg.np.log'
# numpy logarithm
log10 = 'cfg.np.log10'
# numpy logarithm
numpySqrt = 'cfg.np.sqrt'
# numpy cos
numpyCos = 'cfg.np.cos'
# numpy acos
numpyArcCos = 'cfg.np.arccos'
# numpy sin
numpySin = 'cfg.np.sin'
# numpy asin
numpyArcSin = 'cfg.np.arcsin'
# numpy tan
numpyTan = 'cfg.np.tan'
# numpy atan
numpyArcTan = 'cfg.np.arctan'
# numpy exp
numpyExp = 'cfg.np.exp'
# numpy amin
numpyAMin = 'cfg.np.nanmin'
# numpy amax
numpyAMax = 'cfg.np.nanmax'
# numpy nanpercentile
numpyPercentile = 'cfg.np.nanpercentile'
# numpy numpy.nanmedian
numpyMedian = 'cfg.np.nanmedian'
# numpy numpy.nanmean
numpyMean = 'cfg.np.nanmean'
# numpy numpy.nansum
numpySum = 'cfg.np.nansum'
# numpy numpy.nanstd
numpyStd = 'cfg.np.nanstd'
# numpy where
numpyWhere = 'cfg.np.where'
# land cover change variables	
unchngMaskCheck = True
# scatter plot variables
scatterBandX = 1
scatterBandY = 2
# fill plot
pF = []
# virtual raster
landsatVrtNm = 'landsat'
sentinel2VrtNm = 'sentinel2'
tmpVrtNm = 'vrt_temp_'
bndSetVrtNm = 'Virtual Band Set '
tmpVrt = None
tmpVrtDict = {}
# scp input directory
inptDir = None
scpFlPath = None
backupNm = 'backup'
skipProjectSaved = 'No'
# pixel signature names
pixelNm = 'pixel'
pixelCoords = 'Coords'
# temp ROI
tempROINm = 'tempROI'
# temp scatter
tempScatterNm = 'tempScatter'
# empty field name
emptyFN = 'DN'
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
IHS_panType = 'Intensity-Hue-Saturation'
BT_panType = 'Brovey Transform'
# contrast type
cumulativeCutContrast = 'cumulativeCut'
stdDevContrast = 'stdDev'
defaultContrast = cumulativeCutContrast
# settings
testGDALV = None
testMatplotlibV = None
testScipyV = None
testNumpyV = None
# debug
debugRasterPath = '/debug/roi_raster.tif'
absolutePath = False
ctrlClick = None
previewSliderActive = None
previewSliderArray = None
msgWar8check = 'No'
lastSaveDir = ''
skipRegistry = True
# band calc
bandCalcIndex = 0
dockIndex = 0
bandCalcFunctionNames = []
bandCalcFunctionNames.append(['Conditional'])
bandCalcFunctionNames.append(['where', 'where('])
bandCalcFunctionNames.append(['Logical'])
bandCalcFunctionNames.append(['AND', '&'])
bandCalcFunctionNames.append(['OR', '|'])
bandCalcFunctionNames.append(['XOR', '^'])
bandCalcFunctionNames.append(['NOT', '~'])
bandCalcFunctionNames.append(['Statistics'])
bandCalcFunctionNames.append(['max', 'max('])
bandCalcFunctionNames.append(['min', 'min('])
bandCalcFunctionNames.append(['mean', 'mean('])
bandCalcFunctionNames.append(['median', 'median('])
bandCalcFunctionNames.append(['percentile', 'percentile('])
bandCalcFunctionNames.append(['std', 'std('])
bandCalcFunctionNames.append(['sum', 'sum('])
bandCalcFunctionNames.append(['Operations'])
bandCalcFunctionNames.append(['sin', 'sin('])
bandCalcFunctionNames.append(['cos', 'cos('])
bandCalcFunctionNames.append(['tan', 'tan('])
bandCalcFunctionNames.append(['asin', 'asin('])
bandCalcFunctionNames.append(['acos', 'acos('])
bandCalcFunctionNames.append(['atan', 'atan('])
bandCalcFunctionNames.append(['exp', 'exp('])
bandCalcFunctionNames.append(['ln', 'ln('])
bandCalcFunctionNames.append(['log10', 'log10('])
bandCalcFunctionNames.append(['Indices'])
bandCalcFunctionNames.append(['NDVI', '( "#NIR#" - "#RED#" ) / ( "#NIR#" + "#RED#" ) @NDVI'])
bandCalcFunctionNames.append(['EVI', '2.5 * ( "#NIR#" - "#RED#" ) / ( "#NIR#" + 6 * "#RED#" - 7.5 * "#BLUE#" + 1) @EVI'])
bandCalcFunctionNames.append(['NBR', '( "#NIR#" - "#SWIR2#" ) / ( "#NIR#" + "#SWIR2#" ) @NBR'])
bandCalcFunctionNames.append(['Variables'])
bandCalcFunctionNames.append(['nodata', 'nodata('])
bandCalcFunctionNames.append(['forbandsets', 'forbandsets[ ]'])
bandCalcFunctionNames.append(['forbsdates', 'forbsdates[ ]'])
bandCalcFunctionNames.append(['forbandsinbandset', 'forbandsinbandset[ ]'])
bandCalcFunctionNames.append(['#BAND#', '#BAND#'])
bandCalcFunctionNames.append(['!function!', '!function!'])
bandCalcFunctionNames.append(['#BANDSET#', '#BANDSET#'])
bandCalcFunctionNames.append(['#DATE#', '#DATE#'])
bandCalcFunctionNames.append(['@', '@'])
bandCalcFunctionNames.append(['Custom'])
# zonal stat raster
statisticList = []
statisticList.append(['Sum', 'np.nansum(array)'])
statisticList.append(['Max', 'np.nanmax(array)'])
statisticList.append(['Min', 'np.nanmin(array)'])
statisticList.append(['Count', 'np.count_nonzero(~np.isnan(array))'])
statisticList.append(['Mean', 'np.nanmean(array)'])
statisticList.append(['Median', 'np.nanmedian(array)'])
statPerc = '@statPerc@'
statisticList.append(['Percentile', 'np.nanpercentile(array, ' + statPerc + ')'])
statisticList.append(['StandardDeviation', 'np.nanstd(array)'])
# SCP kml name
kmlNm = 'SCP_kml'
# subprocesses dictionary
subprocDictProc={}
parallelArray = 'parallel_array'
parallelRaster = 'parallel_raster'
parallelArrayDict = {}

''' Project variables '''
qmlFl = None
sigClcCheck = '2'
saveInputCheck = '2'
rpdROICheck = '0'
vegIndexCheck = '2'
multiAddFactorsVar = 'multiplicativeAdditiveFactorsVar'
bandSetsList = []
bndSetNumber = 0
bndSetTabList = []
bndSetWidgetReset = 'No'
rasterName = None
cmplClsNm = None
cmplMClsNm = None
treeDockMCItm = {}
treeDockItm = {}
ROIband = 1
maxROIWdth = 100
minROISz = 60
rngRad = 0.01
ROIID = 1
ROIInfo = 'C 1'
ROIMacroClassInfo = 'MC 1'
ROIMacroID = 1
customExpression = ''
macroclassCheckRF = 'Yes'
classRF = ''
# RGB list
RGBListDef = str(['-', '3-2-1', '4-3-2'])
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

''' QGIS variables '''
# registry key for first installation
regFirstInstall = 'SemiAutomaticClassificationPlugin/firstInstall'
firstInstallVal = 'Yes'
# registry key for log setting
regLogKey = 'SemiAutomaticClassificationPlugin/logSetting'
logSetVal = 'No'
# registry key for sound
regSound = 'SemiAutomaticClassificationPlugin/useSoundStart'
soundVal = '2'
# registry key for ROI color setting
regROIClr = 'SemiAutomaticClassificationPlugin/ROIColour'
ROIClrValDefault = '#ffaa00'
ROIClrOutlineValDefault = '#53d4e7'
ROIClrVal = ROIClrValDefault
# registry key for ROI transparency setting
regROITransp = 'SemiAutomaticClassificationPlugin/ROITransparency4'
# registry key for download news
downNewsKey = 'SemiAutomaticClassificationPlugin/downloadNewsStart7'
downNewsVal = '2'
# registry key for download news
vrtRstProjKey = 'SemiAutomaticClassificationPlugin/loadVirtualRasterStart'
vrtRstProjVal = '0'
# registry key for algorithm files
regAlgFiles = 'SemiAutomaticClassificationPlugin/algFilesStart'
algFilesCheck = '0'
ROITrnspValDefault = 45
ROITrnspVal = ROITrnspValDefault
# registry key for temporary raster format
regTempRasterFormat = 'SemiAutomaticClassificationPlugin/tempRastFormat'
# registry key for raster compression
regRasterCompression = 'SemiAutomaticClassificationPlugin/rasterCompression'
# registry key for parallel writing
regparallelWritingCheck = 'SemiAutomaticClassificationPlugin/parallelWritingCheck'
# registry key for RAM value setting
regRAMValue = 'SemiAutomaticClassificationPlugin/RAMValue'
RAMValue = 512
# registry key for CPU threads value setting
regThreadsValue = 'SemiAutomaticClassificationPlugin/threadsValue'
threads = 1
# gdal path setting
regGDALPathSettings = 'SemiAutomaticClassificationPlugin/GDALPathSettings'
gdalPath = ''
# python path setting
regPythonPathSettings = 'SemiAutomaticClassificationPlugin/PythonPathSettings'
PythonPathSettings = ''
# smtp server
regSMTPCheck = 'SemiAutomaticClassificationPlugin/SMTPCheckStart'
SMTPCheck = '2'
regSMTPServer = 'SemiAutomaticClassificationPlugin/SMTPServer'
SMTPServer = ''
regSMTPtoEmails = 'SemiAutomaticClassificationPlugin/SMTPtoEmails'
SMTPtoEmails = ''
regSMTPUser = 'SemiAutomaticClassificationPlugin/SMTPUser'
SMTPUser = ''
regSMTPPassword = 'SemiAutomaticClassificationPlugin/SMTPPassword'
SMTPPassword = ''
# field names for shapefile
regIDFieldName = 'SemiAutomaticClassificationPlugin/IDFieldName'
# registry key for temporary directory
regTmpDir = 'SemiAutomaticClassificationPlugin/TmpDir'
regUSGSUser = 'SemiAutomaticClassificationPlugin/USGSUser'
USGSUser = ''
regUSGSPass= 'SemiAutomaticClassificationPlugin/USGSPass'
USGSPass = ''
regUSGSUserASTER = 'SemiAutomaticClassificationPlugin/USGSUserASTER'
USGSUserASTER = ''
regUSGSPassASTER = 'SemiAutomaticClassificationPlugin/USGSPassASTER'
USGSPassASTER = ''
regSentinelAlternativeSearch = 'SemiAutomaticClassificationPlugin/SentinelAlternativeSearch'
sentinelAlternativeSearch = '0'
regSciHubUser = 'SemiAutomaticClassificationPlugin/SciHubUser'
SciHubUser = ''
regSciHubPass = 'SemiAutomaticClassificationPlugin/SciHubPass'
SciHubPass = ''
regSciHubService = 'SemiAutomaticClassificationPlugin/SciHubService_5_2'
SciHubServiceNm = 'https://scihub.copernicus.eu/apihub'
SciHubService = SciHubServiceNm
fldMacroID_class_def = 'MC_ID'
fldID_class_def = 'C_ID'
fldROI_info_def = 'C_name'
fldROIMC_info_def = 'MC_name'
ROI_Size_info_def = 'ROI_size'
fldSCP_UID_def= 'SCP_UID'
variableName_def = 'raster'
variableOutName_def = 'output'
vectorVariableName_def = 'vector'
variableBandsetName_def = 'bandset'
variableBlueName_def = '#BLUE#'
variableGreenName_def = '#GREEN#'
variableRedName_def = '#RED#'
variableNIRName_def = '#NIR#'
variableSWIR1Name_def = '#SWIR1#'
variableSWIR2Name_def = '#SWIR2#'
variableOutputNameBandset_def = '#BANDSET#'
variableOutputNameDate_def = '#DATE#'
variableBand_def = '#BAND#'
merged_name = 'merged_'
fldID_class = fldID_class_def
# macroclass ID
regMacroIDFieldName = 'SemiAutomaticClassificationPlugin/MCIDFieldName'
fldMacroID_class = fldMacroID_class_def
# macroclass check
regConsiderMacroclass = 'SemiAutomaticClassificationPlugin/ConsiderMacroclass'
macroclassCheck = 'No'
# LCS
regLCSignature = 'SemiAutomaticClassificationPlugin/LCSignature'
LCsignatureCheckBox = 'No'
# info field
regInfoFieldName = 'SemiAutomaticClassificationPlugin/InfoFieldName'
regMCInfoFieldName = 'SemiAutomaticClassificationPlugin/MCInfoFieldName'
fldROI_info = fldROI_info_def
fldROIMC_info = fldROIMC_info_def
ROI_Size_info = ROI_Size_info_def
fldSCP_UID = fldSCP_UID_def
# variable name
regVariableName = 'SemiAutomaticClassificationPlugin/VariableName'
variableName = variableName_def
variableOutName = variableOutName_def
# variable name
regVectorVariableName = 'SemiAutomaticClassificationPlugin/vectorVariableName'
vectorVariableName = vectorVariableName_def
# variable band set name
regVariableBandsetName = 'SemiAutomaticClassificationPlugin/VariableBandsetName'
variableBandsetName = variableBandsetName_def
variableBlueName = variableBlueName_def
variableGreenName = variableGreenName_def
variableRedName = variableRedName_def
variableNIRName = variableNIRName_def
variableSWIR1Name = variableSWIR1Name_def
variableSWIR2Name = variableSWIR2Name_def
variableOutputNameBandset = variableOutputNameBandset_def
variableOutputNameDate = variableOutputNameDate_def
variableBand = variableBand_def
# band set name
regBandSetName = 'SemiAutomaticClassificationPlugin/BandSetName'
bandSetName = 'Band set '
# plot variables
#regRoundCharList = 'SemiAutomaticClassificationPlugin/roundCharList'
roundCharList = 15
# group name for temp ROI and Preview
regGroupName = 'SemiAutomaticClassificationPlugin/groupName'
grpNm_def = 'Class_temp_group'
grpNm = grpNm_def
lastPrev = None
lastScattRaster = None
prevList = []
# clip prefix
clipNm = 'clip'
# reproject prefix
reprojNm = 'reproj'
# output temp raster format
outTempRastFormat = 'VRT'
rasterCompression = 'Yes'
parallelWritingCheck = 'No'
# raster data type
regRasterDataType = 'SemiAutomaticClassificationPlugin/rasterDataTypeNew'
rasterDataType = 'Float32'
rasterBandCalcType = 'Float32'
# raster data type
regExpressionListBC= 'SemiAutomaticClassificationPlugin/expressionListBC'
expressionListBCbase = []
expressionListBC = expressionListBCbase
LCSOld = 'Yes'
# window size
regWindowSizeW = 'SemiAutomaticClassificationPlugin/windowSizeW'
windowSizeW = '700'
regWindowSizeH = 'SemiAutomaticClassificationPlugin/windowSizeH'
windowSizeH = '500'
regSplitterSizeS = 'SemiAutomaticClassificationPlugin/splitterSizeS'
splitterSizeS = '[100, 100]'

''' Names '''
algMinDist = 'Minimum Distance'
algML = 'Maximum Likelihood' 
algSAM = 'Spectral Angle Mapping'
uncls = 'Unclassified'
clasfd = 'Classified'
overlap = 'Class Overlap'
algRasterNm = 'alg_raster'
classRasterNm = 'class_raster'
calcRasterNm = 'calc_raster'
calcFunctionNm = '!function!'
calcVarReplace = 'variable<scp>replace<scp>expression'
scatterRasterNm = 'scatter_raster'
polyRasterNm = 'polyr_raster'
stackRasterNm = 'stack_raster'
virtualRasterNm = 'virt_rast'
errMatrixNm = '_error_matrix.csv'
crossClassNm = '_cross_classification.csv'
PCANm = 'PCA_band_'
PCAReportNm = 'PCA_report.txt'
kmeansNm = 'kmeans_'
kmeansReportNm = 'kmeans_report.txt'
tempMtrxNm = 'tmp_error_matrix'
reportNm = '_report.csv'
sigRasterNm = 'sig'
prvwTempNm = 'previewtemp.tif'
rclssTempNm = 'temporary_ref_reclass'
bsCombTempNm = 'temporary_band_set_comb'
maskRasterNm = 'mskRstr.tif'
subsROINm = 'subset_ROI_temp.tif'
subsTmpRaster = 'subset_temp_b'
subsTmpROI = 'ROI_tmp_copy'
copyTmpROI = 'ROI_rast_temp'
tmpRegionNm = 'region_temp'
tmpROINm = 'temp_ROI'
mapExtent = '\'Map extent\''
pixelExtent = '\'Pixel extent\''
splitBndNm = 'splitBand_'
spectralDistNm = 'SpectralDistanceBandSets_'
reflectanceRasterNm = 'reflectance_temp'
NoDataVal = -32768
unclassifiedVal = -1000
maxLikeNoDataVal = -999999999900000
maxValDt = 999999999900000
unclassValue = None
referenceLayer = None
prvwSz = 200
# alg name
algName = 'Minimum Distance'
kmeansAlgName = 'Minimum Distance'
algLCS = 'Land Cover Signature'
algKmeans = 'K-means'
algISODATA = 'ISODATA'
# type of conversion
convCenterPixels = 'Center of pixels'
convAllPixelsTouch ='All pixels touched'
#index name
indName = 'NDVI'
indNDVI = 'NDVI'
indEVI = 'EVI'
indCustom = 'Custom'
# set mask variable
maskCheck = 'No'
# prefix for ROI signature fields
ROIFieldMean = 'ROIm_b'
ROISigma = 'ROIs_b'
ROINBands = 'ROI_NBands'
# spectral plot
wavelenNm = 'Wavelength'
valNm = 'Values'
standDevNm = 'Standard deviation'
# distances
euclideanDistNm = 'Euclidean distance'
brayCurtisSimNm = 'Bray-Curtis similarity [%]'
spectralAngleNm = 'Spectral angle'
jeffriesMatusitaDistNm = 'Jeffries-Matusita distance'
transformedDivergenceNm = 'Transformed divergence'
notAvailable = 'n/a'
resampling_methods = ['nearest_neighbour', 'average', 'sum', 'maximum', 'minimum', 'mode', 'median', 'first_quartile', 'third_quartile']

''' band set '''
# list of satellites for wavelength
NoSatellite = 'Band order'
satGeoEye1 = 'GeoEye-1 [bands 1, 2, 3, 4]'
satGOES = 'GOES [bands 1, 2, 3, 4, 5, 6]'
satLandsat8 = 'Landsat 8 OLI [bands 2, 3, 4, 5, 6, 7]'
satLandsat7 = 'Landsat 7 ETM+ [bands 1, 2, 3, 4, 5, 7]'
satLandsat45 = 'Landsat 4-5 TM [bands 1, 2, 3, 4, 5, 7]'
satLandsat13 = 'Landsat 1-3 MSS [bands 4, 5, 6, 7]'
satRapidEye = 'RapidEye [bands 1, 2, 3, 4, 5]'
satSentinel1 = 'Sentinel-1 [bands VV, VH]'
satSentinel2 = 'Sentinel-2 [bands 1, 2, 3, 4, 5, 6, 7, 8, 8A, 9, 10, 11, 12]'
satSentinel3 = 'Sentinel-3 [bands 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]'
satASTER = 'ASTER [bands 1, 2, 3N, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]'
satMODIS = 'MODIS [bands 3, 4, 1, 2, 5, 6, 7]'
satMODIS2 = 'MODIS [bands 1, 2]'
satSPOT4 = 'SPOT 4 [bands 1, 2, 3, 4]'
satSPOT5 = 'SPOT 5 [bands 1, 2, 3, 4]'
satSPOT6 = 'SPOT 6 [bands 1, 2, 3, 4]'
satPleiades = 'Pleiades [bands 1, 2, 3, 4]'
satQuickBird = 'QuickBird [bands 1, 2, 3, 4]'
satWorldView23 = 'WorldView-2 -3 Multispectral [bands 1, 2, 3, 4, 5, 6, 7, 8]'
satWlList = ['', NoSatellite, satASTER, satGeoEye1, satGOES, satLandsat8, satLandsat7, satLandsat45, satLandsat13, satMODIS, satMODIS2, satPleiades, satQuickBird, satRapidEye, satSentinel2, satSentinel3, satSPOT4, satSPOT5, satSPOT6, satWorldView23]
usgsLandsat8 = 'L8 OLI/TIRS'
usgsLandsat7 = 'L7 ETM+'
usgsLandsat45 = 'L4-5 TM'
usgsLandsat15 = 'L1-5 MSS'
esaSentinel2 = 'Sentinel-2'
esaSentinel3 = 'Sentinel-3'
esaSentinel1 = 'Sentinel-1'
usgsASTER = 'ASTER Level 1T'
goes16 = 'GOES 16'
goes17 = 'GOES 17'
usgsMODIS_MOD09GQ = 'MOD09GQ_V6'
usgsMODIS_MYD09GQ = 'MYD09GQ_V6'
usgsMODIS_MOD09GA = 'MOD09GA_V6'
usgsMODIS_MYD09GA = 'MYD09GA_V6'
usgsMODIS_MOD09Q1 = 'MOD09Q1_V6'
usgsMODIS_MYD09Q1 = 'MYD09Q1_V6'
usgsMODIS_MOD09A1 = 'MOD09A1_V6'
usgsMODIS_MYD09A1 = 'MYD09A1_V6'
usgsLandsat8Collection = '12864'
usgsLandsat7Collection = '12267'
usgsLandsat45Collection = '12266'
usgsLandsat15Collection = '3120'
usgsASTERCollection = '9380'
NASAMOD09GQCollection = 'C193529903-LPDAAC_ECS'
NASAMYD09GQCollection = 'C193529460-LPDAAC_ECS'
NASAMOD09GACollection = 'C193529902-LPDAAC_ECS'
NASAMYD09GACollection = 'C193529459-LPDAAC_ECS'
NASAMOD09Q1Collection = 'C193529944-LPDAAC_ECS'
NASAMYD09Q1Collection = 'C193529461-LPDAAC_ECS'
NASAMOD09A1Collection = 'C193529899-LPDAAC_ECS'
NASAMYD09A1Collection = 'C193529457-LPDAAC_ECS'
NASAASTERCollection = 'C1000000320-LPDAAC_ECS'
NASALandsat8Collection = 'C1427461962-USGS_EROS'
NASALandsat7Collection = 'C1427459680-USGS_EROS'
NASALandsat45Collection = 'C1427462674-USGS_EROS'
NASALandsat15Collection = 'C1519978054-USGS_EROS'
satSentinelList = [esaSentinel2]
satSentinel3List = [esaSentinel3]
satSentinel1List = [esaSentinel1]
satLandsatList = [usgsLandsat8, usgsLandsat7, usgsLandsat45, usgsLandsat15]
satASTERtList = [usgsASTER]
satGOEStList = [goes16, goes17]
satMODIStList = [usgsMODIS_MOD09GQ, usgsMODIS_MYD09GQ, usgsMODIS_MOD09GA, usgsMODIS_MYD09GA, usgsMODIS_MOD09Q1, usgsMODIS_MYD09Q1, usgsMODIS_MOD09A1, usgsMODIS_MYD09A1]
downProductList = satSentinelList + satSentinel3List + satSentinel1List + satLandsatList + satASTERtList + satMODIStList + satGOEStList
indNDVI = 'NDVI'
indEVI = 'EVI'
indicesList = ['', indNDVI, indEVI]
# unit list
noUnit = 'band number'
wlMicro = 'µm (1 E-6m)'
wlNano = 'nm (1 E-9m)'
unitNano = 'E-9m'
unitMicro = 'E-6m'
unitList = [noUnit, wlMicro, wlNano]
BandTabEdited = 'Yes'
rasterComboEdited = 'Yes'
tempDirName = 'semiautomaticclassification'
# USGS spectral library
usgs_C1 = 'Chapter 1: Minerals'
usgs_C2 = 'Chapter 2: Soils and Mixtures'
usgs_C3 = 'Chapter 3: Coatings'
usgs_C4 = 'Chapter 4: Liquids'
usgs_C5 = 'Chapter 5: Organics'
usgs_C6 = 'Chapter 6: Artificial'
usgs_C7 = 'Chapter 7: Vegetation and Mixtures'
usgs_lib_list = ['', usgs_C1,usgs_C2,usgs_C3,usgs_C4,usgs_C5,usgs_C6,usgs_C7]
usgs_C1p = '/spectralsignature/usgs_spectral_library/minerals.csv'
usgs_C2p = '/spectralsignature/usgs_spectral_library/soils.csv'
usgs_C3p = '/spectralsignature/usgs_spectral_library/coatings.csv'
usgs_C4p = '/spectralsignature/usgs_spectral_library/liquids.csv'
usgs_C5p = '/spectralsignature/usgs_spectral_library/organics.csv'
usgs_C6p = '/spectralsignature/usgs_spectral_library/artificial.csv'
usgs_C7p = '/spectralsignature/usgs_spectral_library/vegetation.csv'

''' Batch '''
workingDirNm = '!working_dir!'
tempRasterNm = '!temp_raster_'
startForDirNm = '!for_directory_in!'
DirNm = '!directory!'
directoryName = '!directory_name!'
endForDirNm = '!end_for_directory!'
startForFileNm = '!for_file_in!'
FileNm = '!file!'
FileDirNm = '!file_directory!'
endForFileNm = '!end_for_file!'
startForBandSetNm = '!for_band_set!'
bandSetNm = '!bandset_number!'
endForBandSetNm = '!end_for_band_set!'
workingDir = None
functionNames = []
functionNames.append([['Band set']])
functionNames.append([[' add_new_bandset', 'cfg.batchT.performAddNewBandSet',  'cfg.bst.addBandSetTab', ['band_set : 1']]])
functionNames.append([[' add_raster', 'cfg.batchT.performAddRaster',  'cfg.utls.addRasterOrBand', ['input_raster_path : \'\'', 'input_raster_name : \'\'', 'band_set : 1', 'center_wavelength : 1']]])
functionNames.append([[' create_bandset', 'cfg.batchT.performBandSetCreation',  'cfg.bst.addFileToBandSet', ['raster_path_list : \'\'', 'center_wavelength : \'\'', 'wavelength_unit : 1', 'multiplicative_factor : \'\'', 'additive_factor : \'\'', 'date : \'\'']]])
functionNames.append([[' open_training_input', 'cfg.batchT.performOpenTrainingInput',  'cfg.SCPD.openInput', ['training_file_path : \'\'']]])
functionNames.append([[' remove_band_from_bandset', 'cfg.batchT.performRemoveBandFromBandSet',  'cfg.bst.removeBandsFromBandSet', ['band_set : 1', 'band_list : \'\'']]])
functionNames.append([[' remove_bandset', 'cfg.batchT.performRemoveBandSet',  'cfg.bst.removeBandSetTab', ['band_set : 1']]])
functionNames.append([[' select_bandset', 'cfg.batchT.performBandSetSelection',  'cfg.bst.selectBandSetTab', ['band_set : 1']]])
functionNames.append([['Band calculation']])
functionNames.append([[' band_calc', 'cfg.batchT.performBandCalc',  'cfg.bCalc.calculate', ['expression : \'\'', 'output_raster_path : \'\'', 'extent_same_as_raster_name : \'\'', 'align : 1', 'extent_intersection : 1', 'input_nodata_as_value : 0', 'use_value_nodata : 0', 'output_nodata_value : -32768', 'data_type : \'Float32\'', 'scale_value : 1',  'offset_value : 0', 'band_set : 1']]])
functionNames.append([['Preprocessing']])
functionNames.append([[' aster_conversion', 'cfg.batchT.performASTERConversion', 'cfg.ASTERT.ASTER', ['input_raster_path : \'\'', 'celsius_temperature : 0', 'apply_dos1 : 0', 'use_nodata : 1', 'nodata_value : 0', 'create_bandset : 1', 'output_dir : \'\'', 'band_set : 1']]])
functionNames.append([[' clip_multiple_rasters', 'cfg.batchT.performClipRasters',  'cfg.clipMulti.clipRasters', ['band_set : 1', 'output_dir : \'\'', 'use_vector : 0', 'vector_path : \'\'', 'use_vector_field : 0', 'vector_field : \'\'', 'ul_x : \'\'', 'ul_y : \'\'', 'lr_x : \'\'', 'lr_y : \'\'', 'nodata_value : 0', 'output_name_prefix : \'clip\'']]])
functionNames.append([[' cloud_masking', 'cfg.batchT.performCloudMasking',  'cfg.cloudMsk.cloudMaskingBandSet', ['band_set : 1', 'input_raster_path : \'\'', 'class_values : \'\'', 'use_buffer : 1', 'size_in_pixels : 1', 'nodata_value : 0', 'output_name_prefix : \'mask\'', 'output_dir : \'\'']]])
functionNames.append([[' goes_conversion', 'cfg.batchT.performGOESConversion', 'cfg.goesT.GOES', ['input_dir : \'\'', 'use_nodata : 1', 'nodata_value : 0', 'create_bandset : 1', 'output_dir : \'\'', 'band_set : 1']]])
functionNames.append([[' landsat_conversion', 'cfg.batchT.performLandsatConversion',  'cfg.landsatT.landsat', ['input_dir : \'\'', 'mtl_file_path : \'\'', 'celsius_temperature : 0', 'apply_dos1 : 0', 'use_nodata : 1', 'nodata_value : 0', 'pansharpening : 0', 'create_bandset : 1', 'output_dir : \'\'', 'band_set : 1']]])
functionNames.append([[' modis_conversion', 'cfg.batchT.performMODISConversion', 'cfg.MODIST.MODIS', ['input_raster_path : \'\'', 'reproject_wgs84 : 1', 'use_nodata : 1', 'nodata_value : -999', 'create_bandset : 1', 'output_dir : \'\'', 'band_set : 1']]])
functionNames.append([[' mosaic_bandsets', 'cfg.batchT.performMosaicBandSets', 'cfg.mosaicBS.mosaicBandSets', ['band_set_list : \'\'', 'virtual_output : 0', 'output_dir : \'\'', 'output_name_prefix : \'mosaic\'']]])
functionNames.append([[' neighbor_pixels', 'cfg.batchT.performNeighborPixels', 'cfg.clssNghbr.classNeighbor', ['band_set : 1', 'matrix_size : 1', 'matrix_file_path : \'\'', 'output_name_prefix : \'neighbor\'', 'statistic : \'sum\'', 'stat_value : 50', 'output_dir : \'\'']]])
functionNames.append([[' reproject_raster_bands', 'cfg.batchT.performReprojectRasters',  'cfg.rprjRstBndsT.reprojectRasters', ['band_set : 1', 'output_dir : \'\'', 'align_raster_path : \'\'', 'same_extent_reference : 0', 'epsg : \'\'','x_resolution : \'\'', 'y_resolution : \'\'', 'resample_pixel_factor : \'\'',  'resampling_method : \'near\'', 'output_nodata_value : -32768', 'data_type : \'auto\'',  'output_name_prefix : \'reproj\'']]])
functionNames.append([[' sentinel1_conversion', 'cfg.batchT.performSentinel1Conversion', 'cfg.sentinel1T.sentinel1', ['input_raster_path : \'\'', 'xml_file_path : \'\'', 'vh : 1', 'vv : 1',  'raster_project : 0',  'raster_projections_band_set : 1', 'convert_to_db : 1', 'use_nodata : 1', 'nodata_value : 0', 'create_bandset : 1', 'output_dir : \'\'', 'band_set : 1']]])
functionNames.append([[' sentinel2_conversion', 'cfg.batchT.performSentinel2Conversion', 'cfg.sentinel2T.sentinel2', ['input_dir : \'\'', 'mtd_safl1c_file_path : \'\'', 'apply_dos1 : 0', 'preprocess_bands_1_9_10 : 0', 'use_nodata : 1', 'nodata_value : 0', 'create_bandset : 1', 'output_dir : \'\'', 'band_set : 1']]])
functionNames.append([[' sentinel3_conversion', 'cfg.batchT.performSentinel3Conversion', 'cfg.sentinel3T.sentinel3', ['input_dir : \'\'', 'apply_dos1 : 0', 'use_nodata : 1', 'nodata_value : 0', 'create_bandset : 1', 'output_dir : \'\'', 'band_set : 1']]])
functionNames.append([[' vector_to_raster', 'cfg.batchT.performVectorToRaster', 'cfg.vctRstrT.convertToRaster', ['vector_file_path : \'\'', 'use_value_field : 1', 'vector_field_name : \'\'', 'constant_value : 1', 'reference_raster_path : \'\'', 'extent_same_as_reference : 0', 'type_of_conversion : \'Center of pixels\'', 'output_raster_path : \'\'']]])
functionNames.append([[' split_raster_bands', 'cfg.batchT.performSplitRaster', 'cfg.splitT.splitRasterToBands', ['input_raster_path : \'\'', 'output_dir : \'\'', 'output_name_prefix : \'split\'']]])
functionNames.append([[' stack_raster_bands', 'cfg.batchT.performStackRaster', 'cfg.stackRstr.stackRasters', ['band_set : 1', 'output_raster_path : \'\'']]])
functionNames.append([['Band processing']])
functionNames.append([[' band_combination', 'cfg.batchT.performBandCombination',  'cfg.bsComb.bandSetCombination', ['band_set : 1', 'output_raster_path : \'\'']]])
functionNames.append([[' classification', 'cfg.batchT.performClassification', 'cfg.classTab.runClassification', ['band_set : 1', 'use_macroclass : 0', 'algorithm_name  : \'Minimum Distance\'', 'use_lcs : 0', 'use_lcs_algorithm : 0', 'use_lcs_only_overlap : 0', 'apply_mask : 0',  'mask_file_path : \'\'', 'vector_output : 0',  'classification_report : 0',  'save_algorithm_files : 0', 'output_classification_path : \'\'']]])
functionNames.append([[' clustering', 'cfg.batchT.performClustering',  'cfg.clusteringT.calculateClustering', ['band_set : 1','clustering_method : 1', 'use_distance_threshold : 1', 'threshold_value : 0.0001', 'number_of_classes : 10', 'max_iterations : 10', 'isodata_max_std_dev : 0.0001', 'isodata_min_class_size : 10', 'use_nodata : 0', 'nodata_value : 0', 'seed_signatures : 1', 'distance_algorithm : 1', 'save_signatures : 0', 'output_raster_path : \'\'']]])
functionNames.append([[' pca', 'cfg.batchT.performPCA',  'cfg.pcaT.calculatePCA', ['band_set : 1', 'use_number_of_components : 0', 'number_of_components : 2', 'use_nodata : 1', 'nodata_value : 0', 'output_dir : \'\'']]])
functionNames.append([[' random_forest', 'cfg.batchT.performRandomForest', 'cfg.rndmFrst.randomForestClassification', ['band_set : 1', 'use_macroclass : 1', 'number_training_samples : 5000', 'number_trees : 10', 'evaluate_classifier : 0', 'evaluate_feature_power_set : 0', 'min_power : 2', 'max_power : 7', 'save_classifier : 0', 'classifier_file_path : \'\'', 'output_classification_path : \'\'']]])
functionNames.append([[' spectral_distance', 'cfg.batchT.performSpectralDistance', 'cfg.spclDstBS.spectralDistBandSets', ['first_band_set : 1', 'second_band_set : 2', 'distance_algorithm  : 1', 'use_distance_threshold : 1', 'threshold_value : 0.1', 'output_raster_path : \'\'']]])
functionNames.append([['Postprocessing']])
functionNames.append([[' accuracy', 'cfg.batchT.performAccuracy',  'cfg.acc.errorMatrix', ['classification_file_path : \'\'', 'reference_file_path : \'\'', 'vector_field_name : \'\'', 'output_raster_path : \'\'', 'use_value_nodata : 0']]])
functionNames.append([[' class_signature', 'cfg.batchT.performClassSignature',  'cfg.classSigT.calculateClassSignature', ['input_raster_path : \'\'', 'band_set : 1', 'save_signatures : 1', 'output_text_path : \'\'']]])
functionNames.append([[' classification_dilation', 'cfg.batchT.performClassificationDilation', 'cfg.dltnRstr.dilationClassification', ['input_raster_path : \'\'', 'class_values : \'\'', 'size_in_pixels : 1', 'pixel_connection : 4', 'output_raster_path : \'\'']]])
functionNames.append([[' classification_erosion', 'cfg.batchT.performClassificationErosion', 'cfg.ersnRstr.erosionClassification', ['input_raster_path : \'\'', 'class_values : \'\'', 'size_in_pixels : 1', 'pixel_connection : 4', 'output_raster_path : \'\'']]])
functionNames.append([[' classification_report', 'cfg.batchT.performClassificationReport',  'cfg.classRep.calculateClassificationReport', ['input_raster_path : \'\'', 'use_nodata : 0', 'nodata_value : 0', 'output_report_path : \'\'']]])
functionNames.append([[' classification_sieve', 'cfg.batchT.performClassificationSieve',  'cfg.sieveRstr.sieveClassification', ['input_raster_path : \'\'', 'size_threshold : 2', 'pixel_connection : 4', 'output_raster_path : \'\'']]])
functionNames.append([[' classification_to_vector', 'cfg.batchT.performClassificationToVector', 'cfg.classVect.convertClassificationToVector', ['input_raster_path : \'\'', 'use_signature_list_code : 0', 'code_field : \'C_ID\'', 'dissolve_output : 0', 'output_vector_path : \'\'']]]) 
functionNames.append([[' cross_classification', 'cfg.batchT.performCrossClassification',  'cfg.crossC.crossClassification', ['classification_file_path : \'\'', 'use_nodata : 0', 'nodata_value : 0', 'reference_file_path : \'\'', 'vector_field_name : \'\'', 'output_raster_path : \'\'']]])
functionNames.append([[' edit_raster_using_vector', 'cfg.batchT.performEditRasterUsingVector', 'cfg.editRstr.setRasterValue', ['input_raster_path : \'\'', 'input_vector_path : \'\'', 'vector_field_name : \'\'', 'constant_value : 0', 'expression :  \'where(raster == 1, 2, raster)\'']]])
functionNames.append([[' land_cover_change', 'cfg.batchT.performLandCoverChange',  'cfg.landCC.landCoverChange', ['reference_raster_path : \'\'', 'new_raster_path : \'\'', 'output_raster_path : \'\'']]])
functionNames.append([[' reclassification', 'cfg.batchT.performReclassification', 'cfg.reclassification.reclassify', ['input_raster_path : \'\'', 'value_list : \'oldVal_newVal,oldVal_newVal\'', 'use_signature_list_code : 1', 'code_field : \'MC_ID\'', 'output_raster_path : \'\'']]])
functionNames.append([[' zonal_stat_raster', 'cfg.batchT.performZonalStatRaster',  'cfg.znlSttRstT.zonalStatRaster', ['input_raster_path : \'\'', 'reference_file_path : \'\'', 'use_nodata : 0', 'nodata_value : 0', 'vector_field_name : \'\'', 'statistic : \'sum\'', 'stat_value : 50', 'output_raster_path : \'\'']]])
functionNames.append([['Variables']])
functionNames.append([[workingDirNm, 'cfg.batchT.workingDirectory', '', ['\'\'']]])
functionNames.append([[startForDirNm, '', '', ['\'\'']]])
functionNames.append([[DirNm, '', '', []]])
functionNames.append([[directoryName, '', '', []]])
functionNames.append([[endForDirNm, '', '', []]])
functionNames.append([[startForFileNm, '', '', ['\'\'']]])
functionNames.append([[FileNm, '', '', []]])
functionNames.append([[FileDirNm, '', '', []]])
functionNames.append([[endForFileNm, '', '', []]])
functionNames.append([[startForBandSetNm, '', '', ['\'\'']]])
functionNames.append([[bandSetNm, '', '', []]])
functionNames.append([[endForBandSetNm, '', '', []]])
functionNames.append([['!temp_raster_1!', '', '', []]])

''' Scatter plot '''
scatterColorMap = ['rainbow', 'gist_rainbow', 'jet', 'afmhot', 'bwr', 'gnuplot', 'gnuplot2', 'BrBG', 'coolwarm', 'PiYG', 'PRGn', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'seismic', 'ocean', 'terrain', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']

''' Input toolbar '''
toolButton_reload = None
main_toolButton = None
bandset_toolButton = None
ROItools_toolButton = None
preprocessing_toolButton = None
postprocessing_toolButton = None
settings_toolButton = None
settings_toolButton = None