from husherror import store
import logging
import time


logger = logging.getLogger(__name__)


class Limiter(object):
    """
    Object for testing a particular seen value against a threshold for
    a period
    """
    def __init__(self, period, threshold, release, store=store.InMemoryStore()):
        """
        period -- time represent a segment of interest

        threshold -- number of events for a period of interest
        
        release -- # of periods the # of events must drop below the
                   threshold to ungate.

        store -- an instance of a storage mediator
        """
        self.period = period
        self.threshold = threshold
        self.store = store
        self.release = release

    def period_count(self, key, now):
        last_seen, count = self.store.last_seen((key, now))
        if (now - last_seen > self.period):
            self.store.reset_count(key)
            last_seen, count = self.store.last_seen((key, now))
        return count

    @property
    def release_period(self):
        return self.release * self.period
        
    def test_and_gate(self, key, test_rate, now, gated=False):
        rate = self.period_count(key, now)
        gate = False

        if rate > test_rate:
            self.store.gate((key, now))
            gate = True

        # if we have been previously gates, we must wait till the end
        # of release envelope to stop limiting
        if gated:
            since_gated = now - gated
            gate = since_gated < self.release_period
        return gate

    def prepare(self, key):
        """
        a hook for subclasses
        """
        pass

    def gate(self, key):
        self.prepare(key)
        epoch_now = time.time()
        last_gated = self.store.last_gated(key)
        
        if last_gated is not None:
            return self.test_and_gate(key, self.threshold, epoch_now, gated=last_gated)
        return self.test_and_gate(key, self.threshold, epoch_now)

        


    

