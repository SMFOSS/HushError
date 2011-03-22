from itertools import count
import time
import unittest


class LimiterTest(unittest.TestCase):
    
    def setUp(self):
        from husherror import limiter
        self.mod = limiter

    def make_one(self, p=0.5, t=5, r=3):
        from husherror import store
        s = store.InMemoryStore()
        return self.mod.Limiter(p, t, r, s)


    def load_key(self, key, store, howmany=5):
        """
        Loads $howmany hits for a key
        """
        epoch_now = time.time()
        return [store.last_seen((key, epoch_now)) for x in xrange(howmany)]

    def test_below_threshold(self):
        """
        acceptance test for main api call
        """
        limiter = self.make_one()
        key1 = 'key1'
        assert limiter.gate(key1) is False

    def test_exceed_threshold(self):
        limiter = self.make_one(0.01)
        key = 'k'
        self.load_key(key, limiter.store)
        assert limiter.gate(key) is True

    def test_release(self):
        limiter = self.make_one(0.01)
        key = 'k'
        ls = self.load_key(key, limiter.store, 6)
        loaded, howmany = ls[0]

        release_period = limiter.period * limiter.release
        clock = time.time() - loaded
        counter = count(1)
        slept = 0
        while clock < release_period:
            i = next(counter)
            gate = limiter.gate(key)
            assert gate is True, "%s: Test #%s at %s, slept %s" %(gate, i, clock, slept)
            time.sleep(0.01)
            slept += 0.01
            clock = time.time() - loaded

        gate = limiter.gate(key)
        assert gate is False, "Gate is still on" %gate

