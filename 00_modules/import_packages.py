"""
author: Eike E. Köhn
date: July 29, 2025
description: functions to load in a set of packages required
"""

class PackageGetter:
        
    @staticmethod
    def import_standard_packages_for_analysis_and_plotting():
    
        # import system packages
        import sys
        import os    
        from copy import deepcopy
        import importlib
        from importlib import reload
        import glob
        from joblib import Parallel, delayed
        
        # import netcdf packages
        import netCDF4
        import xarray as xr
        import dask
    
        # import time packages
        import time
        import cftime
        import datetime
        import nc_time_axis
        #import time as tim
    
        # import analysis packages
        import numpy as np
        import numpy.ma as ma
        import pandas as pd
        from scipy import interpolate
        from scipy import stats as spstats
    
        # import plotting packages
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        import matplotlib.ticker as plticker
        from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
        import cmocean as cmo
        #%matplotlib inline
        import matplotlib.colors as mcolors
        import matplotlib.patches as mpatches
    
        # import mapping packages
        import cartopy.crs as ccrs
        import cartopy
        from cartopy.util import add_cyclic_point

        # import ocean packages
        import gsw
    
        # suppress deprecation warnings
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)

        # Local dictionary for return
        return locals()

    
    @staticmethod
    def import_custom_packages(import_spline=True):
        import sys
        sys.path.append('../00_modules/')

        # import the parameters
        from set_params import Models as pmods
        from set_params import Runs as pruns
        from set_params import ModelRuns as pmodruns

        # import the classes for getting model data
        from model_grabber_ALL import MODELgrabber
        from model_grabber_IPSL import IPSLgrabber
        from model_grabber_UBERN import UBERNgrabber
        from model_grabber_NorESM import NorESMgrabber

        # import the class for getting miscellaneous functions
        from misc_functions import DataFuncs as DFuncs

        # import operators for calculations
        from operations_space import SpaceOperator 
        from operations_time import TimeOperator 
        
        # Local dictionary for return
        return locals()
