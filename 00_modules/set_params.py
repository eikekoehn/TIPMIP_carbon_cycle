import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cftime


class Models:
    """
    This class contains general information about the models participating in the TIPMIP experiments. 
    I.e., which models there are, what their emission rate is for the rampup, and also, what their color_id, marker_id, and linestyle_id are
    """
    
    def __init__(self, name=None, color_id=None, linestyle_id=None, marker_id=None, institute=None, emission_rate=None, rampup_start_year=None, plotting_name=None, default_member=None):
        self.name = name
        self.color_id = color_id
        self.linestyle_id = linestyle_id
        self.marker_id = marker_id
        self.institute = institute
        self.emission_rate = emission_rate # in PgC/yr
        self.rampup_start_year = rampup_start_year
        self.plotting_name = plotting_name
        self.default_member = default_member

    def display_attributes(self):
        print(f"name: {self.name}")
        print(f"color_id: {self.color_id}")
        print(f"linestyle_id: {self.linestyle_id}")
        print(f"marker_id: {self.marker_id}")
        print(f"institute: {self.institute}")
        print(f"emission_rate (PgC/yr): {self.emission_rate}")
        print(f"rampup_start_year: {self.rampup_start_year}")
        print(f"plotting_name: {self.plotting_name}")
        print(f"default_member: {self.default_member}")
        
    @classmethod
    def get_IPSL(cls):
        return cls(name='IPSL-CM6-ESMCO2', 
                   color_id='C0',
                   linestyle_id='--',
                   marker_id='s',
                   institute='IPSL',
                   emission_rate=9.38824139, # PgC/yr
                   rampup_start_year=1850,
                   plotting_name='IPSL-CM6-ESMCO2',
                   default_member='r1i2p3f1')

    @classmethod
    def get_NorESM(cls):
        return cls(name='NorESM2-LM', 
                        color_id='C1',
                        linestyle_id='-.',
                        marker_id='o',
                        institute='NCC',
                        emission_rate=16.807, # GtC yr-1
                        rampup_start_year=1850,
                        plotting_name='NorESM2-LM',
                        default_member='r1i1p1f1')   

    @classmethod
    def get_GFDL(cls):
        return cls(name='GFDL-ESM2M', 
                        color_id='C2',
                        linestyle_id=':',
                        marker_id='*',
                        institute='UBern',
                        emission_rate=18.491, # GtC yr-1
                        rampup_start_year=1861,
                        plotting_name='GFDL-ESM2M',
                        default_member='r1i1p1f1')      

    @classmethod
    def get_ECEarth(cls):
        return cls(name='EC-Earth3-ESM-1', 
                        color_id='C3',
                        linestyle_id='--',
                        marker_id='+',
                        institute='EC-Earth-Consortium',
                        emission_rate=12.4, # GtC yr-1
                        rampup_start_year=1850,
                        plotting_name='EC-Earth3-ESM-1',
                        default_member='r1i1p1f1')     

    @classmethod
    def get_UKESM(cls):
        return cls(name='UKESM1-2', 
                        color_id='C4',
                        linestyle_id='--',
                        marker_id='v',
                        institute='MOHC',
                        emission_rate=8, # GtC yr-1
                        rampup_start_year=2100,#1850,
                        plotting_name='UKESM1-2',
                        default_member='r1i1p1f1')  

    @classmethod
    def get_CNRM(cls):
        return cls(name='CNRM-ESM2-1', 
                        color_id='C5',
                        linestyle_id='-.',
                        marker_id='^',
                        institute='CNRM',
                        emission_rate=11.378, # GtC yr-1
                        rampup_start_year=1850,
                        plotting_name='CNRM-ESM2-1',
                        default_member='r1i1p2f2')   

    @classmethod
    def get_NASA(cls):
        return cls(name='NASA-GISS-E2-1-G', 
                        color_id='C6',
                        linestyle_id=':',
                        marker_id='x',
                        institute='NASA',
                        emission_rate=11.4, # GtC yr-1
                        rampup_start_year=1850,
                        plotting_name='NASA-GISS-E2-1-G',
                        default_member=None)  
        
        
    @classmethod
    def get_model_list(cls,selector):
        """Creates and returns a list of requested model instances."""
        if selector == 'TipESM':
            model_list = [cls.get_IPSL(), cls.get_NorESM(), cls.get_GFDL(), 
                          cls.get_ECEarth(), cls.get_UKESM(), cls.get_CNRM()]            
        elif selector == 'TIPMIP':
            model_list = [cls.get_NASA()]
        elif selector == 'all':
            model_list = [cls.get_IPSL(), cls.get_NorESM(), cls.get_GFDL(), 
                          cls.get_ECEarth(), cls.get_UKESM(), cls.get_CNRM(), 
                          cls.get_NASA()]
        return model_list        

    @classmethod
    def get_model_dict(cls,selector):
        """Creates and returns a dictionary with requested model instances."""
        model_list = cls.get_model_list(selector)
        model_dict = dict()
        for mod in model_list:
            model_dict[mod.name] = mod
        return model_dict



