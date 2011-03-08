from webob import dec

class HushMiddleWare(object):
    """
    A middleware for working with weberror to prevent flooding in
    certain mission critical situations.
    """
    def __init__(self, app, period, threshold, exc_whitelist=set(), exc_blacklist=set()):
        self.app = app
        self.period = period
        self.threshold = threshold
        self.whitelist = exc_whitelist
        self.blacklist = exc_blacklist

    @dec.wsgify
    def __call__(self, request):
        try:
            return request.get_response(self.app)
        except Exception as e:
            if type(e) in self.whitelist:
                raise e



    
 
