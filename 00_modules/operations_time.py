import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cftime

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

        if 'year' in ds.coords or year in ds.dims:
            time_axis = ds.year.values
        elif 'time' in ds.coords or year in ds.dims:
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
        if 'year' in ds.variables:
            ds = ds.drop_vars('year')
        elif 'year' in ds.coords:
            ds = ds.drop_vars('year')  # works for coords too

        ds = ds.rename({'year': 'time'})

        #print(ds)
        
        return ds
        


