import os
import tempfile
import logging
from subprocess import call, STDOUT
import zc.buildout

class ClosureCompile(object):
    def __init__(self, buildout, name, options):
        self.name = name
        basedir = buildout['buildout']['directory']

        self.compiler = options.get('compiler')

        if options.get('input') is None:
            raise zc.buildout.UserError("'input' option is missing.")

        self.input = [os.path.join(basedir, f) for f in options.get('input').split()]
        self.externs = [os.path.join(basedir, f) for f in options.get('externs', '').split()]

        if options.get('output') is None:
            if len(self.input) == 1:
                self.inplace = True
            else:
                raise zc.buildout.UserError("'output' option is missing.")
        else:
            self.output = os.path.join(basedir, options.get('output'))
            self.inplace = False

        self.level = options.get('level', 'WHITESPACE_ONLY')

    def install(self):

        if self.inplace:
            output = tempfile.NamedTemporaryFile()
            self.output = output.name

        cmd  = "java -jar %s "%self.compiler
        cmd += "--js %s --js_output_file %s "%(' --js '.join(self.input), self.output)
        if self.externs:
            cmd += "--externs %s "%" --externs ".join(self.externs)
        cmd += "--compilation_level %s "%self.level

        logging.getLogger(self.name).debug("running '%s'"%cmd)

        errors = tempfile.TemporaryFile()
        retcode = call(cmd.split(), stdout=errors, stderr=STDOUT)

        # fixme: check if retcode != 0

        if self.inplace:
            output.seek(0)
            open(self.input[0], 'w').write(output.read())
            output.close()
            return self.input
        else:
            return self.output

    update = install

