from husherror import store
from mock import Mock
from nose.tools import raises
from webob import Response
from webob import dec
from webtest import TestApp
import json
import sys
import unittest


boom = Exception("KABOOM")

class TestException(Exception):
    """
    A test exception
    """

class TestMW(unittest.TestCase):

    def setUp(self):
        from husherror import middleware as mw
        self.request = Mock()
        self.request.path_info = '/mypath'
        self.request.get_response = Mock(side_effect=boom, name='response')
        self.mod = mw

    def make_one(self, app, **kw):
        return self.mod.Hush(app, store=store.InMemoryStore(), **kw)

    def test_init(self):
        newhush = self.mod.Hush(Mock())
        assert newhush.limiter.store

    def test_hash_exc(self):
        pass

    @raises(Exception)
    def test_basic_exeception_reraised(self):
        app = self.make_one(Mock())
        app.handle_request(self.request)
    
    def test_basic_exception_blacklist(self):
        self.request.get_response = Mock(side_effect=TestException('KABOOM'), name='response')
        app = self.make_one(Mock(), exc_blacklist=set((TestException,)))
        res = app.handle_request(self.request)
        assert res.headers['Content-Type'] == 'application/json'
        assert json.loads(res.body)['error'] == 'KABOOM'

    def test_squelch(self):
        app = self.make_one(Mock())
        self.request.get_response = Mock(side_effect=TestException('KABOOM'), name='response')
        for i in xrange(app.limiter.threshold):
            try:
                app.handle_request(self.request)
                assert False, "Exceptions not being bubbled"
            except TestException:
                pass

        # now the threshold should be exceeded
        res = app.handle_request(self.request)
        assert res.headers['Content-Type'] == 'application/json'
        assert json.loads(res.body)['error'] == 'KABOOM'

    @raises(TestException)
    def test_whitelist(self):
        app = self.make_one(Mock(), exc_whitelist=set((TestException,)))
        self.request.get_response = Mock(side_effect=TestException('KABOOM'), name='response')
        for i in xrange(app.limiter.threshold):
            try:
                app.handle_request(self.request)
                assert False, "Exception should always be raised if whitelisted"
            except TestException:
                pass

        # now the threshold should be exceeded
        # but the exception should still be raised
        app.handle_request(self.request)

    def test_hashing(self):
        self.request.get_response = Mock(side_effect=TestException('KABOOM'), name='response')
        app1 = self.make_one(Mock(), use_py_hash=True)
        app2 = self.make_one(Mock(), use_py_hash=False)
        try:
            app1.handle_request(self.request)
        except TestException:
            exc = sys.exc_info()
            key1 = app1.hash_exception(self.request, exc)
            assert isinstance(key1, int)

        try:
            app2.handle_request(self.request)
        except TestException:
            exc = sys.exc_info()
            key2 = app2.hash_exception(self.request, exc)
            assert isinstance(key2, basestring), key2
            assert key2.startswith('/mypath:TestException:tests/test_middleware.py:test_hashing:'), key2

        try:
            app2.handle_request(self.request)
        except TestException:
            exc = sys.exc_info()
            key2 = app2.hash_exception(self.request, exc)
            app2.use_py_hash = True
            key1 = app2.hash_exception(self.request, exc)
            assert hash(key2) == key1, "%s != %s" %(hash(key2), key1)


def test_mw_wsgi_call():
    """
    Test that our webob dispatch works (to complete coverage)
    """
    from husherror import middleware as mw
    app = TestApp(mw.Hush(dummy))
    res = app.get('/')
    assert res and res.body == 'Ok'


@dec.wsgify
def dummy(request):
    return Response("Ok")
