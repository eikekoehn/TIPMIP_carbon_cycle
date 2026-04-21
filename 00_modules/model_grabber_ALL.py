from model_grabber_IPSL import IPSLgrabber
from model_grabber_UBERN import UBERNgrabber
from model_grabber_NorESM import NorESMgrabber

class MODELgrabber:

    @classmethod
    def get_grabber(cls,model):
        if model == 'IPSL-CM6-ESMCO2':
            grabber = IPSLgrabber
        elif model == 'GFDL-ESM2M':
            grabber = UBERNgrabber
        elif model == 'NorESM2-LM':
            grabber = NorESMgrabber
        return grabber

