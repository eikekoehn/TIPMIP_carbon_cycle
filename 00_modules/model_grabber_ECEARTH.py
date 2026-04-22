"""
this file is to access model output from the EC-Earth3-ESM-1 model.
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
from operations_time import TimeOperator


class ECEARTHgrabber:

    def get_rootdir(run,server='cineca'):
        if server == 'spirit':
            raise Exception('No data for EC-Earth3-ESM-1 on SPIRIT.') 
        elif server == 'levante':
            rootdir = '/work/bm1448/upload/tipesm/EC-Earth3-ESM-1'
        elif server == 'cineca':
            rootdir = '/g100_store/DRES_OptimESM/ESGF/prepub/smhi/CMIP6Plus' #dmi'
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
        if freq_input == 'daily' and varia in ['clt', 'hur', 'hus8', 'prc', 'rlds', 'rsds', 'ta19', 'tasmax', 'ua8', 'va8', 'wap8', 'hfls', 'hurs', 'huss', 'prsn', 'rlus', 'rsus', 'ta8', 'tasmin', 'uas', 'vas', 'zg19', 'hfss', 'hus19', 'pr', 'psl', 'rlut', 'sfcWind', 'tas', 'ua19', 'va19', 'wap19']:
            domain = 'AP'
        elif freq_input == 'monthly' and varia in ['clivi', 'evspsbl', 'hur', 'prc', 'rlds', 'rsds', 'rsut', 'tasmax', 'ua19', 'zg', 'clt', 'fco2antt', 'hurs', 'prsn', 'rldscs', 'rsdscs', 'rsutcs', 'tasmin', 'uas', 'clwvi', 'fco2nat', 'hus19', 'prw', 'rlus', 'rsdt', 'sfcWind', 'tauu', 'va19', 'co2mass', 'hfls', 'huss', 'ps', 'rlut', 'rsus', 'ta', 'tauv', 'vas', 'co2s', 'hfss', 'pr', 'psl', 'rlutcs', 'rsuscs', 'tas', 'ts', 'wap']:
            domain = 'AP'
        elif freq_input == 'daily' and varia in ['albsn', 'lai', 'mrro', 'mrso', 'mrsol', 'mrsos']:
            domain = 'LP'
        elif freq_input == 'monthly' and varia in ['baresoilFrac', 'fLitterSoil', 'lai', 'nVeg', 'burntFractionAll', 'fLuc', 'laiLut', 'nwdFracLut', 'cLand', 'fLulccAtmLut', 'landCoverFrac', 'pastureFrac', 'cLeaf', 'fN2O', 'mrfso', 'pastureFracC3', 'cLitter', 'fNAnthDisturb', 'mrro', 'pastureFracC4', 'cLitterCwd', 'fNdep', 'mrros', 'ra', 'cLitterSubSurf', 'fNfert', 'mrso', 'raGrass', 'cLitterSurf', 'fNgas', 'mrsol', 'raLeaf', 'cOther', 'fNgasFire', 'mrsos', 'raLut', 'cProduct', 'fNgasNonFire', 'nbp', 'raOther', 'cRoot', 'fNLandToOcean', 'necbLut', 'raRoot', 'cropFrac', 'fNleach', 'nep', 'raStem', 'cropFracC3', 'fNLitterSoil', 'netAtmosLandCO2Flux', 'raTree', 'cropFracC4', 'fNloss', 'nLand', 'residualFrac', 'cSoil', 'fNnetmin', 'nLeaf', 'rGrowth', 'cSoilFast', 'fNOx', 'nLitter', 'rh', 'cSoilMedium', 'fNProduct', 'nLitterCwd', 'rhLitter', 'cSoilSlow', 'fNup', 'nLitterSubSurf', 'rhLut', 'cStem', 'fNVegLitter', 'nLitterSurf', 'rhSoil', 'cTotFireLut', 'fProductDecomp', 'nMineral', 'rMaint', 'cVeg', 'fProductDecompLut', 'nMineralNH4', 'shrubFrac', 'fAnthDisturb', 'fracLut', 'nMineralNO3', 'treeFrac', 'fBNF', 'fVegFire', 'nOther', 'treeFracBdlDcd', 'fCLandToOcean', 'fVegLitter', 'npp', 'treeFracBdlEvg', 'fDeforestToAtmos', 'gpp', 'nppGrass', 'treeFracNdlDcd', 'fDeforestToProduct', 'gppGrass', 'nppLut', 'treeFracNdlEvg', 'fFire', 'gppLut', 'nppTree', 'vegFrac', 'fFireAll', 'gppTree', 'nProduct', 'vegHeightTree', 'fFireNat', 'grassFrac', 'nRoot', 'fHarvestToAtmos', 'grassFracC3', 'nSoil', 'fLitterFire', 'grassFracC4', 'nStem']:
            domain = 'LP'
        elif freq_input == 'yearly' and varia in ['cLitter', 'cProduct', 'cSoil', 'cVeg', 'fracLut', 'cLitterLut', 'cProductLut', 'cSoilLut', 'cVegLut']:
            domain = 'LP'
        elif freq_input == 'monthly' and varia in ['dfe', 'dissic', 'expc', 'expfe', 'no3', 'o2', 'ph', 'po4', 'si', 'talk']:
            domain = 'OB'
        elif freq_input == 'fx' and varia in ['areacello', 'basin', 'deptho', 'hfgeou', 'sftof']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['masscello', 'msftyz', 'obvfsq', 'so', 'thetao', 'thkcello', 'umo', 'uo', 'vmo', 'vo', 'wmo', 'wo']:
            domain = 'OP'
        elif freq_input == 'daily' and varia in ['siconc', 'siconca', 'sisnthick', 'sispeed', 'sitemptop', 'sithick', 'sitimefrac', 'siu', 'siv']:
            domain = 'SI'
        elif freq_input == 'monthly' and varia in ['sidivvel', 'sishevel', 'sistremax', 'sistresave']:
            domain = 'SI'
        elif freq_input == 'fx' and varia in ['areacella', 'sftlf']:
            domain = 'AP'
        elif freq_input == 'monthly' and varia in ['snc', 'snd', 'snw']:
            domain = 'LI'
        elif freq_input == 'fx' and varia in ['orog']:
            domain = 'LP'
        elif freq_input == 'yearly' and varia in ['baresoilFrac', 'fracInLut', 'grassFrac', 'shrubFrac', 'vegFrac', 'cropFrac', 'fracOutLut', 'residualFrac', 'treeFrac']:
            domain = 'LP'
        elif freq_input == 'monthly' and varia in ['chldiatos', 'dpco2', 'epsi100', 'intdic', 'intpp', 'limfemisc', 'limnmisc', 'po4os', 'chlmiscos', 'dpo2', 'fgco2', 'intpbfe', 'intppdiat', 'limirrdiat', 'no3os', 'sios', 'chlos', 'epc100', 'fgo2', 'intpbsi', 'intppmisc', 'limirrmisc', 'o2min', 'spco2', 'dfeos', 'epcalc100', 'fric', 'intpoc', 'limfediat', 'limndiat', 'o2os', 'zo2min']:
            domain = 'OB'
        elif freq_input == 'daily' and varia in ['tos','tossq']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['friver', 'hfy', 'mlotstmax', 'sob', 'sosga', 'tauvo', 'tob', 'volo', 'zos', 'hfds', 'masso', 'mlotstmin', 'soga', 't20d', 'thetaoga', 'tos', 'wfo', 'zostoga', 'hfx', 'mlotst', 'pbo', 'sos', 'tauuo', 'thetaot', 'tosga', 'wfonocorr']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['hfbasin', 'hfbasinpmadv', 'htovgyre', 'htovovrt', 'sltovgyre', 'sltovovrt']:
            domain = 'OP'
        elif freq_input == 'monthly' and varia in ['sfdsi', 'sidmassmeltbot', 'siflsensupbot', 'sisali', 'sithick', 'siage', 'sidmassmelttop', 'siflswdtop', 'sisaltmass', 'sitimefrac', 'siarean', 'sidmasssi', 'siforcecoriolx', 'sisnhc', 'siu', 'siareas', 'sidmassth', 'siforcecorioly', 'sisnmass', 'siv', 'sicompstren', 'sidmasstranx', 'siforceintstrx', 'sisnthick', 'sivol', 'siconc', 'sidmasstrany', 'siforceintstry', 'sispeed', 'sivoln', 'siconca', 'siextentn', 'siforcetiltx', 'sistrxdtop', 'sivols', 'sidconcdyn', 'siextents', 'siforcetilty', 'sistrxubot', 'sndmassdyn', 'sidconcth', 'sifb', 'sihc', 'sistrydtop', 'sndmassmelt', 'sidmassdyn', 'siflcondbot', 'siitdconc', 'sistryubot', 'sndmasssi', 'sidmassevapsubl', 'siflcondtop', 'siitdsnthick', 'sitempbot', 'sndmasssnf', 'sidmassgrowthbot', 'siflfwbot', 'siitdthick', 'sitempsnic', 'sndmasssubl', 'sidmassgrowthwat', 'siflfwdrain', 'simass', 'sitemptop']:
            domain = 'SI'
        else:
            raise Exception(f'No domain is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain  

    def get_domain_suffix(varia,freq_input):
        if freq_input == 'daily' and varia in ['clt', 'hur', 'hus8', 'prc', 'rlds', 'rsds', 'ta19', 'tasmax', 'ua8', 'va8', 'wap8', 'hfls', 'hurs', 'huss', 'prsn', 'rlus', 'rsus', 'ta8', 'tasmin', 'uas', 'vas', 'zg19', 'hfss', 'hus19', 'pr', 'psl', 'rlut', 'sfcWind', 'tas', 'ua19', 'va19', 'wap19']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['clivi', 'evspsbl', 'hur', 'prc', 'rlds', 'rsds', 'rsut', 'tasmax', 'ua19', 'zg', 'clt', 'fco2antt', 'hurs', 'prsn', 'rldscs', 'rsdscs', 'rsutcs', 'tasmin', 'uas', 'clwvi', 'fco2nat', 'hus19', 'prw', 'rlus', 'rsdt', 'sfcWind', 'tauu', 'va19', 'co2mass', 'hfls', 'huss', 'ps', 'rlut', 'rsus', 'ta', 'tauv', 'vas', 'co2s', 'hfss', 'pr', 'psl', 'rlutcs', 'rsuscs', 'tas', 'ts', 'wap']:
            domain_suffix = ''
        elif freq_input == 'daily' and varia in ['albsn', 'lai', 'mrro', 'mrso', 'mrsol', 'mrsos']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['baresoilFrac', 'fLitterSoil', 'lai', 'nVeg', 'burntFractionAll', 'fLuc', 'laiLut', 'nwdFracLut', 'cLand', 'fLulccAtmLut', 'landCoverFrac', 'pastureFrac', 'cLeaf', 'fN2O', 'mrfso', 'pastureFracC3', 'cLitter', 'fNAnthDisturb', 'mrro', 'pastureFracC4', 'cLitterCwd', 'fNdep', 'mrros', 'ra', 'cLitterSubSurf', 'fNfert', 'mrso', 'raGrass', 'cLitterSurf', 'fNgas', 'mrsol', 'raLeaf', 'cOther', 'fNgasFire', 'mrsos', 'raLut', 'cProduct', 'fNgasNonFire', 'nbp', 'raOther', 'cRoot', 'fNLandToOcean', 'necbLut', 'raRoot', 'cropFrac', 'fNleach', 'nep', 'raStem', 'cropFracC3', 'fNLitterSoil', 'netAtmosLandCO2Flux', 'raTree', 'cropFracC4', 'fNloss', 'nLand', 'residualFrac', 'cSoil', 'fNnetmin', 'nLeaf', 'rGrowth', 'cSoilFast', 'fNOx', 'nLitter', 'rh', 'cSoilMedium', 'fNProduct', 'nLitterCwd', 'rhLitter', 'cSoilSlow', 'fNup', 'nLitterSubSurf', 'rhLut', 'cStem', 'fNVegLitter', 'nLitterSurf', 'rhSoil', 'cTotFireLut', 'fProductDecomp', 'nMineral', 'rMaint', 'cVeg', 'fProductDecompLut', 'nMineralNH4', 'shrubFrac', 'fAnthDisturb', 'fracLut', 'nMineralNO3', 'treeFrac', 'fBNF', 'fVegFire', 'nOther', 'treeFracBdlDcd', 'fCLandToOcean', 'fVegLitter', 'npp', 'treeFracBdlEvg', 'fDeforestToAtmos', 'gpp', 'nppGrass', 'treeFracNdlDcd', 'fDeforestToProduct', 'gppGrass', 'nppLut', 'treeFracNdlEvg', 'fFire', 'gppLut', 'nppTree', 'vegFrac', 'fFireAll', 'gppTree', 'nProduct', 'vegHeightTree', 'fFireNat', 'grassFrac', 'nRoot', 'fHarvestToAtmos', 'grassFracC3', 'nSoil', 'fLitterFire', 'grassFracC4', 'nStem']:
            domain_suffix = ''
        elif freq_input == 'yearly' and varia in ['cLitter', 'cProduct', 'cSoil', 'cVeg', 'fracLut', 'cLitterLut', 'cProductLut', 'cSoilLut', 'cVegLut']:
            domain_suffix = 'Pt'
        elif freq_input == 'monthly' and varia in ['dfe', 'dissic', 'expc', 'expfe', 'no3', 'o2', 'ph', 'po4', 'si', 'talk']:
            domain_suffix = 'Lev'
        elif freq_input == 'fx' and varia in ['areacello', 'basin', 'deptho', 'hfgeou', 'sftof']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['masscello', 'msftyz', 'obvfsq', 'so', 'thetao', 'thkcello', 'umo', 'uo', 'vmo', 'vo', 'wmo', 'wo']:
            domain_suffix = 'Lev'
        elif freq_input == 'daily' and varia in ['siconc', 'siconca', 'sisnthick', 'sispeed', 'sitemptop', 'sithick', 'sitimefrac', 'siu', 'siv']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['sidivvel', 'sishevel', 'sistremax', 'sistresave']:
            domain_suffix = 'Pt'
        elif freq_input == 'fx' and varia in ['areacella', 'sftlf']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['snc', 'snd', 'snw']:
            domain_suffix = ''
        elif freq_input == 'fx' and varia in ['orog']:
            domain_suffix = ''
        elif freq_input == 'yearly' and varia in ['baresoilFrac', 'fracInLut', 'grassFrac', 'shrubFrac', 'vegFrac', 'cropFrac', 'fracOutLut', 'residualFrac', 'treeFrac']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['chldiatos', 'dpco2', 'epsi100', 'intdic', 'intpp', 'limfemisc', 'limnmisc', 'po4os', 'chlmiscos', 'dpo2', 'fgco2', 'intpbfe', 'intppdiat', 'limirrdiat', 'no3os', 'sios', 'chlos', 'epc100', 'fgo2', 'intpbsi', 'intppmisc', 'limirrmisc', 'o2min', 'spco2', 'dfeos', 'epcalc100', 'fric', 'intpoc', 'limfediat', 'limndiat', 'o2os', 'zo2min']:
            domain_suffix = ''
        elif freq_input == 'daily' and varia in ['tos','tossq']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['friver', 'hfy', 'mlotstmax', 'sob', 'sosga', 'tauvo', 'tob', 'volo', 'zos', 'hfds', 'masso', 'mlotstmin', 'soga', 't20d', 'thetaoga', 'tos', 'wfo', 'zostoga', 'hfx', 'mlotst', 'pbo', 'sos', 'tauuo', 'thetaot', 'tosga', 'wfonocorr']:
            domain_suffix = ''
        elif freq_input == 'monthly' and varia in ['hfbasin', 'hfbasinpmadv', 'htovgyre', 'htovovrt', 'sltovgyre', 'sltovovrt']:
            domain_suffix = 'Z'
        elif freq_input == 'monthly' and varia in ['sfdsi', 'sidmassmeltbot', 'siflsensupbot', 'sisali', 'sithick', 'siage', 'sidmassmelttop', 'siflswdtop', 'sisaltmass', 'sitimefrac', 'siarean', 'sidmasssi', 'siforcecoriolx', 'sisnhc', 'siu', 'siareas', 'sidmassth', 'siforcecorioly', 'sisnmass', 'siv', 'sicompstren', 'sidmasstranx', 'siforceintstrx', 'sisnthick', 'sivol', 'siconc', 'sidmasstrany', 'siforceintstry', 'sispeed', 'sivoln', 'siconca', 'siextentn', 'siforcetiltx', 'sistrxdtop', 'sivols', 'sidconcdyn', 'siextents', 'siforcetilty', 'sistrxubot', 'sndmassdyn', 'sidconcth', 'sifb', 'sihc', 'sistrydtop', 'sndmassmelt', 'sidmassdyn', 'siflcondbot', 'siitdconc', 'sistryubot', 'sndmasssi', 'sidmassevapsubl', 'siflcondtop', 'siitdsnthick', 'sitempbot', 'sndmasssnf', 'sidmassgrowthbot', 'siflfwbot', 'siitdthick', 'sitempsnic', 'sndmasssubl', 'sidmassgrowthwat', 'siflfwdrain', 'simass', 'sitemptop']:
            domain_suffix = ''
        else:
            raise Exception(f'No domain is known for the variable {varia}. At least not for the {freq_input} frequency.')
        return domain_suffix          

    def get_frequency(freq_input='monthly'):
        if freq_input == 'monthly':
            frequency = 'mon'
        elif freq_input == 'yearly':
            frequency = 'yr'
        return frequency

    def get_grid(varia,freq_input): 
        domain = ECEARTHgrabber.get_domain(varia,freq_input)
        freq = ECEARTHgrabber.get_frequency(freq_input)
        if f'{domain}{freq}' == 'APday':
            grid = 'gr'
        elif f'{domain}{freq}' == 'APfx':
            grid = 'gr'
        elif f'{domain}{freq}' == 'APmon' and varia not in ['co2mass','co2s']:
            grid = 'gr'
        elif f'{domain}{freq}' == 'APmon' and varia in ['co2mass','co2s']:
            grid = 'gm'
        elif f'{domain}{freq}' == 'LImon':
            grid = 'gr'      
        elif f'{domain}{freq}' == 'LPday':
            grid = 'gr'     
        elif f'{domain}{freq}' == 'LPfx':
            grid = 'gr'    
        elif f'{domain}{freq}' == 'LPmon':
            grid = 'gr'     
        elif f'{domain}{freq}' == 'LPyr':
            grid = 'gr'
        elif f'{domain}{freq}' == 'OBmon':
            grid = 'gn'
        elif f'{domain}{freq}' == 'OPday':
            grid = 'gn'
        elif f'{domain}{freq}' == 'OPfx':
            grid = 'gn'
        elif f'{domain}{freq}' == 'OPmon':
            grid = 'gn'
        elif f'{domain}{freq}' == 'SIday' and varia in ['siconca']:
            grid = 'gr'
        elif f'{domain}{freq}' == 'SIday' and varia not in ['siconca']:
            grid = 'gn'        
        elif f'{domain}{freq}' == 'SImon' and varia in ['siconca']:
            grid = 'gr'
        elif f'{domain}{freq}' == 'SImon' and varia not in ['siconca']:
            grid = 'gn' 
        else:
            raise Exception('Variable not in known domain.')
        return grid

    def get_area(varia,freq_input):
        domain = ECEARTHgrabber.get_domain(varia,freq_input)
        if domain in ['AP','LI','LP']:
            area_file = f'/g100_store/DRES_OptimESM/ESGF/prepub/dmi/20250514/CMIP6Plus/TIPMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-up2p0/r1i1p1f1/APfx/areacella/gr/v20250429/areacella_APfx_EC-Earth3-ESM-1_esm-up2p0_r1i1p1f1_gr.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacella'].compute()
            area_ds.close()
        elif domain in ['SI','OB','OP']:
            area_file = f'/g100_store/DRES_OptimESM/ESGF/prepub/dmi/20250514/CMIP6Plus/TIPMIP/EC-Earth-Consortium/EC-Earth3-ESM-1/esm-up2p0/r1i1p1f1/OPfx/areacello/gn/v20250429/areacello_OPfx_EC-Earth3-ESM-1_esm-up2p0_r1i1p1f1_gn.nc'
            area_ds = xr.open_dataset(area_file)
            area = area_ds['areacello'].fillna(0).compute()
            #area = area.rename({'y':'j','x':'i'})
            #area = area.rename({'nav_lat':'latitude','nav_lon':'longitude'})
            area_ds.close()       
        else:
            raise Exception('Variable not in known domain.')
        return area

    def get_filelist(varia,run,freq_input):
     
        member = ECEARTHgrabber.get_member()
        exercise = ECEARTHgrabber.get_exercise(run)
        rootdir = ECEARTHgrabber.get_rootdir(run)
        freq = ECEARTHgrabber.get_frequency(freq_input) 
        domain = ECEARTHgrabber.get_domain(varia,freq_input)
        domain_suffix = ECEARTHgrabber.get_domain_suffix(varia,freq_input)

        grid = ECEARTHgrabber.get_grid(varia,freq_input)

        data_path = f'{rootdir}/{exercise}/EC-Earth-Consortium/EC-Earth3-ESM-1/{run}/{member}/{domain}{freq}{domain_suffix}/{varia}/{grid}/v*' 
        pattern = f"/{varia}*_{grid}_*.nc" 
        #print(data_path+pattern)
        file_list = sorted(glob.glob(data_path+pattern,recursive=True))
        file_list_filtered = MISCgrabber.filter_longest_period_files(file_list)
        
        return file_list_filtered

    def get_horizontal_dimensions(varia):
        domain = ECEARTHgrabber.get_domain(varia)
        if domain in ['OB','OP','SI']:
            dims = ('j','i')
        elif domain in ['AP','LI','LP']:
            dims = ('lat','lon')
        else:
            raise Exception('Variable not in known domain.')
        return dims

    #def get_thickness(varia,run,ds):
    #    print('We have 4D dataset "ds". We need to get the vertical thickness of the grid cells.')
    #    thickness_list = ECEARTHgrabber.get_filelist('thkcello',run)
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

    def verify_coords(da,varia,freq_input,verbosity=0):

        # get the area file
        area = ECEARTHgrabber.get_area(varia,freq_input)

        # now get the area and check how many coordinates are the same
        dlat = da['lat']
        dlon = da['lon']
        alat = area['lat']
        alon = area['lon']

        if verbosity==1:
            print('Lons: ',np.size(alon),' (area) vs. ',np.size(dlon),' (da)')
            print('Lats: ',np.size(alat),' (area) vs. ',np.size(dlat),' (da)')

        # check (and adjust) the longitudes
        if np.size(alon) == np.size(dlon):
            sumdiff = np.sum(np.abs(alon.values-dlon.values))
            #print(sumdiff)
            if sumdiff > 1e-8:
                raise Exception('lons are not equal.')
        elif np.size(alon) < np.size(dlon):
            print('There are more lons in da than in area. Subsample the da.')
            da = da.sel(lon=alon)
        else:
            raise Exception('lons are not equal.')

        # check (and adjust) the latitudes
        if np.size(alat) == np.size(dlat):
            sumdiff = np.sum(np.abs(alat.values-dlat.values))
            #print(sumdiff)
            if sumdiff > 1e-8:
                raise Exception('lats are not equal.')
        elif np.size(alat) < np.size(dlat):
            print('There are more lats in da than in area. Subsample the da.')
            da = da.sel(lat=alat)
        else:
            raise Exception('lats are not equal.')
            
        # now recalculate dlat and dlon
        dlat = da['lat']
        dlon = da['lon']

        if verbosity==1:
            print('Updated:')
            print('Lons: ',np.size(alon),' (area) vs. ',np.size(dlon),' (da)')
            print('Lats: ',np.size(alat),' (area) vs. ',np.size(dlat),' (da)')

        # final longitude check
        if np.size(alon) == np.size(dlon):
            sumdiff = np.sum(np.abs(alon.values-dlon.values))
            if sumdiff > 1e-8:
                raise Exception('lons are not equal.')
        else:
            raise Exception('lons are not equal.')

        # final latitude check
        if np.size(alat) == np.size(dlat):
            sumdiff = np.sum(np.abs(alat.values-dlat.values))
            if sumdiff > 1e-8:
                raise Exception('lats are not equal.')
        else:
            raise Exception('lats are not equal.')

        return da
        
    
    def get_data(varia,run,freq_input='monthly',verbose_level=1):
        
        # get the list of files
        files = ECEARTHgrabber.get_filelist(varia,run,freq_input)
        if verbose_level > 0:
            print(files)

        # open the dataset and choose data array
        ds = DataFuncs.open_dataset(files)
        da = ds[varia]
        if verbose_level > 0:
            print(da) 

        # if run is esm-piControl, shift the time by n years
        #if run == 'esm-piControl':
        #    da = TimeOperator.shift_time_axis_by_n_years(da,n=-250)

        # verify lon and lats
        domain = ECEARTHgrabber.get_domain(varia,freq_input)
        if domain in ['AP','LP','LI']:
            da = ECEARTHgrabber.verify_coords(da,varia,freq_input,verbosity=verbose_level)

        return da
 
