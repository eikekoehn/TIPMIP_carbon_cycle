"""
this file is to access model output from the NorESM model.
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


class NorESMgrabber:

    def get_rootdir(run,server='spirit'):
        if server == 'spirit':
            if run == 'esm-piControl':
                rootdir = '/data/ekoehn/TIPMIP/NCC/NorESM2-LM'
            else:
                rootdir = '/projets/TipESM/UiB/NorESM2-LM'
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/tipesm/NorESM2-LM'
        elif rootdir == 'cineca':
            raise Exception('No data for NorESM on CINECA.') 
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

    def get_grid(varia):
        if varia in ['rsus', 'sidmassth', 'wfo', 'sidmasstrany', 'msftbarot', 'zg', 'epsi100', 'chlos', 'bldep', 'dpco2', 'co2', 'sirdgconc', 'sivols', 'no3os', 'oh', 'mfo', 'siitdsnconc', 'rlutcs', 'somint', 'tossq', 'sos', 'ta', 'sidivvel', 'zfullo', 'sidmassevapsubl', 'siflcondbot', 'rlus', 'co2', 'tob', 'sfcWind', 'prc', 'fgdms', 'isop', 'sidmasslat', 'rsdscs', 'prra', 'epn100', 'ccn', 'sistrydtop', 'siage', 'rsuscs', 'sitempsnic', 'rsds', 'so', 'spco2', 'sndmasssi', 'sidconcdyn', 'emibc', 'pbo', 'frn', 'va', 'po4os', 'dmsos', 'sidconcth', 'mmrso4', 'sitempbot', 'siareas', 'sndmassmelt', 'fric', 'emivoc', 'mlotstsq', 'emioa', 'sidmasssi', 'siforceintstry', 'prw', 'wetso2', 'fsitherm', 'siv', 'siitdthick', 'hus', 'siflfwbot', 'simass', 'evs', 'emidms', 'siforcecoriolx', 'emiso2', 'dfeos', 'hfx', 'friver', 'rsdt', 'sios', 'sifllatstop', 'hfds', 'mmrsoa', 'emibvoc', 'prsn', 'ua', 'siarean', 'sicompstren', 'sndmasswindrif', 'hfy', 'mmrss', 'pfull', 'psl', 'siu', 'rtmt', 'emidust', 'sifb', 'rsntds', 'so2', 'mlotst', 'pr', 'ts', 'siflswutop', 'siitdconc', 'zossq', 'fgco2', 't20d', 'sistrxdtop', 'ua', 'ps', 'loaddust', 'rsutcs', 'evspsbl', 'siforceintstrx', 'sithick', 'siflfwdrain', 'lwp', 'masscello', 'hus', 'volcello', 'rldscs', 'sitimefrac', 'siflsenstop', 'cl', 'siextents', 'o2os', 'tauvo', 'va', 'mlotstmin', 'dissicos', 'wfonocorr', 'zg', 'prsn', 'hfls', 'fgo2', 'siflcondtop', 'thkcello', 'hfss', 'epcalc100', 'clt', 'tas', 'sipr', 'rsut', 'mmrdust', 'siflswdtop', 'intpp', 'sivoln', 'hur', 'simpconc', 'cli', 'ta', 'rlds', 'siconc', 'huss', 'sirdgthick', 'sidmassmelttop', 'va', 'epfe100', 'tauuo', 'tauv', 'sispeed', 'opottempmint', 'sifllwdtop', 'hur', 'sisnmass', 'tauu', 'sistrxubot', 'froc', 'siextentn', 'sfdsi', 'sob', 'ua', 'siflsensupbot', 'sisnhc', 'clw', 'ps', 'frfe', 'mmrbc', 'loadss', 'sidmassgrowthbot', 'intpn2', 'rlut', 'emiso4', 'thetaot', 'phalf', 'sisnthick', 'emiisop', 'emiss', 'pso', 'mmroa', 'wap', 'sitemptop', 'agessc', 'hurs', 'sidmassdyn', 'siflswdbot', 'talkos', 'sidmassmeltbot', 'sivol', 'siforcecorioly', 'zos', 'mlotstmax', 'sossq', 'dryso2', 'cdnc', 'ta', 'sidmassgrowthwat', 'dms', 'ficeberg', 'wap', 'rsdsdiff', 'tos', 'hus', 'epc100', 'epp100', 'sihc', 'zhalfo', 'sistryubot', 'thetao', 'sisnconc', 'snowmxrat', 'siforcetiltx', 'ps', 'sifllwutop', 'sidmasstranx', 'zg', 'siforcetilty', 'siitdsnthick', 'clwvi', 'clivi', 'vsf', 'nbp','npp']:
            grid = 'gn'
        elif varia in ['co3', 'so', 'phyc', 'vo', 'zsatcalc', 'o2satos', 'pp', 'calc', 'phynos', 'agessc', 'co3satcalcos', 'bsios', 'co3satcalc', 'obvfsq', 'o2sat', 'phyfeos', 'vmo', 'bfe', 'zoocos', 'talk', 'ponos', 'uo', 'co3os', 'co3satarag', 'pon', 'dissoc', 'wmo', 'thetaot300', 'thetaot2000', 'si', 'no3', 'o2', 'bfeos', 'zsatarag', 'intpoc', 'chl', 'wo', 'dfe', 'umo', 'dissocos', 'phos', 'thetaot700', 'detocos', 'zooc', 'phyfe', 'intdic', 'pop', 'popos', 'ph', 'zo2min', 'dissic', 'detoc', 'thetao', 'intdoc', 'calcos', 'co3sataragos', 'phyn', 'po4', 'ppos', 'bsi', 'o2min']:
            grid = 'gr'
        elif varia in ['co2mass', 'sosga', 'tosga', 'volo', 'masso', 'soga', 'zostoga', 'cfc12global', 'cfc11global', 'thetaoga', 'ch4global', 'n2oglobal']:
            grid = 'gm'
        elif varia in ['msftmz']:
            grid = 'grz'
        return grid

    def get_area(varia,freq_input):
        domain = NorESMgrabber.get_domain(varia,freq_input)
        if domain in ['Si','O']:
            area_file = '/projets/TipESM/UiB/NorESM2-LM/esm-up2p0/v20251010/areacello_Ofx_NorESM2-LM_esm-up2p0_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacello'].fillna(0).compute()
            #area = area.rename({'y':'j','x':'i'})
            area_ds.close()
        elif domain in ['L', 'E', 'A', '', 'CF', 'LI']:
            area_file = '/projets/TipESM/UiB/NorESM2-LM/esm-up2p0/v20251010/areacella_fx_NorESM2-LM_esm-up2p0_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacella'].compute()
            area_ds.close()
        else:
            raise Exception('Variable not in known domain.')
        return area
        
    
    def get_filelist(varia,run,freq_input):
     
        member = NorESMgrabber.get_member()
        exercise = NorESMgrabber.get_exercise(run)
        rootdir = NorESMgrabber.get_rootdir(run)
        freq = NorESMgrabber.get_frequency(freq_input) 
        domain = NorESMgrabber.get_domain(varia,freq_input)
        grid = NorESMgrabber.get_grid(varia)

        if run == 'esm-piControl':
            data_path = f'{rootdir}/{run}/{member}/{domain}{freq}/{varia}/{grid}/v*' 
        else:
            data_path = f'{rootdir}/{run}/v*'
            
        pattern = f"/{varia}_*_{grid}_*.nc" 

        # replace all instances of gwl with swl
        data_path = data_path.replace('gwl','swl')
    
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered


    def get_horizontal_dimensions(vspecs):
        domain = NorESMgrabber.get_domain(varia)
        if domain in ['O','SI']:
            dims = ('latitude','longitude')
        elif domain in ['L', 'E', 'A', '', 'CF', 'LI']:
            dims = ('lat','lon')
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
        files = NorESMgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        da = ds[varia]
        if verbose_level > 0:
            print(da) 
        
        return da
 
