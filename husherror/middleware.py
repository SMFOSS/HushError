from collections import defaultdict
from husherror.limiter import Limiter
from itertools import count
from webob import dec
import logging

logger = logging.getLogger(__name__)


class HushMiddleWare(object):
    """
    A middleware for working with weberror to prevent flooding in
    certain mission critical situations.
    """

    limiter_class = Limiter
    
    def __init__(self, app, period, threshold, noraise_response, exc_whitelist=set(), exc_blacklist=set()):
        self.app = app
        self.whitelist = exc_whitelist
        self.blacklist = exc_blacklist
        self.noraise_response
        self.limiter = self.limiter_class(threshold, period)
        #self._mem_hit_count = defaultdict(count)

    def hash_exc(self):
        pass

    @dec.wsgify
    def __call__(self, request):
        try:
            return request.get_response(self.app)
        except Exception as e:
            if type(e) in self.whitelist:
                raise e
            if type(e) in self.blacklist:
                return 
#



    
 
