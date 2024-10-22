import subprocess
import sys
import futhark_data
import tempfile

class Failure(Exception):
    pass

class Server:
    """An instance of this class represents a running Futhark server.
    When created, it is passed the path to a server executable and
    optionally some options.

    Each command supported in the server protocol is exposed as a
    method on this class, prefixed with cmd_.

    Further, some convenience facilities for accessing values are also
    provided.

    The exception Failure is raised when a command fails.

    The exception Exception is raised when the server process
    terminates unexpectedly.

    """

    def __init__(self, exe, *opts):
        self.exe = opts
        self.opts = opts
        self.proc = subprocess.Popen([exe] + list(opts),
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     shell=False,
                                     stderr=None,
                                     text=True)
        self._read_response()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.proc.stdin.close()
        self.proc.stdout.close()
        self.proc.wait()
        return False

    def _read_response(self):
        ls = []
        while True:
            l = self.proc.stdout.readline()
            if l == '%%% OK\n':
                return ls
            if l == '%%% FAILURE\n':
                err = self._read_response()
                raise Failure('\n'.join(err))
            elif l == '':
                raise Exception('Unexpected EOF from Futhark server process.')
            ls = ls + [l[:-1]] # Remove final \n

    def cmd(self, *args):
        """Send a raw command to the server.

        This is mostly useful when the server protocol has been
        extended without this library having received similar
        extensions. Use the specific command methods in all other
        cases."""
        self.proc.stdin.write(' '.join(args) + '\n')
        self.proc.stdin.flush()
        return self._read_response()

    def cmd_types(self):
        return self.cmd('types')

    def cmd_entry_points(self):
        return self.cmd('entry_points')

    def cmd_call(self, entry, *vs):
        return self.cmd('call', entry, *vs)

    def cmd_restore(self, file, *pairs):
        """Restore Futhark value from file.

        The 'pairs' must be pairs of unused variable names and types.

        """
        args = []
        for x,y in pairs:
            args += [x,y]
        self.cmd('restore', file, *args)

    def cmd_store(self, file, *vs):
        self.cmd('store', file, *vs)

    def cmd_free(self, *vs):
        self.cmd('free', *vs)

    def cmd_rename(self, oldname, newname):
        self.cmd('rename', oldname, newname)

    def cmd_inputs(self, entry):
        return self.cmd('inputs', entry)

    def cmd_outputs(self, entry):
        return self.cmd('outputs', entry)

    def cmd_clear(self):
        self.cmd('clear')

    def cmd_pause_profiling(self):
        self.cmd('pause_profiling')

    def cmd_unpause_profiling(self):
        self.cmd('unpause_profiling')

    def cmd_report(self):
        return self.cmd('report')

    def cmd_set_tuning_param(self, param, value):
        self.cmd('set_tuning_param', param, value)

    def cmd_tuning_params(self, entry):
        return self.cmd('tuning_params', entry)

    def cmd_tuning_param_class(self, param):
        return self.cmd('tuning_param_class', param)[0]

    def cmd_fields(self, type):
        return self.cmd('fields', type)

    def cmd_new(self, v, type, fields):
        todo

    def cmd_project(self, newname, name, field):
        self.cmd('project', newname, name, field)

    def get_value(self, v):
        """Retrieve Futhark value in given variable.

        This only produces a meaningful value if the type of the value
        is non-opaque (i.e., a primitive or array of primitives).

        """
        def unpack(val):
            if len(val.shape) == 0:
                # Convert rank 0 arrays to scalars.
                return val[()]
            else:
                return val
        with tempfile.NamedTemporaryFile() as f:
            self.cmd_store(f.name, v)
            vs = list(map(unpack, futhark_data.load(f)))
            if len(vs) == 1:
                return vs[0]
            else:
                return tuple(vs)

    def put_value(self, var, val):
        """Create Futhark variable with given value.

        The value must be a NumPy value of a NumPy type corresponding
        to a Futhark primitive or array of primitives. Raises
        Exception otherwise.

        """

        rank = len(val.shape)
        primname = futhark_data.numpy_type_to_type_name(val.dtype)
        t = rank * "[]" + primname

        with tempfile.NamedTemporaryFile() as f:
            futhark_data.dump(val, f, binary=True)
            f.flush()
            self.cmd_restore(f.name, (var,t))

    def get_value_bytes(self, v):
        """Retrieve byte representation of Futhark value."""
        with tempfile.NamedTemporaryFile() as f:
            self.cmd_store(f.name, v)
            return f.read()

    def put_value_bytes(self, bs, pairs):
        """Construct Futhark value from byte representation.

        The 'pairs' argument must be a list of pairs of names and
        types.

        """
        with tempfile.NamedTemporaryFile() as f:
            f.write(bs)
            f.flush()
            self.cmd_restore(f.name, pairs)
