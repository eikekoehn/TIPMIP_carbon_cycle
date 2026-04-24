import xarray as xr
import re
from datetime import datetime
from pathlib import Path

#class ModelHandler:
#    #from model_grabber_IPSL import IPSLgrabber
#    def def_grabber():
#        grabber = dict()
#        grabber['IPSL'] = IPSLgrabber
#        grabber['UKESM'] = UKESMgrabber
#        grabber['MIROC'] = MIROCgrabber
#        grabber['NASA-GISS'] = NASAgrabber
#        grabber['ECEarth3-ESM-1'] = ECEARTHgrabber
#        grabber['ACCESS-ESM1-5'] = ACCESSgrabber
#        grabber['CESM2'] = CESM2grabber
#        grabber['CNRM'] = CNRMgrabber
#        grabber['NorESM2-LM'] = NorESMgrabber
#        grabber['GFDL-ESM2M'] = UBERNgrabber

class DataFuncs:

    def open_dataset(files):
        if isinstance(files,list):
            if len(files) > 1:
                ds = xr.open_mfdataset(files,use_cftime=True)
            elif len(files) == 1:
                ds = xr.open_dataset(files[0],use_cftime=True)
            elif len(files) == 0:
                raise Exception('No file found...')
        else:
            ds = xr.open_dataset(files,use_cftime=True)
        return ds

    def close_dataset(ds):
        ds.close()
        return print('.... datset closed')


class MISCgrabber:

    def parse_dates(filename):
        """Extract start and end dates (YYYYMM) from filename."""
        match = re.search(r'(\d{6})-(\d{6})\.nc$', filename)
        if not match:
            return None, None
        start_str, end_str = match.groups()
        start = datetime.strptime(start_str, "%y%m" if len(start_str) == 4 else "%Y%m")
        end = datetime.strptime(end_str, "%y%m" if len(end_str) == 4 else "%Y%m")
        return start, end
    
    def months_between(start, end):
        """Calculate number of months between two datetime objects."""
        return (end.year - start.year) * 12 + (end.month - start.month) + 1
    
    def filter_longest_period_files(files):
        """
        Given a list of .nc filenames, return a list with overlapping or redundant
        files removed — keeping the one that covers the largest time period.
        """
        parsed = []
        for f in files:
            start, end = MISCgrabber.parse_dates(f)
            if start and end:
                parsed.append({
                    'file': f,
                    'start': start,
                    'end': end,
                    'months': MISCgrabber.months_between(start, end)
                })
    
        # Sort by start ascending, then by duration descending (longest first)
        parsed.sort(key=lambda x: (x['start'], -x['months']))
    
        keep = []
        for p in parsed:
            # Check overlap with already kept files
            overlap = any(
                not (p['end'] < k['start'] or p['start'] > k['end'])
                for k in keep
            )
            if not overlap:
                keep.append(p)
            else:
                # Only keep if this file covers a larger period
                for k in keep:
                    if not (p['end'] < k['start'] or p['start'] > k['end']):
                        if p['months'] > k['months']:
                            keep.remove(k)
                            keep.append(p)
                        break
    
        return [p['file'] for p in keep]


class miniFuncs:

    def is_available(file_string):
        # do the check
        from pathlib import Path
        file_path = Path(file_string)
        if file_path.exists():
            available=True
        else:
            available=False
        return available