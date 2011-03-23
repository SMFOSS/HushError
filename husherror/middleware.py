from husherror.limiter import Limiter
import traceback
import sys
from webob import Response
from webob import dec
import json
import logging


logger = logging.getLogger(__name__)


class Hush(object):
    """
    A middleware for working with weberror to prevent flooding in
    certain mission critical situations.
    """

    limiter_class = Limiter
    
    def __init__(self, app, period=1, threshold=3, release=10, noraise=None, use_py_hash=False, exc_whitelist=set(), exc_blacklist=set(), store=None):
        """
        
        """
        self.app = app
        self.whitelist = exc_whitelist
        self.blacklist = exc_blacklist
        if store is None:
            self.limiter = self.limiter_class(period, threshold, release)
        else:
            self.limiter = self.limiter_class(period, threshold, release, store=store)
        self.noraise = noraise
        self.use_py_hash = use_py_hash
        if self.noraise is None:
            self.noraise = self.default_noraise

    def default_noraise(self, request, (et, ev, etb)):
        body = json.dumps(dict(error="%s" %ev.message))
        return Response(body=body, status=400, headers={'Content-Type': 'application/json'})

    def noraise_response(self, request, exc):
        """
        Calls whatever function has been set to generate a response
        for the captured exceptions.
        """
        return self.noraise(request, exc)

    def hash_exception(self, request, (etype, eval, etb)):
        """
        Creates a semi unique key for an exception based on the the
        following 5 characteristics of an exception::

        From where the exc occurred:
        
        * name of function 
        * truncated filename for module 
        * index of byte string of the code object

        Also:
        * Path info for original
        * name of exception type

        The resulting tuple is serialized. Depending on whether the
        middleware object is configured to use the python hash builtin
        or not, the serialize version is hashed. Resulting key is
        returned.
        """
        block_name = etb.tb_frame.f_code.co_name
        filename = "/".join((etb.tb_frame.f_code.co_filename.split('/')[-2:]))
        lineno = etb.tb_lineno
        last_instr = etb.tb_lasti
        identifier = (request.path_info, etype.__name__, filename, block_name, "%s.%s" %(lineno, last_instr))
        serialized = ":".join(identifier)
        if self.use_py_hash is True:
            return hash(serialized)
        return serialized

    def gated_response(self, request, (et, ev, etb)):
        """
        Checks limiter to determine whether an exception should be
        squelched or re-raised.
        """
        key = self.hash_exception(request, (et, ev, etb))
        gate = self.limiter.gate(key)
        if gate is True:
            return self.noraise_response(request, (et, ev, etb))
        raise ev

    def handle_request(self, request):
        """
        Attempt to return a valid response from the wrapped
        application. If it fails, proceed to check exception for
        inclusion in whitelisted or blacklisted exceptions, then pass
        to `gated_response`.

        Takes a request, returns a response.
        """
        try:
            return request.get_response(self.app)
        except Exception as e:
            if type(e) in self.whitelist:
                raise e
            exc_info = sys.exc_info()
            if type(e) in self.blacklist:
                return self.noraise_response(request, exc_info)
            return self.gated_response(request, exc_info)

    @dec.wsgify
    def __call__(self, request):
        """
        Provide a wsgi for `handle_request`
        """
        return self.handle_request(request)



    
 