class Runs:
    """
    This class contains information about the general design of the runs within the TIPMIP experiments. 
    I.e., which runs there are, how they depend on one another, and how the experiment cycles are defined.
    """

    def __init__(self,color_id=None, linestyle_id=None):
        self.color_id = color_id
        self.linestyle_id = linestyle_id

    def get_run_list(selector='tipmip_tier1'):
        if selector == 'tipmip_tier1':
            run_list = ['esm-piControl',
                        'esm-up2p0',
                        'esm-up2p0-gwl2p0',
                        'esm-up2p0-gwl4p0',
                        'esm-up2p0-gwl2p0-50y-dn2p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0']
        elif selector=='cycle_runs':
            run_list = ['esm-up2p0',
                        'esm-up2p0-gwl1p1',
                        'esm-up2p0-gwl1p5',
                        'esm-up2p0-gwl2p0',
                        'esm-up2p0-gwl3p0',
                        'esm-up2p0-gwl4p0',
                        'esm-up2p0-gwl5p0',
                        'esm-up2p0-gwl6p0',
                        'esm-up2p0-gwl1p5-50y-dn2p0',
                        'esm-up2p0-gwl2p0-50y-dn2p0',
                        'esm-up2p0-gwl2p0-200y-dn2p0',
                        'esm-up2p0-gwl2p0-50y-dn1p0',
                        'esm-up2p0-gwl3p0-50y-dn2p0',
                        'esm-up2p0-gwl2p0-50y-dn2p0-gwl0p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0',
                        'esm-up2p0-gwl4p0-200y-dn2p0',
                        'esm-up2p0-gwl4p0-50y-dn1p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0-gwl0p0']
        elif selector == 'all':
            run_list = ['esm-piControl',
                        'esm-hist'
                        'esm-up2p0',
                        'esm-up2p0-gwl1p1',
                        'esm-up2p0-gwl1p5',
                        'esm-up2p0-gwl2p0',
                        'esm-up2p0-gwl3p0',
                        'esm-up2p0-gwl4p0',
                        'esm-up2p0-gwl5p0',
                        'esm-up2p0-gwl6p0',
                        'esm-up2p0-gwl1p5-50y-dn2p0',
                        'esm-up2p0-gwl2p0-50y-dn2p0',
                        'esm-up2p0-gwl2p0-200y-dn2p0',
                        'esm-up2p0-gwl2p0-50y-dn1p0',
                        'esm-up2p0-gwl3p0-50y-dn2p0',
                        'esm-up2p0-gwl2p0-50y-dn2p0-gwl0p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0',
                        'esm-up2p0-gwl4p0-200y-dn2p0',
                        'esm-up2p0-gwl4p0-50y-dn1p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0',
                        'esm-up2p0-gwl4p0-50y-dn2p0-gwl0p0']            
        return run_list


    @classmethod
    def get_run_dict(cls):
        """Creates and returns a dictionary with requested model instances."""
        run_dict = dict()

        # CMIP type runs
        run_dict['esm-piControl']    = cls(color_id='#555555',linestyle_id=':')
        run_dict['esm-hist']         = cls(color_id='C3',     linestyle_id='-')

        # TIPMIP rampup
        run_dict['esm-up2p0']        = cls(color_id='#F28E2B',     linestyle_id='-')

        # TIPMIP stabilizations
        run_dict['esm-up2p0-gwl1p1'] = cls(color_id='C2',     linestyle_id=':')
        run_dict['esm-up2p0-gwl1p5'] = cls(color_id='C2',     linestyle_id=':')
        run_dict['esm-up2p0-gwl2p0'] = cls(color_id='#4C9A47',     linestyle_id=':')
        run_dict['esm-up2p0-gwl3p0'] = cls(color_id='C2',     linestyle_id=':')
        run_dict['esm-up2p0-gwl4p0'] = cls(color_id='#2E7D32',     linestyle_id=':')
        run_dict['esm-up2p0-gwl5p0'] = cls(color_id='C2',     linestyle_id=':')
        run_dict['esm-up2p0-gwl6p0'] = cls(color_id='C2',     linestyle_id=':')

        # TIPMIP rampdowns
        run_dict['esm-up2p0-gwl1p5-50y-dn2p0']  = cls(color_id='C0', linestyle_id='--')
        run_dict['esm-up2p0-gwl2p0-50y-dn2p0']  = cls(color_id='#6BAED6', linestyle_id='--')
        run_dict['esm-up2p0-gwl3p0-50y-dn2p0']  = cls(color_id='C0', linestyle_id='--')
        run_dict['esm-up2p0-gwl4p0-50y-dn2p0']  = cls(color_id='#4F8FC1', linestyle_id='--')
        run_dict['esm-up2p0-gwl2p0-200y-dn2p0'] = cls(color_id='C0', linestyle_id='--')
        run_dict['esm-up2p0-gwl4p0-200y-dn2p0'] = cls(color_id='C0', linestyle_id='--')
        run_dict['esm-up2p0-gwl2p0-50y-dn1p0']  = cls(color_id='c', linestyle_id='--')
        run_dict['esm-up2p0-gwl4p0-50y-dn1p0']  = cls(color_id='c', linestyle_id='--')

        # TIPMIP restabilizations
        run_dict['esm-up2p0-gwl2p0-50y-dn2p0-gwl0p0'] = cls(color_id='C4', linestyle_id=':')
        run_dict['esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0'] = cls(color_id='#E15759', linestyle_id=':')
        run_dict['esm-up2p0-gwl4p0-50y-dn2p0-gwl0p0'] = cls(color_id='C4', linestyle_id=':')
        
        return run_dict

    def get_run_history(run):
        """Function returning a list of simulation names that precede the simulation itself. The list contains the simulation at the end."""
        # get all the previous runs
        # rampup, historical, and pi-Control
        if run in ['esm-up2p0','esm-hist','esm-piControl']:
            history = []
        # stabilizations
        elif run in ['esm-up2p0-gwl1p1','esm-up2p0-gwl1p5','esm-up2p0-gwl2p0','esm-up2p0-gwl3p0',
                     'esm-up2p0-gwl4p0','esm-up2p0-gwl5p0','esm-up2p0-gwl6p0']:
            history = ['esm-up2p0']
        # rampdowns
        elif run == 'esm-up2p0-gwl1p5-50y-dn2p0':
            history = ['esm-up2p0','esm-up2p0-gwl1p5'] 
        elif run in ['esm-up2p0-gwl2p0-50y-dn2p0','esm-up2p0-gwl2p0-200y-dn2p0','esm-up2p0-gwl2p0-50y-dn1p0']:
            history = ['esm-up2p0','esm-up2p0-gwl2p0']
        elif run == 'esm-up2p0-gwl3p0-50y-dn2p0':
            history = ['esm-up2p0','esm-up2p0-gwl3p0']
        elif run in ['esm-up2p0-gwl4p0-50y-dn2p0','esm-up2p0-gwl4p0-200y-dn2p0','esm-up2p0-gwl4p0-50y-dn1p0']:
            history = ['esm-up2p0','esm-up2p0-gwl4p0'] 
        # restabilizations
        elif run in ['esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0','esm-up2p0-gwl4p0-50y-dn2p0-gwl0p0']:
            history = ['esm-up2p0','esm-up2p0-gwl4p0','esm-up2p0-gwl4p0-50y-dn2p0'] 
        elif run == 'esm-up2p0-gwl2p0-50y-dn2p0-gwl0p0':
            history = ['esm-up2p0','esm-up2p0-gwl2p0','esm-up2p0-gwl2p0-50y-dn2p0']
        # add the current run to complete the history
        history = history + [run]
        
        return history

    @classmethod
    def get_standard_cycles(cls):
        """Function returning a list of simulation names that are part of the core experiment 'rampup-stabilization-rampdown' cycles."""
        cycle2K = cls.get_run_history('esm-up2p0-gwl2p0-50y-dn2p0')
        cycle4K = cls.get_run_history('esm-up2p0-gwl4p0-50y-dn2p0')
        cycles = dict()
        cycles['2K'] = cycle2K
        cycles['4K'] = cycle4K
        cycles['2K_4K'] = list(set(cycle2K+cycle4K))
        cycles['2K_4K_piC'] = list(set(cycle2K+cycle4K+['esm-piControl']))

        return cycles

    @classmethod
    def get_runlist_for_cycle(cls,cycle):
        cycles = cls.get_standard_cycles()
        runlist_for_cycle = cycles[cycle]
        return runlist_for_cycle


