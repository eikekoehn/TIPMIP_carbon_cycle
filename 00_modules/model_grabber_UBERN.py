"""
this file is to access model output from the GFDL-ESM2M (UBern).
author: Eike Köhn
date: Apr 20, 2026
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import glob

# custom mdoules
from time_module import Timer
from misc_functions import DataFuncs
from misc_functions import MISCgrabber


class UBERNgrabber:

    def get_rootdir(server='spirit'):
        if server == 'spirit':
            rootdir = '/projets/TipESM/UBERN/TipESM/GFDL-ESM2M'
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/urshe/GFDL-ESM2M'
        elif rootdir == 'cineca':
            raise Exception('No data for GFDL-ESM2M on CINECA.') 
        return rootdir

    def get_member():
        member = 'r1i1p1f1'
        return member

    def get_exercise(run):
        if run in ['esm-hist','esm-piControl']:
            exercise = 'CMIP'
        else:
            exercise = 'TIPMIP'
        return exercise

    def get_domain(varia,freq_input):
        if freq_input == 'fx' and varia in ['slthick','wilt']:
            domain = 'E'        
        elif freq_input == 'daily' and varia in ['clt', 'hus', 'huss', 'pr', 'prc', 'psl', 'rlds', 'rsds', 'sfcWind', 'tas', 'ua', 'va']:
            domain = ''
        elif freq_input == 'daily' and varia in ['ps']:
            domain = 'CF'
        elif freq_input == 'daily' and varia in ['ts']:
            domain = 'E'
        elif freq_input == 'daily' and varia in ['tos','tossq']:
            domain = 'O'
        elif freq_input == 'monthly' and varia in ['cl', 'cli', 'clivi', 'clt', 'clw', 'clwvi', 'co2', 'hfls', 'hfss', 'hur', 'hurs', 'hus', 'pr', 'prc', 'prw', 'psl', 'rlds', 'rldscs', 'rlus', 'rluscs', 'rlut', 'rlutcs', 'rsds', 'rsdscs', 'rsdt', 'rsus', 'rsuscs', 'rsut', 'rsutcs', 'ta', 'tas', 'tasmax', 'tasmin', 'tauu', 'tauv', 'ua', 'uas', 'va', 'vas', 'wap', 'zg']:
            domain = 'A'
        elif freq_input == 'monthly' and varia in ['sftgif', 'sftgrf', 'snd', 'snm', 'snw']:
            domain = 'LI'
        elif freq_input == 'monthly' and varia in ['burntFractionAll', 'cLeaf', 'cRoot', 'cropFrac', 'cVeg', 'evspsblsoi', 'evspsblveg', 'gpp', 'grassFrac', 'lai', 'landCoverFrac', 'mrfso', 'mrro', 'mrso', 'nbp', 'npp', 'pastureFrac', 'ra', 'residualFrac', 'rh', 'tran', 'treeFrac', 'tsl']:
            domain = 'L'
        elif freq_input == 'monthly' and varia in ['cLand', 'cSoil', 'cSoilLevels', 'cWood', 'fFireAll', 'fracLut', 'grassFracC3', 'grassFracC4', 'mrsfl', 'mrsll', 'mrsol', 'nep', 'nwdFracLut', 'orog', 'rhSoil', 'vegFrac']:
            domain = 'E'
        elif freq_input == 'monthly' and varia in ['chlos', 'epcalc100', 'fgco2', 'friver', 'hfbasinpmadv', 'hfx', 'intpp', 'masso', 'mlotstmax', 'msftbarot', 'msftyz', 'o2os', 'pbo', 'po4os', 'sob', 'sos', 'talk', 'tauvo', 'thetaoga', 'tob', 'tosga', 'uo', 'vo', 'wfo', 'wo', 'zostoga', 'epc100', 'evs', 'fgo2', 'hfbasin', 'hfds', 'hfy', 'masscello', 'mlotst', 'mlotstmin', 'msftmz', 'no3os', 'obvfsq', 'ph', 'so', 'soga', 'sosga', 'tauuo', 'thetao', 'thkcello', 'tos', 'umo', 'vmo', 'volo', 'wmo', 'zos']:
            domain = 'O'
        elif freq_input == 'monthly' and varia in ['siconc', 'siconca', 'simass', 'sisnconc', 'sisnmass', 'sisnthick', 'sispeed', 'sitemptop', 'sithick', 'siu', 'siv', 'sivol']:
            domain = 'SI'
        elif freq_input == 'yearly' and varia in ['dfe', 'no3', 'o2', 'po4', 'si']:
            domain = 'O'
        else:
            raise Exception(f'No domain is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain  

    def get_frequency(freq_input='monthly'):
        if freq_input == 'daily':
            frequency = 'day'
        elif freq_input == 'monthly':
            frequency = 'mon'
        elif freq_input == 'yearly':
            frequency = 'yr'
        elif freq_input == 'fx':
            frequency = 'fx'
        return frequency

    def get_grid(): 
        grid = 'gn'
        return grid

    def get_area(varia,freq_input):
        domain = UBERNgrabber.get_domain(varia,freq_input)
        if domain in ['L', 'E', 'A', '', 'CF', 'LI']:
            area_file = '/home/ekoehn/jobs/jupyter/TipESM/carbon_cycle_reversibility/model_grids/areacella_fx_GFDL-ESM2M_historical_r0i0p0.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacella'].compute()
            area = area.rename({'lat':'latitude','lon':'longitude'})
            area_ds.close()
        elif domain in ['Si','O']:
            area_file = '/home/ekoehn/jobs/jupyter/TipESM/carbon_cycle_reversibility/model_grids/areacello_Ofx_GFDL-ESM2M_faf-all_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacello'].fillna(0).compute()
            area = area.rename({'lat':'geolat_t','lon':'geolon_t'})
            area = area.rename({'x':'longitude','y':'latitude'})

            area_ds.close()        
        else:
            raise Exception('Variable not in known domain.')
        return area

    
    def get_filelist(varia,run,freq_input):
     
        member = UBERNgrabber.get_member()
        exercise = UBERNgrabber.get_exercise(run)
        rootdir = UBERNgrabber.get_rootdir()
        freq = UBERNgrabber.get_frequency(freq_input) 
        domain = UBERNgrabber.get_domain(varia,freq_input)
        grid = UBERNgrabber.get_grid()

        data_path = f'{rootdir}/{run}/{member}/{domain}{freq}/{varia}/{grid}/v*' 
        pattern = f"/{varia}*_{grid}_*.nc" 
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered


    def get_horizontal_dimensions(vspecs):
        domain = UBERNgrabber.get_domain(varia)
        if domain in ['O','SI']:
            dims = ('latitude','longitude')
        elif domain in ['L', 'E', 'A', '', 'CF', 'LI']:
            dims = ('latitude','longitude')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    #def get_area_fraction(frac_type='land'):
    #    if frac_type == 'land':
    #        indir = '/bdd/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/1pctCO2/r1i1p1f1/fx/sftlf/gr/latest'
    #        land_area_fraction_ds = xr.open_dataset(f'{indir}/sftlf_fx_IPSL-CM6A-LR_1pctCO2_r1i1p1f1_gr.nc')
    #        area_fraction = land_area_fraction_ds.sftlf/100. 
    #    return area_fraction

    def get_data(varia,run,freq_input='monthly',verbose_level=1):
        
        # get the list of files
        files = UBERNgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        da = ds[varia]
        if verbose_level > 0:
            print(da) 
        
        return da
 
