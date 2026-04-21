import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

class Operator:


    def calc_spatial_mean(da, area_weights, mask=None, dims=None):
        """
        Compute area-weighted spatial mean of a DataArray.
        
        Parameters
        ----------
        da : xr.DataArray
            Input data (can include time dimension)
        area_weights : xr.DataArray
            Grid cell area weights (same spatial dims as da)
        mask : xr.DataArray, optional
            Mask (1 for valid, NaN or 0 for invalid)
        dims : list or tuple, optional
            Spatial dimensions to average over (e.g., ['lat', 'lon'])

        Returns
        -------
        xr.DataArray
            Area-weighted spatial mean
        """
    
        # Infer spatial dims if not provided
        if dims is None:
            dims = area_weights.dims

        # make sure that the coordinates area the same
        for coord in area_weights.coords:
            diff_coord = da[coord].values - area_weights[coord].values
            sum_diff_coord = np.sum(np.abs(diff_coord))
            unique_diffs = np.unique(diff_coord)
            if sum_diff_coord > 0:
                print(f'There is a total coordinate difference of: {sum_diff_coord}')
                if np.sum(np.abs((da[coord].values - area_weights[coord].values))) < 1e-8:
                    print(f'... this is small enough (smaller than 1e-8), so we just set the area_weights.coord to da.coord.')
                    area_weights = area_weights.assign_coords({coord: da[coord]})
                elif np.all(np.isin(unique_diffs, [-360, 0, 360])):
                    print(f'... all of the differences are just caused by 360° longitude wrapping. So we just set the area_weights.coord to da.coord.')
                    area_weights = area_weights.assign_coords({coord: da[coord]})        
                else:
                    raise Exception('Coordinates do not match')

        # Apply mask if provided
        if mask is not None:
            da = da.where(mask)
            area_weights = area_weights.where(mask)
        
        # Weighted sum (numerator)
        numerator = (da * area_weights).sum(dim=dims)

        # Effective weights (denominator)
        denominator = area_weights.where(~np.isnan(da)).sum(dim=dims)

        spatial_mean = numerator / denominator

        return spatial_mean

    def calc_spatial_integral(da, area_weights, mask=None, dims=None):
        """
        Compute area-weighted spatial integral of a DataArray.

        Parameters
        ----------
        da : xr.DataArray
            Input data (can include time dimension)
        area_weights : xr.DataArray
            Grid cell areas (same spatial dims as da, e.g. m^2)
        mask : xr.DataArray, optional
            Mask (1 for valid, NaN or 0 for invalid)
        dims : list or tuple, optional
            Spatial dimensions to integrate over (e.g., ['lat', 'lon'])

        Returns
        -------
        xr.DataArray
            Spatial integral (units = da * area)
        """

        # Infer spatial dims if not provided
        if dims is None:
            dims = area_weights.dims

        # make sure that the coordinates area the same
        for coord in area_weights.coords:
            diff_coord = da[coord].values - area_weights[coord].values
            sum_diff_coord = np.sum(np.abs(diff_coord))
            unique_diffs = np.unique(diff_coord)
            if sum_diff_coord > 0:
                print(f'There is a total coordinate difference of: {sum_diff_coord}')
                if np.sum(np.abs((da[coord].values - area_weights[coord].values))) < 1e-8:
                    print(f'... this is small enough (smaller than 1e-8), so we just set the area_weights.coord to da.coord.')
                    area_weights = area_weights.assign_coords({coord: da[coord]})
                elif np.all(np.isin(unique_diffs, [-360, 0, 360])):
                    print(f'... all of the differences are just caused by 360° longitude wrapping. So we just set the area_weights.coord to da.coord.')
                    area_weights = area_weights.assign_coords({coord: da[coord]})        
                else:
                    raise Exception('Coordinates do not match')
    
        # Apply mask if provided
        if mask is not None:
            da = da.where(mask)
            area_weights = area_weights.where(mask)
            
        # Integral = sum(x * dA)
        integral = (da * area_weights).sum(dim=dims)

        return integral


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
    
        # --- detect annual ---
        if n_months == 1 and n_days == 1:
            return "annual"
    
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
        freq_output=None,          # None, "monthly", "annual", "climatology"
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
            - "annual": annual means (one per year)
            - "climatology": multi-year monthly climatology (12 months)
        weights : xr.DataArray, optional
            Custom weights

        Returns
        -------
        xr.DataArray
        """

        time = da[dim]
        resolution = Operator._infer_time_resolution(time)
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

        # --- annual ---
        elif freq_output == "annual":
            if skip_if_native and resolution == "annual":
                return da                
            return da.groupby(f"{dim}.year").map(_weighted_mean)

        # --- climatology (12-month seasonal cycle) ---
        elif freq_output == "climatology":
            return da.groupby(f"{dim}.month").map(_weighted_mean)

        else:
            raise ValueError("freq_output must be None, 'monthly', 'annual', or 'climatology'")


