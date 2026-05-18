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
        return member

    def get_exercise(run):
        if run in ['esm-hist','esm-piControl']:
            exercise = 'CMIP'
        else:
            exercise = 'TIPMIP'
        return exercise

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
        freq_num = 'h*'
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
            area = area_ds['TAREA'].compute() / 100 / 100 # convert from cm2 to m2
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
            area = CESMgrabber.cesm_atm_area_from_ds(area_ds, VAR='TREFHT') # m2
            #area = area_ds['gw'].compute() # latitude weights 
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

    
    def cesm_atm_area_from_ds(area_ds, VAR, radius=6371000):
        """
        Construct 2D atmospheric grid-cell area from a CESM dataset
        containing:
            - gw(lat)
            - VAR(lat, lon)
    
        Parameters
        ----------
        area_ds : xarray.Dataset
            Dataset containing 'gw' and the target variable
        VAR : str
            Variable name used to infer horizontal dimensions
        radius : float
            Earth radius [m]
    
        Returns
        -------
        area : xarray.DataArray
            Grid-cell area [m2] with dimensions (lat, lon)
        """
    
        # Load weights and variable
        gw = area_ds['gw'].compute()
        var = area_ds[VAR].compute()
    
        # Infer dimensions
        lat_dim = gw.dims[0]
    
        # Find longitude dimension
        lon_dim = [d for d in var.dims if d != lat_dim][-1]
    
        nlon = var.sizes[lon_dim]
    
        # Earth surface area
        earth_area = 4.0 * np.pi * radius**2
    
        # CESM gw sums to 2
        lat_fraction = gw / gw.sum()
    
        # Area per latitude band
        lat_band_area = earth_area * lat_fraction
    
        # Convert to per-gridcell area
        area_1d = lat_band_area / nlon
    
        # Broadcast to 2D
        area_2d = xr.DataArray(
            np.repeat(area_1d.values[:, None], nlon, axis=1),
            dims=(lat_dim, lon_dim),
            coords={
                lat_dim: var[lat_dim],
                lon_dim: var[lon_dim]
            },
            name='area'
        )
    
        area_2d.attrs['units'] = 'm2'
        area_2d.attrs['long_name'] = 'atmospheric grid cell area'
    
        return area_2d



    def get_filelist(varia,run,freq_input):
     
        member = CESMgrabber.get_member()
        exercise = CESMgrabber.get_exercise(run)
        rootdir = CESMgrabber.get_rootdir(run)
        freq, freq_num = CESMgrabber.get_frequency(freq_input) 
        domain = CESMgrabber.get_domain(varia,freq_input)
        grid = CESMgrabber.get_grid(varia,freq_input)

        data_path = f'{rootdir}/b.e21.B1850.f09_g17.{run}.{member}/{domain}/proc/tseries/{freq}_1/' 
        pattern = f"/b.e21.B1850.f09_g17.{run}.{member}.{grid}.{freq_num}.{varia}.*.nc" 
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
            area_fraction = xr.where(np.isnan(area_fraction),0,area_fraction)
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


    def varia_mapper_cmor_to_model(CMOR_var_name):
        
        varname_mapper = dict()
        # lnd
        varname_mapper['nbp']= 'NBP'
        varname_mapper['ra']=  'AR'
        varname_mapper['rh']=  'HR'
        varname_mapper['gpp']= 'GPP'
        varname_mapper['npp']= 'NPP'
        varname_mapper['landCoverFrac'] = 'PCT_LANDUNIT'
        varname_mapper['lai'] = 'TLAI'
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
        varname_mapper['epc100']= 'POC_FLUX_100m'
        varname_mapper['so']= 'SALT'
        varname_mapper['sio3']= 'SiO3'
        varname_mapper['zos']= 'SSH'
        varname_mapper['thetao']= 'TEMP'
        varname_mapper['tos']= 'TEMP'
        # atm
        varname_mapper['co2']= 'CO2'
        varname_mapper['ps']= 'PS'
        varname_mapper['psl']= 'PSL'
        varname_mapper['tas']='TREFHT'
        try:
            MODEL_var_name = varname_mapper[CMOR_var_name]
        except:
            raise Exception(f'Variable name {CMOR_var_name} not yet mapped to CESM2 model.')

        return MODEL_var_name

    
    def varia_mapper_model_to_cmor(MODEL_var_name):
    
        varname_mapper = dict()
    
        # lnd
        varname_mapper['NBP'] = 'nbp'
        varname_mapper['AR'] = 'ra'
        varname_mapper['HR'] = 'rh'
        varname_mapper['GPP'] = 'gpp'
        varname_mapper['NPP'] = 'npp'
        varname_mapper['PCT_LANDUNIT'] = 'landCoverFrac'
        varname_mapper['TLAI'] = 'lai'
        varname_mapper['TOTSOMC'] = 'cSoil'
        varname_mapper['TOTVEGC'] = 'cVeg'
        varname_mapper['TOTECOSYSC'] = 'cLand'
        varname_mapper['TSOI'] = 'ts'
    
        # ocn
        varname_mapper['DIC'] = 'dissic'
        varname_mapper['FG_CO2'] = 'fgco2'
        varname_mapper['HMXL_DR'] = 'mlotst'
        varname_mapper['MOC'] = 'msftyz'
        varname_mapper['NO3'] = 'no3'
        varname_mapper['O2'] = 'o2'
        varname_mapper['POC_FLUX_100m'] = 'epc100'
        varname_mapper['SALT'] = 'so'
        varname_mapper['SiO3'] = 'sio3'
        varname_mapper['SSH'] = 'zos'
        varname_mapper['TEMP'] = 'thetao' # careful, this is overwritten here for now...
        varname_mapper['TEMP'] = 'tos'
        # atm
        varname_mapper['CO2'] = 'co2'
        varname_mapper['PS'] = 'ps'
        varname_mapper['PSL'] = 'psl'
        varname_mapper['TREFHT']='tas'

        try:
            CMOR_var_name = varname_mapper[MODEL_var_name]
        except KeyError:
            raise Exception(
                f'Variable name {MODEL_var_name} not yet mapped to CMOR.'
            )
    
        return CMOR_var_name
