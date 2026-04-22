"""
this file is to access model output from the GISSE2.1-G-CC2.
author: Eike Köhn
date: Apr 20, 2026
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import glob
import cftime

# custom mdoules
from misc_functions import DataFuncs
from misc_functions import MISCgrabber
from operations_time import TimeOperator 


class NASAgrabber:

    def get_rootdir(server='spirit'):
        if server == 'spirit':
            rootdir = '/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2'
        else:
            raise Exception('No data for GISSE2.1-G-CC2 available.') 
        return rootdir

    def get_member():
        member = 'r0i0p0f0'
        return member

    def get_exercise(run):
        if run in ['esm-hist','esm-piControl']:
            exercise = 'CMIP'
        else:
            exercise = 'TIPMIP'
        return exercise

    def get_domain(varia,freq_input):
        if varia in ['chldiatos', 'dfe', 'dissic', 'intdic', 'dissocos', 'epc100', 'epsi100', 'fgo2', 'hfds', 'limfediat', 'limirrdiat', 'limndiat', 'masso', 'msftyz', 'no3os', 'o2os', 'phydiatos', 'po4', 'si', 'so', 'talk', 'tauuo', 'thetao', 'tos', 'uo', 'vo', 'wmo', 'zmesoos', 'zos', 'chlmiscos', 'dfeos', 'dissicos', 'dpco2', 'epcalc100', 'fgco2', 'friver', 'intpp', 'limfemisc', 'limirrmisc', 'limnmisc', 'mlotst', 'no3', 'o2', 'ph', 'phymiscos', 'po4os', 'sios', 'sos', 'talkos', 'tauvo', 'thkcello', 'umo', 'vmo', 'wfo', 'wo', 'zmicroos', 'zostoga']: 
            domain = 'O'
        elif varia in ['siconc', 'sisnthick', 'sispeed', 'sitemptop', 'sithick', 'siu', 'siv', 'sivol']:
            domain = 'Si'
        elif varia in ['c3PftFrac', 'cLeaf', 'cProduct', 'cVeg', 'gpp', 'landCoverFrac', 'mrso', 'npp', 'rh', 'treeFracPrimEver', 'c4PftFrac', 'cLitter', 'cRoot', 'fVegLitter', 'lai', 'mrros', 'nbp', 'ra', 'treeFracPrimDec']:
            domain = 'L'
        elif varia in ['cLand', 'cOther', 'cSoil', 'cStem', 'cWood', 'fAnthDisturb', 'fDeforestToProduct', 'fLuc', 'fProductDecomp', 'nep']:
            domain = 'E'
        elif varia in ['clivi', 'co2', 'fco2antt', 'hur', 'pr', 'prw', 'rlds', 'rlut', 'rsdscs', 'rsuscs', 'sfcWind', 'tasmax', 'tauv', 'uas', 'wap', 'clt', 'co2mass', 'hfls', 'hus', 'prc', 'ps', 'rldscs', 'rlutcs', 'rsdt', 'rsut', 'ta', 'tasmin', 'ts', 'va', 'clwvi', 'evspsbl', 'hfss', 'huss', 'prsn', 'psl', 'rlus', 'rsds', 'rsus', 'rsutcs', 'tas', 'tauu', 'ua', 'vas']:
            domain = 'A'
        else:
            raise Exception(f'No domain is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain  

    def get_frequency(freq_input='monthly'):
        if freq_input == 'monthly':
            frequency = 'mon'
        elif freq_input == 'yearly':
            frequency = 'yr'
        return frequency

    #def get_grid(varia,freq_input): 
    #    domain = IPSLgrabber.get_domain(varia,freq_input)
    #    if domain in ['L','E','A','']:
    #        grid = 'gr'
    #    elif domain in ['O','SI']:
    #        grid = 'gn' 
    #    else:
    #        raise Exception('Variable not in known domain.')
    #    return grid

    def get_area(varia,freq_input):
        domain = NASAgrabber.get_domain(varia,freq_input)
        if domain in ['L','E','A']:
            area_file = '/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2/area_arrays/axyp.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['axyp'].fillna(0).compute()
            area_ds.close()
        elif domain in ['Si','O']:
            area_file = '/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2/area_arrays/oxyp.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['oxyp'].fillna(0).compute()   
            area_ds.close()       
        else:
            raise Exception('Variable not in known domain.')
        return area

    def map_run_names(run):
        if run == 'esm-piControl':
            run_mapped = 'pi-Control'
        elif run == 'esm-up2p0':
            run_mapped = 'up2p0'
        elif run == 'esm-up2p0-gwl2p0':
            run_mapped = 'swl2p0'
        elif run == 'esm-up2p0-gwl4p0':
            run_mapped = 'swl4p0'
        elif run == 'esm-up2p0-gwl2p0-50y-dn2p0':
            run_mapped = 'up2p0-swl2p0-50y-dn2p0'
        elif run == 'esm-up2p0-gwl4p0-50y-dn2p0':
            run_mapped = 'up2p0-swl4p0-50y-dn2p0'        
        elif run == 'esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0':
            run_mapped = 'up2p0-swl4p0-50y-dn2p0-swl2p0'
        else:
            raise Exception('No name mapped to this run')
        return run_mapped
    
    def get_filelist(varia,run,freq_input):
     
        member = NASAgrabber.get_member()
        exercise = NASAgrabber.get_exercise(run)
        rootdir = NASAgrabber.get_rootdir()
        freq = NASAgrabber.get_frequency(freq_input) 
        domain = NASAgrabber.get_domain(varia,freq_input)
        #grid = NASAgrabber.get_grid(varia,freq_input)

        run_mapped = NASAgrabber.map_run_names(run)
        
        data_path = f'{rootdir}/{run_mapped}' 
        pattern = f"/{varia}_*_{run_mapped}_*.nc" 
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        #print(file_list)
        file_list_filtered = file_list #MISCgrabber.filter_longest_period_files(file_list)
        #print(file_list_filtered)

        return file_list_filtered

    def get_horizontal_dimensions(varia):
        domain = IPSLgrabber.get_domain(varia)
        if domain in ['O','SI']:
            dims = ('lato','lono')
        elif domain in ['L','E','A']:
            dims = ('lat','lon')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    #def get_thickness(varia,run,ds):
    #    print('We have 4D dataset "ds". We need to get the vertical thickness of the grid cells.')
    #    thickness_list = IPSLgrabber.get_filelist('thkcello',run)
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
        files = NASAgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        #print(ds)

        # adjust the time axis if necessary
        ds = TimeOperator.adjust_time_axis(ds)
        #print(ds)
        
        # now choose the data array
        da = ds[varia]
        if verbose_level > 0:
            print(da) 

        da.attrs['units'] = ds.attrs.get('units')

        
        return da
 
