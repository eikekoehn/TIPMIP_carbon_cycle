import xarray as xr
import numpy as np
from pathlib import Path

from set_params import Runs as pruns
from operations_time import TimeOperator


class RConcatenator:
    def __init__(self,model,member,varia="tas",freq="monthly",stat="mean",root_dir="./../01_postprocessed_data/global_time_series"):
        self.model = model
        self.member = member
        self.varia = varia
        self.freq = freq
        self.stat = stat
        self.root_dir = root_dir

    # -------------------------
    # helpers
    # -------------------------
    def _build_filepath(self, run):
        return Path(
            f"{self.root_dir}/{self.varia}/{self.model}/{run}/"
            f"{self.member}/{self.freq}/global_{self.stat}/"
            f"{self.varia}_{self.model}_{run}_{self.member}_global_{self.stat}.nc")

    @staticmethod
    def trim_years_for_concatenation(year_tuples):
        trimmed = []
        for k in range(len(year_tuples)):
            start = year_tuples[k][0]
            if k < len(year_tuples) - 1:
                end = year_tuples[k + 1][0] - 1
            else:
                end = year_tuples[k][1]
            trimmed.append((start, end))
        return trimmed

    @staticmethod
    def remove_runs_from_history_if_before_concatenation_start(run_names, run_years, run, concatenation_start):
        if run != "esm-piControl" and concatenation_start in run_names:
            idx = run_names.index(concatenation_start)
            run_names = run_names[idx:]
            run_years = run_years[idx:]
        return run_names, run_years

    # -------------------------
    # core functionality
    # -------------------------
    def get_model_run_years(self, run):
        fp = self._build_filepath(run)

        if not fp.is_file():
            raise FileNotFoundError(f"Missing file: {fp}")

        with xr.open_dataset(fp, use_cftime=True) as ds:
            years = ds.time.dt.year.values

        return int(years[0]), int(years[-1])

    def get_run_history_years(self, run):
        run_history = pruns.get_run_history(run)
        run_names = []
        run_years = []
        for hist_run in run_history:
            try:
                yrs = self.get_model_run_years(hist_run)
                run_names.append(hist_run)
                run_years.append(yrs)
            except FileNotFoundError as e:
                raise Exception(
                    f"Missing run history for {self.varia}, {self.model}, {run}"
                ) from e

        return run_names, run_years

    def generate_list_of_das(self, run_names, run_years):
        das = []

        for run_name, (y0, y1) in zip(run_names, run_years):
            fp = self._build_filepath(run_name)
            if not fp.is_file():
                print(f"Skipping missing file: {fp}")
                continue
            with xr.open_dataset(fp, use_cftime=True) as ds:
                da = ds[f"{self.varia}_global_{self.stat}"]
            # ensure consistent calendar
            da = TimeOperator.shift_time_axis_by_n_years(da, n=0)
            # slice
            da = da.sel(time=slice(f"{int(y0):04d}-01-01", f"{int(y1):04d}-12-31"))
            if da.size > 0:
                das.append(da)

        return das

    def concat_da(self, das):
        if not das:
            # fallback: return minimal NaN DataArray
            return xr.DataArray([np.nan], dims=["time"])
        return xr.concat(das, dim="time")

    def get_concatenated_da(self,run,ref_year=1,concatenation_start="esm-up2p0"):
        # get run history
        run_names, run_years = self.get_run_history_years(run)
        # filter runs
        run_names, run_years = self.remove_runs_from_history_if_before_concatenation_start(run_names, run_years, run, concatenation_start)
        # trim years
        run_years = self.trim_years_for_concatenation(run_years)
        # load + slice
        das = self.generate_list_of_das(run_names, run_years)
        # concatenate
        da = self.concat_da(das)
        
        # shift to reference year
        if ref_year is not None:
            da = TimeOperator.shift_time_axis_to_ref_year(self.model, da, ref_year=ref_year)
            #print(da)
            # enforce start
            da = da.sel(time=slice(f"{ref_year:04d}-01-01", None))
        return da

