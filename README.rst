===========
 HushError
===========

If you use WebError, you may run into situations where a failure of
one or more systems will result in flood of notifications (say to
email) where one would do.

This package provides some knobs to staunch the flow of notifications.


Behavior Gating Middleware
==========================

`husherror.middleware.Hush` should wrap your wsgi app before
WebError. 

The following example shows how to employ 'Hush' with it's defaults::

>>> from husherror.middleware import Hush

>>> myapp = Hush(myapp, threshold=3, period=1, release=10)
>>> myapp = WebError(myapp, ...)

>>> serve(myapp)

By default, the middleware defines defaults for threshold, period, and
release that will prevent errors from bubbling up beyond the
middleware is more than 3 exceptions per second are thrown along a
specific code path. By default, Hush will continue to gate
notifications until the number of errors per second stays under 3 for
10 seconds.


How it works
============

An error is keyed and recorded for frequency by passing the key to the
`Limiter`, which returns whether or not this key is "gated".

