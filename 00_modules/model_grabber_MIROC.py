"""
this file is to access model output from the MIROC-ES2L model.
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


class MIROCgrabber:

    def get_rootdir(run,server='levante'):
        if server == 'spirit':
            raise Exception('No data for MIROC-ES2L on spirit.') 
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/tipesm/IPSL-CM6-ESMCO2'
        elif rootdir == 'cineca':
            raise Exception('No data for MIROC-ES2L on CINECA.') 
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
        if varia in ['depdust'] and freq_input == 'monthly':
            domain = 'AE'
        elif varia in ["clt","hfls","hfss","hur","hurs","hus8","huss","pr","prc","prsn","ps","psl","rlds","rlus","rlut","rsds","rsus","sfcWind","sfcWindmax","ta8","tas","tasmax","tasmin","ua8","uas","va8","vas","wap8"] and freq_input == 'daily':
            domain = 'AP'
        elif varia in ["sftlf"] and freq_input == 'fx':
            domain = 'AP'
        elif varia in ["clivi","clt","clwvi","co2s","evspsbl","hfls","hfss","hur","hurs","hus19","huss","pr","prsn","prw","ps","psl","rlds","rldscs","rlus","rlut","rlutcs","rsds","rsdscs","rsdt","rsus","rsuscs","rsut","rsutcs","rtmt","sfcWind","ta","tas","tauu","tauv","ts","ua19","uas","va19","vas","wap","zg"] and freq_input == 'monthly':
            domain = 'AP'
        elif varia in ["cl","cli","clw"] and freq_input == 'monthly':
            domain = 'AP'
        elif varia in ["snc","snw"] and freq_input == 'daily':
            domain = 'LI'
        elif varia in ["sbl","snc","snd","snm","snw","tsn"] and freq_input == 'monthly':
            domain = 'LI'
        elif varia in ["mrro","mrso","mrsos"] and freq_input == 'daily':
            domain = 'LP'
        elif varia in ["cLand","cLeaf","cLitter","cProduct","cRoot","cropFrac","cSoil","cSoilMedium","cVeg","evspsblsoi","evspsblveg","fLitterSoil","fNdep","fracLut","fVegLitter","gpp","lai","mrfso","mrro","mrros","mrso","mrsos","nbp","netAtmosLandCO2Flux","npp","pastureFrac","ra","residualFrac","rh","tran","tsl"] and freq_input == 'monthly':
            domain = 'LP'
        elif varia in ["chlos","epc100","epcalc100","fgco2","fgo2","intpp","o2os","po4os","spco2"] and freq_input == 'monthly':
            domain = 'OB'
        elif varia in ["talk"] and freq_input == 'monthly':
            domain = 'talk'
        elif varia in ["evs","friver","mlotst","sos","tauuo","tauvo","tos","zos"] and freq_input == 'monthly':
            domain = 'OP'
        elif varia in ["so","thetao","uo","vo","wo"] and freq_input == 'monthly':
            domain = 'OP'
        elif varia in ["sithick","siu","siv"] and freq_input == 'daily':
            domain = 'SI'
        elif varia in ["siconc","sisnthick","sithick","sitimefrac"] and freq_input == 'monthly':
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
        return frequency

    def get_grid(varia,freq_input): 
        domain = MIROCgrabber.get_domain(varia,freq_input)
        if domain in ['AE','AP','LI','LP']:
            grid = 'gn'
        elif domain in ['OB','OP','SI']:
            grid = 'gn' 
        else:
            raise Exception('Variable not in known domain.')
        return grid

    def get_area(varia,freq_input):
        domain = MIROCgrabber.get_domain(varia,freq_input)
        if domain in ['AE','AP','LI','LP']:
            area_file = '/home/ekoehn/jobs/jupyter/TIPMIP_carbon_cycle/00_modules/support_data/areacella_fx_MIROC-ES2L_piControl_r1i1p1f2_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacella'].compute()
            area_ds.close()
        elif domain in ['OB','OP','SI']:
            area_file = '/home/ekoehn/jobs/jupyter/TIPMIP_carbon_cycle/00_modules/support_data/areacello_Ofx_MIROC-ES2L_piControl_r1i1p1f2_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacello'].fillna(0).compute()
            #area = area.rename({'y':'lat','x':'lon'})
            #area = area.rename({'latitude':'lat','longitude':'lon'})
            area_ds.close()       
        else:
            raise Exception('Variable not in known domain.')
        return area

    def get_filelist(varia,run,freq_input):
     
        member = MIROCgrabber.get_member()
        exercise = MIROCgrabber.get_exercise(run)
        rootdir = MIROCgrabber.get_rootdir(run)
        freq = MIROCgrabber.get_frequency(freq_input) 
        domain = MIROCgrabber.get_domain(varia,freq_input)
        grid = MIROCgrabber.get_grid(varia,freq_input)

        data_path = f'{rootdir}/{exercise}/MIROC/MIROC-ES2L/{run}/{member}/{domain}{freq}/{varia}/{grid}/v*' 
        pattern = f"/{varia}*_{grid}_*.nc" 
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered

    def get_horizontal_dimensions(varia):
        domain = MIROCgrabber.get_domain(varia)
        if domain in ['AE','AP','LI','LP']:
            dims = ('lat','lon')
        elif domain in ['OB','OP','SI']:
            dims = ('y','x')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    def get_area_fraction(varia):
        if varia in ['nbp','npp']:
            indir = '/work/bm1448/upload/abemnb/CMIP6Plus/TIPMIP/MIROC/MIROC-ES2L/esm-up2p0/r1i1p1f1/APfx/sftlf/gn/v20250808'
            land_area_fraction_ds = xr.open_dataset(f'{indir}/sftlf_APfx_MIROC-ES2L_esm-up2p0_r1i1p1f1_gn.nc')
            area_fraction = land_area_fraction_ds.sftlf/100. 
        else:
            area_fraction = None
        return area_fraction

    def get_data(varia,run,freq_input='monthly',verbose_level=1):
        
        # get the list of files
        files = MIROCgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        da = ds[varia]
        if verbose_level > 0:
            print(da) 
        
        return da
 
