from collections import defaultdict
from functools import partial
from itertools import count


class InMemoryStore(object):
    """
    Memory based store for gating.  No network overhead, no ability to
    sync with other procs.
    """
    def __init__(self):
        self._last_seen = dict()
        self._gated = dict()
        self._howmany = defaultdict(partial(count, 1))

    def last_seen(self, (key, time_seen)):
        last_seen = self._last_seen.get(key, time_seen)
        self._last_seen[key] = time_seen
        return last_seen, next(self._howmany[key])

    def gate(self, (key, time)):
        self._gated[key] = time

    def last_gated(self, key):
        return self._gated.get(key, None)

    def reset_count(self, key):
        self._howmany[key] = count(1)


## class RedisStore(object):
##     def __init__(self, dsn, prefix='husherror'):
##         self.dsn = dsn

##     @property
##     def last_seen(self):
##         pass

##     @property
##     def gated(self):
##         pass

##     @property
##     def howmany(self):
##         pass
    

## class RedisDict(dict):
##     def __init__(self, redis, hashname):
##         self.redis = redis
##         self.hashname = hashname

##     def __getitem__(self, key):
##         return self.redis.hget(self.hashname, key)

##     def __setitem__(self, key, value):
##         self.redis.hset(self.hashname, key, value)

##     def __delitem__(self, key):
##         self.redis.hdel(self.hashname, key)

##     def keys(self):
##         return self.redis.hkeys(self.hashname)

##     def __contains__(self, key):
##         return self.redis.hexists(self.hashname, key)



## #__getitem__(), __setitem__(), __delitem__(), and keys()
