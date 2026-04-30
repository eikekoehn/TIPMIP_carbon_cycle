import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

class SpaceOperator:

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


    def calc_vertical_integral(da, thickness_weights, mask=None, dims=None):
        import xarray as xr
    
        # --------------------------------------------------
        # detect vertical dims
        # --------------------------------------------------
        if dims is None:
            vertical_candidates = {"lev", "level", "levelo", "depth", "deptho"}
            dims = [d for d in da.dims if d.lower() in vertical_candidates]
    
            if len(dims) == 0:
                raise ValueError(f"No vertical dimension found in {da.dims}")
    
        # --------------------------------------------------
        # ensure dask (critical for big data)
        # --------------------------------------------------
        #if not da.chunks:
        #    da = da.chunk({dims[0]: -1})  # chunk vertically (fast reduction)
    
        #if not thickness_weights.chunks:
        #    thickness_weights = thickness_weights.chunk({dims[0]: -1})
    
        # --------------------------------------------------
        # align WITHOUT copying data
        # --------------------------------------------------
        #da, thickness_weights = xr.align(da, thickness_weights, join="inner", copy=False)
        #thickness_weights = thickness_weights.broadcast_like(da)
        # --------------------------------------------------
        # mask (lazy)
        # --------------------------------------------------
        if mask is not None:
            da = da.where(mask)
    
        # --------------------------------------------------
        # vertical integral (lazy, no big temp array)
        # --------------------------------------------------
        #integral = xr.dot(da, thickness_weights, dims=dims)
        integral = (da * thickness_weights).sum(dim=dims)
    
        # --------------------------------------------------
        # metadata
        # --------------------------------------------------
        integral.attrs = da.attrs.copy()
        integral.attrs["long_name"] = f"vertical integral of {da.name}"
    
        return integral


