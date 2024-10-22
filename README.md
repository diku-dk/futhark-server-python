# Python implementation of the Futhark server protocol

This library library provides an implementation of the
[Futhark](https://futhark-lang.org) [server
protocol](https://futhark.readthedocs.io/en/latest/server-protocol.html).
This can be used to interact with Futhark code in a more decoupled
manner than through an FFI.

## Basic usage

First compile a Futhark program `foo.fut` to a server-mode binary with
e.g. `futhark c --server`. Then instantiate a `futhark_server.Server`
object:

```Python
import futhark_server

with futhark_server.Server('./test') as server:
  ...
```

The `Server` class has various methods for interacting with the
server. In particular, every servr protocol command `foo` has an
associated method `cmd_foo`.
