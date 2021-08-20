---
title: 'Semi-Automatic Classification Plugin: A Python tool for the download and processing of remote sensing images in QGIS'
tags:
  - Python
  - Remote sensing
  - Supervised classification
  - Image processing
  - Land cover
authors:
  - name: Luca Congedo
    orcid: 0000-0001-7283-116X
    affiliation: "1"
affiliations:
 - name: Independent Researcher
   index: 1
date: 8 March 2021
bibliography: paper.bib


---

# Summary

The `Semi-Automatic Classification Plugin` is a Python plugin for the software QGIS [@QGIS] developed with the overall objective to facilitate land cover monitoring by people whose main field is not strictly remote sensing, but that could benefit from remote sensing analysis.
The `Semi-Automatic Classification Plugin` provides a set of intertwined tools and a user interface for easing and automating the phases of land cover classification, from the download of remote sensing images, to the preprocessing (i.e. tools for preparing the data to the analysis or other calculations), the processing (i.e. tools for performing the classification of land cover or perform analysis), and postprocessing (i.e. tools for assessing the classification accuracy, refining the classification, or integrating additional data).
The processing of remote sensing data can be computationally intensive, therefore most of the developed tools use [Python multiprocessing](https://docs.python.org/3/library/multiprocessing.html) to exploit the system CPU and RAM by splitting the work among multiple subprocesses.
The aim of this paper is to describe the main characteristics of the `Semi-Automatic Classification Plugin` for the land cover classification of remote sensing images.

# Statement of need

Remote sensing is the measurement, by a sensor installed on board of airplanes or satellites, of the energy that is emanated from the Earth’s surface [@Richards:2006].
Remote sensing images are spatial data and require the use of a Geographic Information System (GIS) for visualization and processing. 
The free availability of satellite data (such as Landsat [@USGS:2019], and Sentinel-2 [@ESA:2018]) extended the use of remote sensing in various fields such as urban planning, agriculture, environmental monitoring, etc. [@Rogan:2004; @Pesaresi:2016; @Weiss:2020; @Nink:2019].
Land cover is defined as the material at the Earth’s surface, such as soil, vegetation, water, asphalt, etc. [@Fisher:2005].
A supervised classification (also known as semi-automatic classification) is an image processing technique that aims at classifying land cover by training an algorithm with samples of material spectral signatures.

The development of open source GIS and processing software can foster environmental monitoring, which can be performed with no cost for software and remote sensing images considering the free data availability.
QGIS is an open source GIS software which provides several tools for data visualization and analysis; it is mainly written in C++ code, but it also allows to extend the functions thereof through API and plugins written in Python [@QGIS].
QGIS has a large repository of plugins that improve data analysis and also provide access to several image processing tools included in other open source programs such as GRASS [@GRASS], GDAL [@GDAL], and Orfeo Toolbox [@OTB].
These programs allow for the processing of satellite images, nevertheless their use can be difficult for people interested in land cover classifications but specialized in fields other than remote sensing, because of the several steps required for image processing. 

The `Semi-Automatic Classification Plugin` aims to provide a complete suite of tools for processing remote sensing data, easing the phases related to the download, the preprocessing of images, and the postprocessing of classifications, with built-in algorithms developed in Python and third party algorithms for specific functions (e.g. Sentinel-1 preprocessing through ESA SNAP [@SNAP]).

Several tutorials about the `Semi-Automatic Classification Plugin` are freely available on the [official website](https://fromgistors.blogspot.com/search/label/Tutorial), and the [user manual](https://semiautomaticclassificationmanual.readthedocs.io) is being translated into several languages by the user community.

The `Semi-Automatic Classification Plugin` has been cited in several studies about land cover, urban growth, and image processing [@Leroux:2018; @Zhang:2018; @Arekhi:2019; @Huq:2019; @Pelage:2019; @Teodoro:2019; @Furukawa:2020; @Damtew:2021; @Garilli:2021; @Palafox-Juarez:2021].

# Overview of the Semi-Automatic Classification Plugin

The `Semi-Automatic Classification Plugin` interfaces is composed of several modules (as illustrated in \autoref{fig:plugin_interface}).
A module allows for searching and downloading freely available images (in particular ASTER, GOES, Landsat, MODIS, Sentinel-1, Sentinel-2, and Sentinel-3).
It is possible to perform the preprocessing and raster calculations automatically after the download, by setting a few parameters in the user interface.

![User interface of the `Semi-Automatic Classification Plugin` for QGIS.\label{fig:plugin_interface}](plugin_interface.png)

The interface allows to define an image input (named `band set`) which is the set of raster bands to be processed.

The following tools are available for `preprocessing`:

* Conversion to reflectance for ASTER, GOES, Landsat, MODIS, Sentinel-1, Sentinel-2, and Sentinel-3 images;
* Clip multiple rasters at once;
* Cloud masking based on the values of a raster mask;
* Mosaic band sets, merging the corresponding bands of two or more band sets;
* Statistic calculation for neighbor pixels;
* Reprojection of the coordinates of raster bands;
* Splitting or stacking raster bands in a unique file;
* Vector to raster conversion.

The following `processing` tools are available:

* Band combination to get a raster where each value corresponds to a combination of input values;
* Clustering for unsupervised classification (i.e. without training input);
* Principal Component Analysis of band set;
* Calculation of the spectral distance between every corresponding pixel of two band sets; 
* Classification using one of the available algorithms, such as Minimum Distance [@Richards:2006], Maximum Likelihood [@Richards:2006], Spectral Angle Mapping [@Kruse:1993], and Random Forest [@Breiman:2001].

Considering that semi-automatic classification algorithms require training pixels (i.e. spectral signatures), a specific dock interface for training input creation and spectral signature calculation is available, which allows to create polygons interactively (manually or through region growing) and import spectral libraries such as the USGS Spectral Library [@Kokaly:2017].
The interface allows to create classification previews on small portion of the image to assess the results before launching the classification process for the whole image.
In addition, the plot of spectral signatures can be visualized in order to assess the spectral separability of signatures.

A band calculator is available for performing mathematical and conditional calculation using input rasters, for instance for the calculation of spectral indices.

The following `postprocessing` tools are available for refining the classification output and further analyses:

* Accuracy assessment of the classification;
* Classification dilation, erosion, and sieve for refining the patches of the classes;
* Classification report for calculation of class statistics such as number of pixels, percentage and area;
* Conversion of classification from raster to vector;
* Manual editing of raster values;
* Assessment of land cover change comparing two classifications;
* Statistics related to an input raster for every unique value of a reference vector or raster;
* Reclassification of raster values.

Finally, the tool `Batch` allows for performing a series of functions consecutively and automatically through the definition of a script.

The `Semi-Automatic Classification Plugin` for [QGIS](https://github.com/qgis/QGIS) is developed with [Python 3](https://github.com/python) and requires the installation of [GDAL](https://github.com/OSGeo/gdal), [NumPy](https://github.com/numpy/numpy), [SciPy](https://github.com/scipy/scipy), and [Matplotlib](https://github.com/matplotlib/matplotlib) (as illustrated in \autoref{fig:plugin_framework}).
The user interface is developed using the [Qt framework](https://doc.qt.io).
The additional installation of SNAP [@SNAP] is required for the Sentinel-1 preprocessing and random forest classification tools.

![Framework of the `Semi-Automatic Classification Plugin` main dependencies.\label{fig:plugin_framework}](plugin_framework.png)

A testing tool is available for verifying the correct installation of the required dependencies and check the main functions of the `Semi-Automatic Classification Plugin`.

# Acknowledgements

The first version of the Semi-Automatic Classification Plugin was developed by Luca Congedo in 2012 for the [ACC Dar Project](http://www.planning4adaptation.org) in order to create a tool for the classification of land cover in an affordable and automatic fashion; following versions 2, 3, 4, and 5 of Semi-Automatic Classification Plugin were developed by Luca Congedo as personal commitment to the remote sensing field and open source philosophy. 
Semi-Automatic Classification Plugin version 6 was developed in the frame of Luca Congedo’s PhD in Landscape and Environment at Sapienza University of Rome. 
`Semi-Automatic Classification Plugin` version 7 was developed by Luca Congedo as personal commitment to the remote sensing field and open source philosophy.

Special thanks to all the users for contributing to the Semi-Automatic Classification Plugin and translating the interface and user manual to other languages.

# References