"""
this file is to access model output from the UKESM1-2 model.
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


class UKESMgrabber:

    def get_rootdir(run,server='cineca'):
        if server == 'spirit':
            raise Exception('No data for UKESM1-2 on SPIRIT.') 
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/tipesm/UKESM1-2'
        elif server == 'cineca':
            rootdir = '/g100_store/DRES_OptimESM/ESGF/prepub/mohc'
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
        if freq_input == 'daily' and varia in ['clt', 'hfls', 'hfss', 'hur', 'hurs', 'hus', 'huss', 'mrro', 'mrso', 'mrsos', 'pr', 'prc', 'prsn', 'psl', 'rlds', 'rlus', 'rlut', 'rsds', 'rsus', 'sfcWind', 'sfcWindmax', 'snc', 'snw', 'ta', 'tas', 'tasmax', 'tasmin', 'ua', 'uas', 'va', 'vas', 'wap']:
            domain = ''
        elif freq_input == 'daily' and varia in ['mrsll','mrsol']:
            domain = 'E'
        elif freq_input == 'daily' and varia in ['siconca','sitemptop']:
            domain = 'SI'
        elif freq_input == 'monthly' and varia in ['clivi', 'fco2antt', 'hurs', 'prc', 'psl', 'rlut', 'rsdt', 'rsutcs', 'tasmax', 'ts', 'vas', 'clt', 'hfls', 'hus', 'prsn', 'rlds', 'rlutcs', 'rsus', 'sfcWind', 'tasmin', 'ua', 'wap', 'clwvi', 'hfss', 'huss', 'prw', 'rldscs', 'rsds', 'rsuscs', 'ta', 'tauu', 'uas', 'zg', 'evspsbl', 'hur', 'pr', 'ps', 'rlus', 'rsdscs', 'rsut', 'tas', 'tauv', 'va']:
            domain = 'A'
        elif freq_input == 'monthly' and varia in ['sbl', 'snc', 'snd', 'snm', 'snw']:
            domain = 'LI'
        elif freq_input == 'monthly' and varia in ['baresoilFrac', 'cRoot', 'evspsblsoi', 'grassFrac', 'mrro', 'mrsos', 'ra', 'tran', 'cLeaf', 'cropFrac', 'evspsblveg', 'lai', 'mrros', 'nbp', 'residualFrac', 'treeFrac', 'cProduct', 'cVeg', 'gpp', 'mrfso', 'mrso', 'npp', 'rh']:
            domain = 'L'
        elif freq_input == 'monthly' and varia in ['cLand', 'cSoil', 'fDeforestToProduct', 'fracLut', 'laiLut', 'netAtmosLandCO2Flux', 'thetaot', 'cropFracC3', 'cStem', 'fLuc', 'grassFracC3', 'mrsll', 'nppLut', 'vegFrac', 'cropFracC4', 'fAnthDisturb', 'fProductDecomp', 'grassFracC4', 'mrsol', 't20d']:
            domain = 'E'
        elif freq_input == 'monthly' and varia in ['chlmiscos', 'fgo2', 'htovovrt', 'intppmisc', 'masscello', 'o2os', 'sos', 'thkcello', 'vo', 'chlos', 'fric', 'intdic', 'limfediat', 'masso', 'obvfsq', 'sosga', 'tob', 'volo', 'dpco2', 'friver', 'intpbfe', 'limfemisc', 'mlotst', 'pbo', 'spco2', 'tos', 'wmo', 'epc100', 'hfbasin', 'intpbsi', 'limirrdiat', 'mlotstmax', 'sios', 'tauuo', 'tosga', 'wo', 'epcalc100', 'hfbasinpmadv', 'intpoc', 'limirrmisc', 'mlotstmin', 'so', 'tauvo', 'umo', 'zos', 'epsi100', 'hfds', 'intpp', 'limndiat', 'msftyz', 'sob', 'thetao', 'uo', 'zostoga', 'fgco2', 'htovgyre', 'intppdiat', 'limnmisc', 'no3os', 'soga', 'thetaoga', 'vmo']:
            domain = 'O'
        elif freq_input == 'monthly' and varia in ['siconc', 'simass', 'sisnthick', 'sitemptop', 'sitimefrac', 'siv', 'siconca', 'sisnmass', 'sispeed', 'sithick', 'siu', 'sivol']:
            domain = 'SI'
        else:
            raise Exception(f'No domain is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain  

    def get_frequency(freq_input='monthly'):
        if freq_input == 'monthly':
            frequency = 'mon'
        elif freq_input == 'yearly':
            frequency = 'yr'
        return frequency

    def get_grid(varia,freq_input): 
        domain = UKESMgrabber.get_domain(varia,freq_input)
        if domain == 'SI' and varia in ['siconca','sitemptop']:
            grid = 'gr'
        elif domain == 'O' and varia in ['hfbasin','hfbasinpmadv','htovgyre','htovovrt']:
            grid = 'gnz'
        elif domain == 'O' and varia in ['masso','soga','sosga','thetaoga','tosga','volo','zostoga']:
            grid = 'gm'
        else:
            grid = 'gn' 
        #else:
        #    raise Exception('Variable not in known domain.')
        return grid

    def get_area(varia,freq_input):
        domain = UKESMgrabber.get_domain(varia,freq_input)
        area_path = '/g100/home/userexternal/ekoehn00/jobs/TipESM/carbon_cycle_reversibility/model_grids'
        if domain in ['L','E','A']:
            area_file = f'{area_path}/areacella_fx_UKESM1-0-LL_piControl_r1i1p1f2_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacella'].compute()
            area_ds.close()
        elif domain in ['Si','O']:
            area_file = f'{area_path}/areacello_Ofx_UKESM1-0-LL_piControl_r1i1p1f2_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacello'].fillna(0).compute()
            #area = area.rename({'y':'j','x':'i'})
            #area = area.rename({'nav_lat':'latitude','nav_lon':'longitude'})
            area_ds.close()       
        else:
            raise Exception('Variable not in known domain.')
        return area

    def get_filelist(varia,run,freq_input):
     
        member = UKESMgrabber.get_member()
        exercise = UKESMgrabber.get_exercise(run)
        rootdir = UKESMgrabber.get_rootdir(run)
        freq = UKESMgrabber.get_frequency(freq_input) 
        domain = UKESMgrabber.get_domain(varia,freq_input)
        grid = UKESMgrabber.get_grid(varia,freq_input)

        data_path = f'{rootdir}/2*/CMIP6/CMIP/MOHC/UKESM1-2/{run}/{member}/{domain}{freq}/{varia}/{grid}/v*' 
        pattern = f"/{varia}*_{grid}_*.nc" 
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered

    def get_horizontal_dimensions(varia):
        domain = UKESMgrabber.get_domain(varia)
        if domain in ['O','SI']:
            dims = ('j','i')
        elif domain in ['L','E','A']:
            dims = ('lat','lon')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    #def get_thickness(varia,run,ds):
    #    print('We have 4D dataset "ds". We need to get the vertical thickness of the grid cells.')
    #    thickness_list = UKESMgrabber.get_filelist('thkcello',run)
    #    thkcello_ds = xr.open_mfdataset(thickness_list,use_cftime=True)
    #    thkcello = thkcello_ds['thkcello']
    #    # Make sure thkcello has the same temporal dimension as the dataset to be analyzed
    #    tsel = ds[varia].time.shape[0]
    #    thkcello = thkcello.sel(time=slice(ds.time.min(), ds.time.max()))
    #    # Fill the nans with 0 for weighting
    #    thickness = thkcello.fillna(0)        
    #    return thickness

    #def get_area_fraction(frac_type='land'):
    #    if frac_type == 'land':
    #        indir = '/bdd/CMIP6/CMIP/IPSL/IPSL-CM6A-LR/1pctCO2/r1i1p1f1/fx/sftlf/gr/latest'
    #        land_area_fraction_ds = xr.open_dataset(f'{indir}/sftlf_fx_IPSL-CM6A-LR_1pctCO2_r1i1p1f1_gr.nc')
    #        area_fraction = land_area_fraction_ds.sftlf/100. 
    #    return area_fraction

    def get_data(varia,run,freq_input='monthly',verbose_level=1):
        
        # get the list of files
        files = UKESMgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        da = ds[varia]
        if verbose_level > 0:
            print(da) 
        
        return da
 
