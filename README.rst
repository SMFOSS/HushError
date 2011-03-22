===========
 HushError
===========

If you use WebError, you may run into situations where a failure of
one or more systems will result in flood of notifications (say to
email) where one would do.

This package provides some knobs to staunch the flow of notifications.


Behavior Gating Middleware
==========================

An error is keyed and recorded for frequency by passing the key to the
`Limiter`, which returns whether or not this key is "gated".