class ModelRuns:
    """
    This class contains functions to get information about the model specific runs completed within the TIPMIP experiment.
    I.e., which model ran which simulations, when they started and when they ended
    """

    @classmethod
    def get_list_of_all_available_simulations(cls,model):
        if model == 'IPSL-CM6-ESMCO2':
            list_of_simulations = ['esm-hist',
                                   'esm-piControl',
                                   'esm-up2p0',
                                   'esm-up2p0-gwl1p5',
                                   'esm-up2p0-gwl2p0',
                                   'esm-up2p0-gwl3p0',
                                   'esm-up2p0-gwl4p0',
                                   'esm-up2p0-gwl2p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0']

        elif model == 'NorESM2-LM':
            list_of_simulations = ['esm-piControl',
                                   'esm-up2p0',
                                   'esm-up2p0-gwl2p0',
                                   'esm-up2p0-gwl4p0',
                                   'esm-up2p0-gwl2p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0']            

        elif model == 'GFDL-ESM2M':
            list_of_simulations = ['esm-piControl',
                                   'esm-up2p0',
                                   'esm-up2p0-gwl2p0',
                                   'esm-up2p0-gwl4p0',
                                   'esm-up2p0-gwl2p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0',
                                   'esm-up2p0-gwl2p0-50y-dn2p0-gwl0p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0-gwl0p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0'] 

        elif model == 'EC-Earth3-ESM-1':
            list_of_simulations = ['esm-hist',
                                   'esm-piControl',
                                   'esm-up2p0',
                                   'esm-up2p0-gwl1p5',
                                   'esm-up2p0-gwl2p0',
                                   'esm-up2p0-gwl3p0',
                                   'esm-up2p0-gwl4p0',
                                   'esm-up2p0-gwl5p0',
                                   'esm-up2p0-gwl6p0',   
                                   'esm-up2p0-gwl1p5-50y-dn2p0',
                                   'esm-up2p0-gwl2p0-50y-dn2p0',
                                   'esm-up2p0-gwl2p0-200y-dn2p0',
                                   'esm-up2p0-gwl3p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-200y-dn2p0',
                                   'esm-up2p0-gwl2p0-50y-dn1p0',
                                   'esm-up2p0-gwl4p0-50y-dn1p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0-gwl2p0']     

        elif model == 'UKESM1-2':
            list_of_simulations = ['esm-hist',
                                   'esm-piControl',
                                   'esm-up2p0',
                                   'esm-up2p0-gwl2p0',
                                   'esm-up2p0-gwl3p0',
                                   'esm-up2p0-gwl4p0',  
                                   'esm-up2p0-gwl2p0-50y-dn2p0',
                                   'esm-up2p0-gwl3p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0',
                                   'esm-up2p0-gwl2p0-50y-dn1p0',
                                   'esm-up2p0-gwl4p0-50y-dn1p0']       

        elif model == 'CNRM-ESM2-1':
            list_of_simulations = ['esm-hist',
                                   'esm-piControl',
                                   'esm-up2p0',
                                   'esm-up2p0-gwl1p1',
                                   'esm-up2p0-gwl1p5',
                                   'esm-up2p0-gwl2p0',
                                   'esm-up2p0-gwl4p0',  
                                   'esm-up2p0-gwl5p0']    

        elif model == 'NASA-GISS-E2-1-G':
            list_of_simulations = ['esm-piControl',
                                   'esm-up2p0',
                                   'esm-up2p0-gwl2p0',
                                   'esm-up2p0-gwl4p0',  
                                   'esm-up2p0-gwl2p0-50y-dn2p0',
                                   'esm-up2p0-gwl4p0-50y-dn2p0']              

        return list_of_simulations

    
    def get_model_run_years(model,run):
        """A function to return the start and end years of a given model run."""
        # get the annual mean tas time series file
        dummy_var = 'tas'
        ts_key = 'annual_mean'
        root_dir = '/home/ekoehn/jobs/jupyter/TipESM/carbon_cycle_reversibility/global_time_series'
        if model == 'UKESM1-2':
            root_dir = root_dir + '_UKESM'
        elif model == 'EC-Earth3-ESM-1':
            root_dir = root_dir + '_CINECA'
        filedir = f'{root_dir}/{run}/{ts_key}/{dummy_var}/'
        filename = f'tas_{model}_{run}_{ts_key}.nc'
        try:
            # open the ts file
            with xr.open_dataset(filedir+filename,use_cftime=True) as ts:
                # get the time vector
                time = ts.time
                #print(time)
                # get years
                years = time.dt.year.values
                #print(years)
                # get the first year
                start_year = years[0]
                end_year = years[-1]
        except:
            start_year = None
            end_year = None
        return start_year,end_year

    @classmethod
    def get_list_of_available_modelruns_in_cycle(cls,model,cycle):
        runlist_for_cycle = Runs.get_runlist_for_cycle(cycle)
        list_of_all_available_runs_for_model = cls.get_list_of_all_available_simulations(model)
        list_of_available_runs = [avail_run for avail_run in list_of_all_available_runs_for_model if avail_run in runlist_for_cycle] 
        return list_of_available_runs

    @classmethod
    def get_model_run_start_and_end_years_for_cycle(cls,model,cycle):
        """A function to return the start and 'end' years of a given model run within the defined experiment cycle (i.e., cutting away the unneccessary bits)."""
        #runlist_for_cycle = Runs.get_runlist_for_cycle(cycle)
        #list_of_all_available_runs_for_model = cls.get_list_of_all_available_simulations(model)
        #available_runs_for_cycle = cls.get_list_of_available_runs(runlist_for_cycle,list_of_all_available_runs_for_model)
        list_of_available_modelruns_in_cycle = cls.get_list_of_available_modelruns_in_cycle(model,cycle)
        
        ys_dict = dict()
        ye_dict = dict()
        pr_dict = dict()
        
        all_previous_run_names = []
        for run in list_of_available_modelruns_in_cycle:
            # get the run years
            ys,ye = cls.get_model_run_years(model,run)
            ys_dict[run],ye_dict[run] = ys,ye
            
            # get the previous run name (pr name)
            if len(Runs.get_run_history(run))>1:
                previous_run_name = Runs.get_run_history(run)[-2]
            else:
                previous_run_name = '-'
            pr_dict[run] = previous_run_name
            all_previous_run_names.append(previous_run_name)    
        
        # get the largest start year for the runs with the same previous_run_name
        previous_run_end_years = dict()
        for run in list_of_available_modelruns_in_cycle:
            # update the end year of the previous run to "start_year-1" of the run at hand
            pr_name = pr_dict[run]
            # now get the value of the years
            if pr_name == '-':   # do not do anything
                continue
            elif pr_name not in previous_run_end_years.keys():  # if the key does not exist, create the key, and put a list in it
                previous_run_end_years[pr_name] = [ys_dict[run] - 1]
            else:    
                previous_run_end_years[pr_name].append(ys_dict[run] - 1)    # if the key exisis, append to the existing list

        # now that the previous_run_end_years dictionary has been created, we get the maximum values and put it into the ye_dict
        for key in previous_run_end_years.keys():
            ye_dict[key] = int(np.max(previous_run_end_years[key]))

        return ys_dict,ye_dict


