import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cftime

from set_params import Models as pmods

class TimeOperator:

    def _infer_time_resolution(time):
        """
        Infer temporal resolution using calendar fields instead of timedeltas.
        Works reliably with cftime.
        """
    
        if time.size < 2:
            return "unknown"
    
        t = time.values
    
        years  = np.array([tt.year for tt in t])
        months = np.array([tt.month for tt in t])
        days   = np.array([tt.day for tt in t])
    
        # unique counts
        n_years  = len(np.unique(years))
        n_months = len(np.unique(months))
        n_days   = len(np.unique(days))
    
        # total length
        n = len(t)
    
        # --- detect yearly ---
        if n_months == 1 and n_days == 1:
            return "yearly"
    
        # --- detect monthly ---
        # typical: one value per month, varying day (15/16 etc.)
        if n > n_years * 10 and n < n_years * 14:
            return "monthly"
    
        # --- detect daily ---
        # many entries per month, lots of unique days
        if n_days > 20:
            return "daily"
    
        return "unknown"


    def calc_temporal_mean_weighted(
        da,
        dim="time",
        freq_output=None,          # None, "monthly", "yearly", "climatology"
        weights=None,
        skip_if_native=True,
        verbosity=1):
        """
        Flexible temporal averaging with weighting.
    
        Parameters
        ----------
        da : xr.DataArray
        dim : str
            Time dimension
        freq_output : str or None
            - None: mean over full time period
            - "monthly": monthly means (year-month resolution)
            - "yearly": yearly means (one per year)
            - "climatology": multi-year monthly climatology (12 months)
        weights : xr.DataArray, optional
            Custom weights

        Returns
        -------
        xr.DataArray
        """

        time = da[dim]
        resolution = TimeOperator._infer_time_resolution(time)
        if verbosity>0:
            print(f'Input data has {resolution} resolution')

        # --- infer weights ---
        if weights is None:
            if hasattr(da[dim].dt, "days_in_month"):
                weights = da[dim].dt.days_in_month
            else:
                weights = xr.ones_like(da[dim])

        # helper
        def _weighted_mean(x):
            w = weights.sel({dim: x[dim]})
            w = w / w.sum(dim=dim)
            return (x * w).sum(dim=dim)
    
        # --- no grouping ---
        if freq_output is None:
            return _weighted_mean(da)

        # --- monthly (year-month resolution) ---
        elif freq_output == "monthly":
            if skip_if_native and resolution == "monthly":
                return da
            return da.resample({dim: "1MS"}).map(_weighted_mean)

        # --- yearly ---
        elif freq_output == "yearly":
            if skip_if_native and resolution == "yearly":
                return da                
            return da.resample({dim: "1YS"}).map(_weighted_mean)

        # --- climatology (12-month seasonal cycle) ---
        elif freq_output == "climatology":
            return da.groupby(f"{dim}.month").map(_weighted_mean)

        else:
            raise ValueError("freq_output must be None, 'monthly', 'yearly', or 'climatology'")

    
    def needs_time_fix(time_axis):
        years = np.array([dt.year for dt in time_axis])
        microsecs = np.array([dt.microsecond for dt in time_axis])
    
        return (
            np.all(years == 1970) and          # constant fake year
            np.all(microsecs > 1000) and       # looks like real years
            np.all(microsecs < 4000)           # reasonable year range
        )
    

    def adjust_time_axis(ds):

        if 'year' in ds.coords or 'year' in ds.dims:
            time_axis = ds.year.values
        elif 'time' in ds.coords or 'time' in ds.dims:
            time_axis = ds.time.values
            #print(time_axis)
            #if np.all([np.isinstance(time_axis_id))

        if TimeOperator.needs_time_fix(time_axis):

            new_time_axis = np.array([
                cftime.DatetimeProlepticGregorian(
                    dt.microsecond,  # move microsecond → year
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    0,               # reset microsecond
                    has_year_zero=True
                )
                for dt in time_axis], dtype=object)
        else:
            new_time_axis = np.array([
                cftime.DatetimeProlepticGregorian(
                    dt.year,  # move microsecond → year
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,               # reset microsecond
                    has_year_zero=True
                )
                for dt in time_axis], dtype=object)

        ds['time'] = new_time_axis

        # Remove 'year' if it exists as a variable or coordinate
        #if 'year' in ds.variables:
        #    ds = ds.drop_vars('year')
        if 'year' in ds.coords:
            ds = ds.drop_vars('year')  # works for coords too

        if 'year' in ds.coords or 'year' in ds.dims:
            ds = ds.rename({'year': 'time'})

        #print(ds)
        
        return ds


    def shift_time_axis_by_n_years(ds,n=0,set_to_start_of_months=False):

        # negative n shifts backward in time
        
        time_axis = ds.time.values

        if set_to_start_of_months == False:
            new_time_axis = np.array([
                cftime.DatetimeProlepticGregorian(
                    dt.year + n,  # move microsecond → year
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,               # reset microsecond
                    has_year_zero=True
                )
                for dt in time_axis], dtype=object)
        else:
            new_time_axis = np.array([
                cftime.DatetimeProlepticGregorian(
                    dt.year + n,  # move microsecond → year
                    dt.month,
                    1, #dt.day,
                    0, #dt.hour,
                    0, #dt.minute,
                    0, #dt.second,
                    0, #dt.microsecond,               # reset microsecond
                    has_year_zero=True
                )
                for dt in time_axis], dtype=object)            

        ds['time'] = new_time_axis
        
        return ds


    def shift_time_axis_to_ref_year(model,ds,ref_year=1850,set_to_start_of_months=False,verbosity=0):

        # identify how many years i need to shift:
        model_dict = pmods.get_model_dict('all')
        n = ref_year - model_dict[model].rampup_start_year
        if verbosity>0:
            print(f'{model}: shifting by {n} years')
        

        # now shift by n years
        ds = TimeOperator.shift_time_axis_by_n_years(ds,n,set_to_start_of_months=set_to_start_of_months)
        
        return ds

    def set_calendar(ds,model):
        model_dict = pmods.get_model_dict('all')
        calendar = model_dict[model].calendar
        if calendar == 'noleap':
            ds = ds.convert_calendar("noleap")
        return ds

    def integrate_in_time(da, model, freq_input='monthly',overwrite_leap_years=False,take_half_months_into_account=True):
        
        da = TimeOperator.set_calendar(da,model)
    
        units = da.attrs.get("units", "")
    
        # get number of days in each month (calendar-aware)
        if freq_input == 'monthly':
            days = da.time.dt.days_in_month
            if overwrite_leap_years == True:
                days = xr.where(days==29,28,days) # overwrite leap year
        elif freq_input == 'yearly':
            if da.indexes["time"].calendar == 'noleap':# model_dict[model].calendar == 'noleap':
                days = 365
            else:
                days = da.time.dt.is_leap_year.astype(int) + 365
        else:
            raise Exception('Not known time step.')
    
        # convert to seconds
        seconds = days * 24 * 3600
    
        # integrate
        da_times_time = da*seconds
        
        if take_half_months_into_account:
            da_times_time_shifted = da_times_time.shift(time=1, fill_value=0)
            # now take the half of each element
            da_times_time_half = da_times_time/2.
            da_times_time_shifted_half = da_times_time_shifted/2.
            #print(da_times_time_half)
            #print(da_times_time_shifted_half)
            #
            integrated_da = (da_times_time_half+da_times_time_shifted_half).cumsum(dim='time')
        else:
            integrated_da = (da_times_time).cumsum(dim="time")
    
        integrated_da.attrs["units"] = f"{units} x s"
        if np.any(days==29) and overwrite_leap_years == False:
            integrated_da.attrs["comment"] = f"integrated with leap years"
        elif np.all(days!=29) or overwrite_leap_years == True:
            integrated_da.attrs["comment"] = f"integrated without leap years"
        return integrated_da
        
    
    #def integrate_in_time(da,model):
    #
    #    model_dict = pmods.get_model_dict('all')
    #    calendar = model_dict[model].calendar
    #    if calendar == 'noleap':
    #        da = da.convert_calendar("noleap")
    #
    #    units = da.attrs.get("units", "")
    # 
    #    # time differences (length N-1)
    #    dt = da.time.diff("time")
    #
    #    # convert to seconds
    #    seconds = dt / np.timedelta64(1, "s")
    #
    #    # pad to match original length (assume first step same as second)
    #    seconds = seconds.reindex(time=da.time, method="bfill")
    #    print(seconds/3600/24)
    #
    #    # integrate
    #    integrated_da = (da * seconds).cumsum(dim="time")
    #
    #    integrated_da.attrs["units"] = f"{units} x s"
    #    return integrated_da

