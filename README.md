# This repository contains all analysis script for the multi-model study of the global carbon cycle in the context of TIPMIP/TipESM. 

##### author: Eike E. Köhn
##### date: April 21, 2026

## Contents:

* "00_modules" contains all functionalities to facilitate the multi-model analysis across different servers/clusters.
* "01_postprocessing" contains scripts to compute standardized datasets for each model, such as globally integrated or averaged time series, or time slice maps
* "02_analysis_and_plotting" takes these standardized datasets to perform single model or multi-model analyses.

## To Do:

* so far, the global average/integral time series calculation does not take the land or ocean area fraction (sftlf, sftof) into account. Need to implement for the relevant models.

  
