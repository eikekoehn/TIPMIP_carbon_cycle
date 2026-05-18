"""
this file is to access model output from ACCESS-ESM1-5.
author: Eike Köhn
date: Apr 20, 2026
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import glob

# custom mdoules
from misc_functions import DataFuncs
from misc_functions import MISCgrabber


class ACCESSgrabber:

    def get_rootdir(server='levante'):
        if server == 'spirit':
            rootdir = '/bdd/CMIP6/CMIP/CSIRO/ACCESS-ESM1-5' 
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/tipesm/ACCESS-ESM1-5'
        elif rootdir == 'cineca':
            raise Exception('No data for ACCESS on cineca.') 
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
        if freq_input == 'monthly' and varia in ['clt', 'co2', 'evspsbl', 'hfls', 'hfss', 'pr', 'prsn', 'prw', 'psl', 'rlut', 'rlutcs', 'rsut', 'rsutcs', 'tas', 'tasmax', 'tasmin', 'tauu', 'tauv', 'ua', 'va', 'zg']:
            domain = 'A'        
        elif freq_input == 'daily' and varia in ['pr', 'tas', 'tasmax', 'tasmin']:
            domain = ''
        elif freq_input == 'monthly' and varia in ['cSoil']:
            domain = 'E'
        elif freq_input == 'monthly' and varia in ['sftgif']:
            domain = 'LI'
        elif freq_input == 'monthly' and varia in ['baresoilFrac', 'cVeg', 'gpp', 'lai', 'mrro', 'mrros', 'npp', 'ra', 'rh', 'treeFrac']:
            domain = 'L'
        elif freq_input == 'fx' and varia in ['areacello']:
            domain = 'O'
        elif freq_input == 'monthly' and varia in ['sftgif', 'sftgrf', 'snd', 'snm', 'snw']:
            domain = 'LI'
        elif freq_input == 'monthly' and varia in ['epc100', 'fgco2', 'hfds', 'intpp', 'mlotst', 'msftmz', 'msftyz', 'o2', 'so', 'sos', 'thetao', 'tos', 'uo', 'vo', 'zos']:
            domain = 'O'
        elif freq_input == 'monthly' and varia in ['siconc', 'simass', 'sisnmass']:
            domain = 'SI'
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
        domain = ACCESSgrabber.get_domain(varia,freq_input)
        if domain in ['L', 'E', 'A', '', 'CF', 'LI']:
            area_file = './../00_modules/support_data/areacella_fx_ACCESS-ESM1-5_piControl_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacella'].compute()
            #area = area.rename({'lat':'latitude','lon':'longitude'})
            area_ds.close()
        elif domain in ['SI','O']:
            area_file = './../00_modules/support_data/areacello_Ofx_ACCESS-ESM1-5_esm-up2p0_r1i1p1f1_gn.nc' #'/work/bm1448/upload/tipesm/ACCESS-ESM1-5/esm-up2p0/r1i1p1f1/Ofx/areacello/v20250428/areacello_Ofx_ACCESS-ESM1-5_esm-up2p0_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacello'].fillna(0).compute()
            #area = area.rename({'lat':'geolat_t','lon':'geolon_t'})
            #area = area.rename({'x':'longitude','y':'latitude'})
            area_ds.close()        
        else:
            raise Exception('Variable not in known domain.')
        return area

    
    def get_filelist(varia,run,freq_input):
     
        member = ACCESSgrabber.get_member()
        exercise = ACCESSgrabber.get_exercise(run)
        rootdir = ACCESSgrabber.get_rootdir()
        freq = ACCESSgrabber.get_frequency(freq_input) 
        domain = ACCESSgrabber.get_domain(varia,freq_input)
        grid = ACCESSgrabber.get_grid()

        data_path = f'{rootdir}/{run}/{member}/{domain}{freq}/{varia}/v*' 
        pattern = f"/{varia}*_{grid}_*.nc" 
        print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        print(file_list)
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered


    def get_horizontal_dimensions(vspecs):
        domain = ACCESSgrabber.get_domain(varia)
        if domain in ['O','SI']:
            dims = ('j','i')
        elif domain in ['L', 'E', 'A', '', 'CF', 'LI']:
            dims = ('lat','lon')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    def get_area_fraction(varia):
        if varia in ['nbp','npp']:
            indir = './../00_modules/support_data'
            land_area_fraction_ds = xr.open_dataset(f'{indir}/sftlf_fx_ACCESS-ESM1-5_piControl_r1i1p1f1_gn.nc')
            area_fraction = land_area_fraction_ds.sftlf/100.             
        else:
            area_fraction = None
        return area_fraction

    def get_data(varia,run,freq_input='monthly',verbose_level=1):
        
        # get the list of files
        files = ACCESSgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        da = ds[varia]
        if verbose_level > 0:
            print(da) 
        
        return da
 