class Masks:

    def define_ocean_mask_1x1(source='RECCAP2'):
        if source == 'RECCAP2':
            import xarray as xr
            ds = xr.open_dataset("support_data/RECCAP2_region_masks_all_v20221025.nc")
            ds = ds.assign_coords(
                lon=((ds.lon + 180) % 360) - 180
            ).sortby("lon")
            da_mask = xr.where(ds.seamask==1.,1.,np.NaN)
        else:
            raise Exception('not yet implemented')
        da_mask = da_mask.rename('mask')
        return da_mask

    def define_land_mask_1x1(source='RECCAP2'):
        if source == 'RECCAP2':
            import xarray as xr
            ds = xr.open_dataset("support_data/RECCAP2_region_masks_all_v20221025.nc")
            ds = ds.assign_coords(
                lon=((ds.lon + 180) % 360) - 180
            ).sortby("lon")
            da_mask = xr.where(ds.seamask==0.,1.,np.NaN)
        else:
            raise Exception('not yet implemented')
        da_mask = da_mask.rename('mask')
        return da_mask

    def define_air_mask_1x1(source='RECCAP2'):
        if source == 'RECCAP2':
            import xarray as xr
            ds = xr.open_dataset("support_data/RECCAP2_region_masks_all_v20221025.nc")
            ds = ds.assign_coords(
                lon=((ds.lon + 180) % 360) - 180
            ).sortby("lon")
            da_mask = xr.where(ds.seamask==1.,1.,1.)
        else:
            raise Exception('not yet implemented')
        da_mask = da_mask.rename('mask')
        return da_mask



