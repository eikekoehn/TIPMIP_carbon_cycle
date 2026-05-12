"""
this file is to access model output from the CESM2 model.
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


class CESMgrabber:

    def get_rootdir(run,server='levante'):
        if server == 'spirit':
            raise Exception('No data for CESM2 on spirit.') 
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/tipesm/CESM2'
        elif rootdir == 'cineca':
            raise Exception('No data for CESM2 on CINECA.') 
        return rootdir

    def get_member():
        member = '001'
        mversion = 'b.e21.B1850.f09_g17'
        return member, mversion

    #def get_exercise(run):
    #    if run in ['esm-hist','esm-piControl']:
    #        exercise = 'CMIP'
    #    else:
    #        exercise = 'TIPMIP'
    #    return exercise

    def get_domain(varia,freq_input):
        if varia in ['AR','FSNO','GPP','H2OSNO','HR','NBP','NPP','PCT_LANDUNIT','QFLX_SUB_SNOW','QOVER','QRUNOFF','SNOTXMASS','SNOWDP','SNOWICE','SNOWLIQ','SOILICE','SOILLIQ','TLAI','TOPO_COL_ICE','TOTECOSYSC','TOTSOMC','TOTVEGC','TSOI']:
            domain = 'lnd'
        elif varia in ['DIC','EVAP_F','FG_CO2','HMXL_DR','IAGE','IOFF_F','MELT_F','MOC','NO3','O2','POC_FLUX_100m','PREC_F','QFLUX','ROFF_F','SALT','SHF','SiO3','SSH','TEMP','UVEL','VVEL']:
            domain = 'ocn'
        elif varia in ['aice','hi','sisnthick','sithick','siu','siv']:
            domain = 'ice'
        elif varia in ['CLDTOT','CO2','FLUT','FLUTC','FSNTOAC','FSUTOA','LHFLX','PRECT','PS','PSL','QFLX','SHFLX','SOLIN','TAUBLJX','TAUBLJY','TAUGWX','TAUGWY','TAUX','TAUY','TGCLDIWP','TGCLDLWP','TMQ','TREFHT','TREFHTMN','TREFHTMX','U','V','Z3']:
            domain = 'atm'
        else:
            raise Exception(f'No domain is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain  

    def get_frequency(freq_input='monthly'):
        if freq_input == 'daily':
            frequency = 'day'
            freq_num = 'h1'
        elif freq_input == 'monthly':
            frequency = 'month'
            freq_num = 'h0'
        elif freq_input == 'yearly':
            frequency = 'yr'
            freq_num = 'h2'
        return frequency, freq_num

    def get_grid(varia,freq_input): 
        domain = CESMgrabber.get_domain(varia,freq_input)
        if domain in ['ice']:
            grid = 'cice'
        elif domain in ['atm']:
            grid = 'cam'
        elif domain in ['ocn']:
            grid = 'pop'
        elif domain in ['lnd']:
            grid = 'clm2'
        else:
            raise Exception('Variable not in known domain.')
        return grid

    def get_area(varia,freq_input):
        domain = CESMgrabber.get_domain(varia,freq_input)
        if domain in ['ocn']:
            area_file = '/work/bm1448/upload/tipesm/CESM2/b.e21.B1850.f09_g17.esm-up2p0.001/ocn/proc/tseries/month_1/b.e21.B1850.f09_g17.esm-up2p0.001.pop.h.FG_CO2.000101-001012.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['TAREA'].compute() / 100 # convert from cm2 to m2
            area_ds.close()
        elif domain in ['lnd']:
            area_file = '/work/bm1448/upload/tipesm/CESM2/b.e21.B1850.f09_g17.esm-up2p0.001/lnd/proc/tseries/month_1/b.e21.B1850.f09_g17.esm-up2p0.001.clm2.h0.NBP.000101-001012.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['area'].compute() * 10**6 # convert from km2 to m2
            area_ds.close()        
        elif domain in ['ice']:
            area_file = '/work/bm1448/upload/tipesm/CESM2/b.e21.B1850.f09_g17.esm-up2p0.001/ice/proc/tseries/month_1/b.e21.B1850.f09_g17.esm-up2p0.001.cice.h.aice.000101-001012.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['tarea'].compute() # in m2
            area_ds.close()            
        elif domain in ['atm']:
            area_file = '/work/bm1448/upload/tipesm/CESM2/b.e21.B1850.f09_g17.esm-up2p0.001/atm/proc/tseries/month_1/b.e21.B1850.f09_g17.esm-up2p0.001.cam.h0.TREFHT.000101-001012.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['gw'].compute() # latitude weights 
            area_ds.close()     
        #elif domain in ['OB','OP','SI']:
        #    area_file = '/home/ekoehn/jobs/jupyter/TIPMIP_carbon_cycle/00_modules/support_data/areacello_Ofx_MIROC-ES2L_piControl_r1i1p1f2_gn.nc'
        #    area_ds = xr.open_dataset(area_file)
        #    area = area_ds['areacello'].fillna(0).compute()
        #    #area = area.rename({'y':'lat','x':'lon'})
        #    #area = area.rename({'latitude':'lat','longitude':'lon'})
        #    area_ds.close()       
        else:
            raise Exception('Variable not in known domain.')
        return area

    def get_filelist(varia,run,freq_input):
     
        member, mversion = CESMgrabber.get_member()
        exercise = CESMgrabber.get_exercise(run)
        rootdir = CESMgrabber.get_rootdir(run)
        freq, freq_num = CESMgrabber.get_frequency(freq_input) 
        domain = CESMgrabber.get_domain(varia,freq_input)
        grid = CESMgrabber.get_grid(varia,freq_input)

        data_path = f'{rootdir}/{mversion}.{run}.{member}/{domain}/proc/tseries/{freq}_1/' 
        pattern = f"/{mversion}.{run}.{member}.{grid}.{freq_num}.{varia}.*.nc" 
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered

    def get_horizontal_dimensions(varia):
        domain = CESMgrabber.get_domain(varia)
        if domain in ['atm']:
            dims = ('lat','lon')
        elif domain in ['ice']:
            dims = ('nj','ni')
        elif domain in ['oce']:
            dims = ('nlat','nlon')
        elif domain in ['lnd']:
            dims = ('lat','lon')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    def get_area_fraction(varia):
        domain = CESMgrabber.get_domain(varia,'monthly')
        if domain in ['lnd']:
            indir = '/work/bm1448/upload/tipesm/CESM2/b.e21.B1850.f09_g17.esm-up2p0.001/lnd/proc/tseries/month_1'
            land_area_fraction_ds = xr.open_dataset(f'{indir}/b.e21.B1850.f09_g17.esm-up2p0.001.clm2.h0.NBP.000101-001012.nc')
            area_fraction = land_area_fraction_ds.landfrac #/100. 
        else:
            area_fraction = None
        return area_fraction

    def get_data(varia,run,freq_input='monthly',verbose_level=1):
        
        # get the list of files
        files = CESMgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        da = ds[varia]
        if verbose_level > 0:
            print(da) 
        
        return da


    def varia_mapper(CMOR_var_name):
        
        varname_mapper = dict()
        # lnd
        varname_mapper['nbp']= 'NBP'
        varname_mapper['ra']=  'AR'
        varname_mapper['rh']=  'HR'
        varname_mapper['gpp']= 'GPP'
        varname_mapper['npp']= 'NPP'
        varname_mapper['landCoverFrac'] = 'PCT_LANDUNIT'
        varname_mapper['lai'] 'TLAI'
        varname_mapper['cSoil']= 'TOTSOMC'
        varname_mapper['cVeg']= 'TOTVEGC'
        varname_mapper['cLand']= 'TOTECOSYSC'
        varname_mapper['ts']= 'TSOI'
        # ocn
        varname_mapper['dissic']= 'DIC'
        varname_mapper['fgco2']= 'FG_CO2'
        varname_mapper['mlotst']= 'HMXL_DR'
        varname_mapper['msftyz']= 'MOC'
        varname_mapper['no3']= 'NO3'
        varname_mapper['o2']= 'O2'
        varname_mapper['expc100']= 'POC_FLUX_100m'
        varname_mapper['so']= 'SALT'
        varname_mapper['sio3']= 'SiO3'
        varname_mapper['zos']= 'SSH'
        varname_mapper['thetao']= 'TEMP'
        # atm
        varname_mapper['co2']= 'CO2'
        varname_mapper['ps']= 'PS'
        varname_mapper['psl']= 'PSL'

        try:
            CESM_var_name = varname_mapper[CMOR_var_name]
        except:
            raise Exception(f'Variable name {CMOR_var_name} not yet mapped to CESM2 model.')

        return CESM_var_name
 
