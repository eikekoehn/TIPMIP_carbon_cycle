from model_grabber_IPSL import IPSLgrabber

class MODELgrabber:

    @classmethod
    def get_grabber(cls,model):
        if model == 'IPSL-CM6-ESMCO2':
            grabber = IPSLgrabber
        return grabber
