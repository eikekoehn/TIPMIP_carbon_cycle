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
from misc_functions import DataFuncs
from misc_functions import MISCgrabber


class UBERNgrabber:

    def get_rootdir(server='spirit'):
        if server == 'spirit':
            rootdir = '/projets/TipESM/UBERN/CMIP6Plus/TIPMIP/UBERN/GFDL-ESM2M'
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
        if freq_input == 'daily' and varia in ['ua8', 'hus8', 'rlds', 'tas', 'prc', 'clt', 'ts', 'pr', 'ps', 'rsds', 'psl', 'sfcWind', 'va8', 'prra']:
            domain = 'AP'
        elif freq_input == 'fx' and varia in ['areacella', 'sftlf']:
            domain = 'AP'
        elif freq_input == 'monthly' and varia in ['tauu', 'co2mass', 'hfls', 'co2', 'evspsbl', 'rlds', 'zg', 'vas', 'rsutcs', 'hus19', 'tas', 'co2s', 'prc', 'rsus', 'rsuscs', 'clt', 'hur', 'rluscs', 'tasmin', 'prw', 'pr', 'ps', 'rlutcs', 'va19', 'tasmax', 'prsn', 'rsds', 'rsut', 'psl', 'ta', 'clwvi', 'rsdscs', 'rlut', 'ua19', 'hurs', 'tauv', 'rldscs', 'wap', 'clivi', 'rsdt', 'uas', 'hfss', 'rlus']:
            domain = 'AP'
        elif freq_input == 'monthly' and varia in ['cl', 'cli', 'clw']:
            domain = 'AP'
        elif freq_input == 'monthly' and varia in ['sbl', 'sftgrf', 'snw', 'snm', 'snd']:
            domain = 'LI'
        elif freq_input == 'fx' and varia in ['slthick', 'wilt', 'orog']:
            domain = 'LP'
        elif freq_input == 'monthly' and varia in ['tsl', 'residualFrac', 'evspsblsoi', 'cVeg', 'evspsblveg', 'cSoil', 'lai', 'fFireAll', 'cropFrac', 'npp', 'rhSoil', 'cLand', 'mrsol', 'burntFractionAll', 'cWood', 'sftgif', 'mrsll', 'landCoverFrac', 'mrro', 'gpp', 'nbp', 'ra', 'vegFrac', 'mrfso', 'treeFrac', 'grassFrac', 'grassFracC3', 'rh', 'mrsos', 'mrtws', 'fracLut', 'pastureFrac', 'cRoot', 'grassFracC4', 'mrsfl', 'cLeaf', 'nep', 'tran', 'mrso']:
            domain = 'LP'
        elif freq_input == 'monthly' and varia in ['epc100', 'dissic', 'chldiatos', 'no3os', 'intpp', 'fgco2', 'epcalc100', 'fgo2', 'po4os', 'intppdiat', 'intdic', 'chlos', 'o2os']:
            domain = 'OB'
        elif freq_input == 'monthly' and varia in ['talk', 'ph', 'no3', 'o2']:
            domain = 'OB'
        elif freq_input == 'yearly' and varia in ['po4', 'no3', 'si', 'dfe', 'o2']:
            domain = 'OB'
        elif freq_input == 'daily' and varia in ['tossq', 'tos']:
            domain = 'OP'
        elif freq_input == 'fx' and varia in ['areacello']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['zostoga', 'hfx', 'tosga', 'sob', 'hfy', 'mlotst', 'evs', 'friver', 'sos', 'sosga', 'tob', 'soga', 'zos', 'wfo', 'thetaoga', 'tauvo', 'masso', 'pbo', 'volo', 'msftbarot', 'tos', 'hfds', 'tauuo', 'mlotstmin', 'mlotstmax']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['msftyz', 'wmo', 'thkcello', 'vo', 'so', 'vmo', 'uo', 'volcello', 'thetao', 'obvfsq', 'umo', 'masscello', 'wo', 'agessc']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['hfbasinpmadv', 'hfbasin']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['sitemptop', 'sisnmass', 'sisnconc', 'sithick', 'sispeed', 'siconc', 'siconca', 'siu', 'sivol', 'siv', 'simass', 'sisnthick']:
            domain = 'SI'
        else:
            raise Exception(f'No domain is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain  

    def get_domain_suffix(varia,freq_input):
        if freq_input == 'daily' and varia in ['ua8', 'hus8', 'rlds', 'tas', 'prc', 'clt', 'ts', 'pr', 'ps', 'rsds', 'psl', 'sfcWind', 'va8', 'prra']:
            domain_suffix = ''
        elif freq_input == 'fx' and varia in ['areacella', 'sftlf']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['tauu', 'co2mass', 'hfls', 'co2', 'evspsbl', 'rlds', 'zg', 'vas', 'rsutcs', 'hus19', 'tas', 'co2s', 'prc', 'rsus', 'rsuscs', 'clt', 'hur', 'rluscs', 'tasmin', 'prw', 'pr', 'ps', 'rlutcs', 'va19', 'tasmax', 'prsn', 'rsds', 'rsut', 'psl', 'ta', 'clwvi', 'rsdscs', 'rlut', 'ua19', 'hurs', 'tauv', 'rldscs', 'wap', 'clivi', 'rsdt', 'uas', 'hfss', 'rlus']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['cl', 'cli', 'clw']:
            domain_suffix = 'Lev'
        elif freq_input == 'monthly' and varia in ['sbl', 'sftgrf', 'snw', 'snm', 'snd']:
            domain_suffix = ''
        elif freq_input == 'fx' and varia in ['slthick', 'wilt', 'orog']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['tsl', 'residualFrac', 'evspsblsoi', 'cVeg', 'evspsblveg', 'cSoil', 'lai', 'fFireAll', 'cropFrac', 'npp', 'rhSoil', 'cLand', 'mrsol', 'burntFractionAll', 'cWood', 'sftgif', 'mrsll', 'landCoverFrac', 'mrro', 'gpp', 'nbp', 'ra', 'vegFrac', 'mrfso', 'treeFrac', 'grassFrac', 'grassFracC3', 'rh', 'mrsos', 'mrtws', 'fracLut', 'pastureFrac', 'cRoot', 'grassFracC4', 'mrsfl', 'cLeaf', 'nep', 'tran', 'mrso']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['epc100', 'dissic', 'chldiatos', 'no3os', 'intpp', 'fgco2', 'epcalc100', 'fgo2', 'po4os', 'intppdiat', 'intdic', 'chlos', 'o2os']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['talk', 'ph', 'no3', 'o2']:
            domain_suffix = 'Lev'
        elif freq_input == 'yearly' and varia in ['po4', 'no3', 'si', 'dfe', 'o2']:
            domain_suffix = 'Lev'
        elif freq_input == 'daily' and varia in ['tossq', 'tos']:
            domain_suffix = ''
        elif freq_input == 'fx' and varia in ['areacello']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['zostoga', 'hfx', 'tosga', 'sob', 'hfy', 'mlotst', 'evs', 'friver', 'sos', 'sosga', 'tob', 'soga', 'zos', 'wfo', 'thetaoga', 'tauvo', 'masso', 'pbo', 'volo', 'msftbarot', 'tos', 'hfds', 'tauuo', 'mlotstmin', 'mlotstmax']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['msftyz', 'wmo', 'thkcello', 'vo', 'so', 'vmo', 'uo', 'volcello', 'thetao', 'obvfsq', 'umo', 'masscello', 'wo', 'agessc']:
            domain_suffix = 'Lev'
        elif freq_input == 'monthly' and varia in ['hfbasinpmadv', 'hfbasin']:
            domain_suffix = 'Z'
        elif freq_input == 'monthly' and varia in ['sitemptop', 'sisnmass', 'sisnconc', 'sithick', 'sispeed', 'siconc', 'siconca', 'siu', 'sivol', 'siv', 'simass', 'sisnthick']:
            domain_suffix = ''
        else:
            raise Exception(f'No domain suffix is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain_suffix  

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
        if domain in ['AP','LI','LP']:
            #area_file = '/home/ekoehn/jobs/jupyter/TipESM/carbon_cycle_reversibility/model_grids/areacella_fx_GFDL-ESM2M_historical_r0i0p0.nc'
            area_file = '/projets/TipESM/UBERN/CMIP6Plus/TIPMIP/UBERN/GFDL-ESM2M/esm-piControl/r1i1p1f1/APfx/areacella/gn/v20250510/areacella_APfx_GFDL-ESM2M_esm-piControl_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacella'].compute()
            #area = area.rename({'lat':'latitude','lon':'longitude'})
            area_ds.close()
        elif domain in ['OB','OP','SI']:
            #area_file = '/home/ekoehn/jobs/jupyter/TipESM/carbon_cycle_reversibility/model_grids/areacello_Ofx_GFDL-ESM2M_faf-all_r1i1p1f1_gn.nc'
            area_file = '/projets/TipESM/UBERN/CMIP6Plus/TIPMIP/UBERN/GFDL-ESM2M/esm-piControl/r1i1p1f1/OPfx/areacello/gn/v20250510/areacello_OPfx_GFDL-ESM2M_esm-piControl_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacello'].fillna(0).compute()
            #area = area.rename({'lat':'geolat_t','lon':'geolon_t'})
            #area = area.rename({'x':'longitude','y':'latitude'})
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
        domain_suffix = UBERNgrabber.get_domain_suffix(varia,freq_input)

        data_path = f'{rootdir}/{run}/{member}/{domain}{freq}{domain_suffix}/{varia}/{grid}/v*' 
        pattern = f"/{varia}*_{grid}_*.nc" 
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered


    def get_horizontal_dimensions(vspecs):
        domain = UBERNgrabber.get_domain(varia)
        if domain in ['OB','OP','SI']:
            dims = ('latitude','longitude')
        elif domain in ['AP','LI','LP']:
            dims = ('latitude','longitude')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    def get_area_fraction(varia):
        if varia in ['nbp','npp','cLand','cVeg','cSoil','cLitter','cCwd','cProduct','cLeaf','cStem','cRoot','cWood','cSoilFast','cSoilMedium','cSoilSlow','cSoilAbove1m']:
            indir = '/projets/TipESM/UBERN/CMIP6Plus/TIPMIP/UBERN/GFDL-ESM2M/esm-piControl/r1i1p1f1/APfx/sftlf/gn/v20250510'
            land_area_fraction_ds = xr.open_dataset(f'{indir}/sftlf_APfx_GFDL-ESM2M_esm-piControl_r1i1p1f1_gn.nc')
            area_fraction = land_area_fraction_ds.sftlf/100. 
        #elif varia in ['fgco2']:
        #    indir = '/projets/TipESM/UBERN/TipESM/GFDL-ESM2M/esm-piControl/r1i1p1f1/Ofx/sftof/gn/v20250510'
        #    ocean_area_fraction_ds = xr.open_dataset(f'{indir}/sftof_Ofx_GFDL-ESM2M_esm-piControl_r1i1p1f1_gn.nc')
        #    area_fraction = ocean_area_fraction_ds.sftof/100. 
        #elif varia in ['fgco2','dissic']: 
        #    indir = '/projets/TipESM/UiB/NorESM2-LM/esm-up2p0/v20251010'
        #    ocean_area_fraction_ds = xr.open_dataset(f'{indir}/sftof_Ofx_NorESM2-LM_esm-up2p0_r1i1p1f1_gn.nc')
        #    area_fraction = ocean_area_fraction_ds.sftof/100.             
        else:
            area_fraction = None
        return area_fraction

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

    def get_dz(varia,run,freq_input='monthly',verbose_level=1):
        
        # get the list of files
        files = UBERNgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        dz = ds['olevel_bnds'].diff(dim='bnds')
        if verbose_level > 0:
            print(dz) 
        
        return dz
 
