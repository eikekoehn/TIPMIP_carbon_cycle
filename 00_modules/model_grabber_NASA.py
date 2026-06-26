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

    def get_rootdir(): #,server='cineca'):
        server = MISCgrabber.get_server()
        if server == 'spirit':
            rootdir = '/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2'
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/NASA-GISS/GISS-E2-1-G-CC2'
        elif server == 'cineca':
            raise Exception('No data for GISSE2.1-G-CC2 available.') 
        return rootdir
        
    def get_member():
        server = MISCgrabber.get_server()
        if server == 'spirit':
            member = 'r0i0p0f0'
        elif server == 'levante':
            member = 'r1i1p1f3'
        elif server == 'cineca':
            raise Exception('No data for GISSE2.1-G-CC2 available.') 
        return member

    def get_exercise(run):
        if run in ['esm-hist','esm-piControl']:
            exercise = 'CMIP'
        else:
            exercise = 'TIPMIP'
        return exercise

    def get_domain(varia,freq_input):
        server = MISCgrabber.get_server()
        
        if server == 'spirit':

            #%%
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

        #%%
        elif server == 'levante':
            if freq_input == 'monthly' and varia in ["hfls", "tas", "clwvi", "tauu", "evspsbl", "prw", "tasmin", "vas", "pr", "psl", "rsut", "tasmax", "hfss", "uas", "rsutcs", "clt", "rsdt", "prsn", "rlutcs", "tauv", "rlut"]:
                domain = 'AP'
            elif freq_input == 'monthly' and varia in ["snc", "snd", "sbl", "snw"]:
                domain = 'LI'
            elif freq_input == 'monthly' and varia in ["cSoil", "lai", "mrros", "npp", "nbp", "ra", "baresoilFrac", "mrsol", "tsl", "gpp", "treeFrac", "mrro", "sftgif", "rh"]:
                domain = 'LP'
            elif freq_input == 'monthly' and varia in ["intdic", "intpp", "chldiatos", "chlos", "epc100", "fgco2", "intppdiat"]:
                domain = 'OB'
            elif freq_input == 'monthly' and varia in ["si", "no3", "dissic"]:
                domain = 'OB'
            elif freq_input == 'monthly' and varia in ["sos", "wfo", "mlotst", "hfds", "zos", "tos", "zostoga"]:
                domain = 'OP'
            elif freq_input == 'monthly' and varia in ["so", "vo", "thetao", "uo", "agessc"]:
                domain = 'OP'
            elif freq_input == 'monthly' and varia in ["simass", "siv", "sithick", "siu", "sivol"]:
                domain = 'SI'    
        
        return domain  

    def get_domain_suffix(varia,freq_input):
        
        server = MISCgrabber.get_server()
        
        if server == 'spirit':
            domain_suffix = ''
        elif server == 'levante':
            if freq_input == 'monthly' and varia in ["hfls", "tas", "clwvi", "tauu", "evspsbl", "prw", "tasmin", "vas", "pr", "psl", "rsut", "tasmax", "hfss", "uas", "rsutcs", "clt", "rsdt", "prsn", "rlutcs", "tauv", "rlut"]:
                domain_suffix = ''
            elif freq_input == 'monthly' and varia in ["snc", "snd", "sbl", "snw"]:
                domain_suffix = ''
            elif freq_input == 'monthly' and varia in ["cSoil", "lai", "mrros", "npp", "nbp", "ra", "baresoilFrac", "mrsol", "tsl", "gpp", "treeFrac", "mrro", "sftgif", "rh"]:
                domain_suffix = ''
            elif freq_input == 'monthly' and varia in ["intdic", "intpp", "chldiatos", "chlos", "epc100", "fgco2", "intppdiat"]:
                domain_suffix = ''
            elif freq_input == 'monthly' and varia in ["si", "no3", "dissic"]:
                domain_suffix = 'Lev'
            elif freq_input == 'monthly' and varia in ["sos", "wfo", "mlotst", "hfds", "zos", "tos", "zostoga"]:
                domain_suffix = ''
            elif freq_input == 'monthly' and varia in ["so", "vo", "thetao", "uo", "agessc"]:
                domain_suffix = 'Lev'
            elif freq_input == 'monthly' and varia in ["simass", "siv", "sithick", "siu", "sivol"]:
                domain_suffix = ''   
        
        return domain_suffix  

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
        server = MISCgrabber.get_server()
        domain = NASAgrabber.get_domain(varia,freq_input)
        if domain in ['L','E','A','AP','LI','LP']:
            if server == 'spirit':
                area_file = './../00_modules/support_data/axyp.nc' #'/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2/area_arrays/axyp.nc'
            elif server == 'levante':
                area_file = './../00_modules/support_data/areacella_fx_GISS-E2-1-G_piControl_r1i1p1f1_gn.nc' #'/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2/area_arrays/axyp.nc'
            area_ds = xr.open_dataset(area_file)
            if 'axyp' in area_ds.variables:
                area = area_ds['axyp'].fillna(0).compute()
            elif 'areacella' in area_ds.variables:
                area = area_ds['areacella'].fillna(0).compute()
            else:
                raise Exception('no area found')
            area_ds.close()
        elif domain in ['Si','O','OB','OP','SI']:
            if server == 'spirit':
                area_file = './../00_modules/support_data/oxyp.nc' #'/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2/area_arrays/oxyp.nc'
            elif server == 'levante':
                area_file = './../00_modules/support_data/areacello_Ofx_GISS-E2-1-G_piControl_r1i1p1f1_gn.nc' 
            area_ds = xr.open_dataset(area_file)
            if 'oxyp' in area_ds.variables:
                area = area_ds['oxyp'].fillna(0).compute()
            elif 'areacello' in area_ds.variables:
                area = area_ds['areacello'].fillna(0).compute()
                area = area.assign_coords(lat=xr.where(area.lat == -89.5, -90,xr.where(area.lat == 89.5, 90, area.lat)))
                print(area)
            else:
                raise Exception('no area found')
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

    def get_grid(varia,freq_input):
        grid = 'gn'
        return grid
        
    
    def get_filelist(varia,run,freq_input):
     
        member = NASAgrabber.get_member()
        exercise = NASAgrabber.get_exercise(run)
        rootdir = NASAgrabber.get_rootdir()
        freq = NASAgrabber.get_frequency(freq_input) 
        domain = NASAgrabber.get_domain(varia,freq_input)
        domain_suffix = NASAgrabber.get_domain_suffix(varia,freq_input)
        grid = NASAgrabber.get_grid(varia,freq_input)

        server = MISCgrabber.get_server()
        if server == 'spirit':
            run_mapped = NASAgrabber.map_run_names(run)
            data_path = f'{rootdir}/{run_mapped}' 
            pattern = f"/{varia}_*_{run_mapped}_*.nc" 
            #print(data_path+pattern)
            file_list = sorted(glob.glob(data_path+pattern,recursive=True))
            #print(file_list)
            file_list_filtered = file_list #MISCgrabber.filter_longest_period_files(file_list)
            #print(file_list_filtered)
            
        elif server == 'levante':
            if run in ['esm-up2p0-gwl4p0-50y-dn2p0','esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0']:
                data_path = f'{rootdir}/{run}/{domain}{freq}{domain_suffix}/{varia}/{grid}/' 
                pattern = f"/v*/{varia}_*_{run}_*.nc" 
                #print(data_path+pattern)
                file_list = sorted(glob.glob(data_path+pattern,recursive=True))                
            else:
                data_path = f'{rootdir}/{run}/{member}/{domain}{freq}{domain_suffix}/{varia}/{grid}/' 
                pattern = f"/v*/{varia}_*_{run}_*.nc" 
                #print(data_path+pattern)
                file_list = sorted(glob.glob(data_path+pattern,recursive=True))
            #print(file_list)
            file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
            #print(file_list_filtered)
        elif server == 'cineca':
            raise Exception('No data for GISSE2.1-G-CC2 available.') 
        else:
            raise Exception('unknown server')

        return file_list_filtered

    def get_horizontal_dimensions(varia):
        server = MISCgrabber.get_server()

        domain = NASAgrabber.get_domain(varia)
        if domain in ['O']:
            dims = ('lato','lono')
        elif domain in ['OB','OP']:
            dims = ('lat','lon')
        elif domain in ['SI']:
            if server == 'spirit':
                dims = ('lato','lono')
            elif server == 'levante':
                dims = ('lat','lon')
        elif domain in ['L','E','A','AP','LI','LP']:
            dims = ('lat','lon')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    def get_area_fraction(varia):
        server = MISCgrabber.get_server()

        if varia in ['nbp','npp','cLand','cVeg','cSoil','cLitter','cCwd','cProduct','cLeaf','cStem','cRoot','cWood','cSoilFast','cSoilMedium','cSoilSlow','cSoilAbove1m']:
            indir = './../00_modules/support_data' #'/data/ekoehn/TIPMIP/NASA-GISS/GISSE2.1-G-CC2/area_arrays'
            land_area_fraction_ds = xr.open_dataset(f'{indir}/sftlf_fx_GISS-E2-1-G-CC_piControl_r1i1p1f1_gn.nc')
            area_fraction = land_area_fraction_ds.sftlf/100. 
            area_fraction = area_fraction.assign_coords(
                lon=(((area_fraction.lon + 180) % 360) - 180)
            )
            if server == 'spirit':
                area_fraction = area_fraction.sortby('lon')
                area_fraction = area_fraction.assign_coords(lat=xr.where(area_fraction.lat == -89, -90,xr.where(area_fraction.lat == 89, 90, area_fraction.lat)))
        else:
            print('... no area fractions used')
            area_fraction = None
        return area_fraction
    
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
        #print('-------------')
        #print(ds[varia].units)
        
        # now choose the data array
        da = ds[varia]
        if verbose_level > 0:
            print(da) 

        server = MISCgrabber.get_server()
        if server == 'spirit':
            da.attrs['units'] = ds.attrs.get('units')
        elif server == 'levante':
            da.attrs['units'] = ds[varia].attrs.get('units')

        
        return da
 
