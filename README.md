# This repository contains all analysis script for the multi-model study of the global carbon cycle in the context of TIPMIP/TipESM. 

##### author: Eike E. Köhn
##### date: April 21, 2026

## Contents:

* "00_modules" contains all functionalities to facilitate the multi-model analysis across different servers/clusters.
* "01_postprocessing" contains scripts to compute standardized datasets for each model, such as globally integrated or averaged time series, or time slice maps
* "02_analysis_and_plotting" takes these standardized datasets to perform single model or multi-model analyses.

## Analyses to be added:

* compute time slice average maps at different global warming levels for each run (31-yr centered means)
* compute regional time series for terrestrial keys regions: Amazon, Congo, Boreal
* compute regional time series for oceanic key regions: North Atlantic, Arctic, Southern Ocean, subtropics/tropics
* time series for total oceanic carbon (dissic/intdic)

## To Do:

* so far, the global average/integral time series calculation does not take the land or ocean area fraction (sftlf, sftof) into account. Need to implement for the relevant models.
* when plotting the time series color coded with the run color, i go backwards so that each run color appears. Overlaying obscures the colors somewhat.

## Double check:

* The reference values so far are taken to be the piControl at the start year of the rampup. Should rather use the 31yr centered mean, but data is not provided by models (i.e., the 15yr leading up to 1850).
* for which models do I need to use land or ocean area fraction (sftlf, sftof) to correctly scale coastal points for regional (flux) integrals/means?
* for UKESM, I shifted esm-piControl backward by 250 years. Correct?
* for UKESM, I used the areacello/areacella fields from UKESM1-0-LL. Ok?
* in general, I use a fixed areacelloa/areacella
* in ECEarth, there are 6 extra latitudes for example in tas, that do not appear in areacella. What to do with those? I subsample for now to match areacella. This seems to be the case only for tas (so far?).
* for NorESM2-LM, I used a temporally fixed thkcello for vertical integration (in IPSL it is temporally varying)