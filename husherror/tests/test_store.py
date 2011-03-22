import unittest
from itertools import count


class InMemoryStoreTest(unittest.TestCase):
    def setUp(self):
        from husherror import store
        self.mod = store
        self.time = count() # flashback to the seventies

    def make_one(self):
        return self.mod.InMemoryStore()

    def test_incrementation_by_last_seen(self):
        ims = self.make_one()
        time = next(self.time)
        assert ims.last_seen(('key1', time)) == (0, 1)
        assert ims.last_seen(('key1', next(self.time))) == (0, 2)
        assert ims.last_seen(('key1', next(self.time))) == (1, 3)
        ims.reset_count('key1') 
        assert ims.last_seen(('key1', next(self.time))) == (2, 1) # time should increase, but count should return to 1

    def test_gating(self):
        ims = self.make_one()
        ims.gate(('key', 1))
        assert 'key' in ims._gated
        assert ims.last_gated('key') == 1
        
