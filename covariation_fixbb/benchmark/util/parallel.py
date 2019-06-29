#!/usr/bin/env python
# -*- coding: utf-8 -*-
# :noTabs=true:
# (c) Copyright Rosetta Commons Member Institutions.
# (c) This file is part of the Rosetta software suite and is made available under license.
# (c) The Rosetta software is developed by the contributing members of the Rosetta Commons.
# (c) For more information, see http://www.rosettacommons.org. Questions about this can be
# (c) addressed to University of Washington CoMotion, email: license@uw.edu.
#
## @file   parallel.py
## @brief  Script to parallelize run of arbitrary command lines
## @author Sergey Lyskov

from __future__ import print_function

import sys, signal

import os, re, subprocess, time, json
from os import path
from optparse import OptionParser


class OI:
    def __init__(self, **entries): self.__dict__.update(entries)


class Runner:
    def __init__(self, jobs, quiet=False, quiet_errors=False):
        self.njobs = jobs
        self.quiet = quiet
        self.quiet_errors = quiet_errors

        self.jobs = []    # list of spawned process pid's
        self.output = ''  # output of current job

    def log(self, message):
        self.output += message
        if not self.quiet: print(message)

    def log_error(self, message):
        self.output += message
        if not self.quiet_errors:
            sys.stderr.write( message + "\n")

    def mfork(self):
        ''' Check if number of child process is below self.njobs. And if it is - fork the new process and return its pid.
        '''
        while len(self.jobs) >= self.njobs :
            for p in self.jobs[:] :
                r = os.waitpid(p, os.WNOHANG)
                if r == (p, 0):  # process has ended without error
                    self.jobs.remove(p)
                elif r[0] == p :  # process ended, but with error. Special case: we will have to wait for all process to terminate and call system exit.
                    for p in self.jobs: os.waitpid(p, 0)
                    sys.stderr.write('Some of the processes terminated abnormally!\n')
                    sys.exit(1)

            if len(self.jobs) >= self.njobs: time.sleep(.5)

        #pid = os.fork()

        #while True:
        try:
            pid = os.fork()
        except OSError as e:
            sys.stderr.write('Error: os.fork() failure: {0}\n'.format(e))
            sys.exit(1)


        if pid: self.jobs.append(pid) # We are parent!
        return pid


    def signal_handler(self, signal_, f):
        sys.stderr('Ctrl-C pressed... killing child jobs...\n')
        for pid in self.jobs:
            os.killpg(os.getpgid(pid), signal.SIGKILL)


    def runCommandLine(self, file_, line_, command_line, output_file=''):
        self.log("Running %s:%s %s" % (file_, line_, command_line) )

        p = subprocess.Popen(command_line, bufsize=0, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # if not output_file:
        #     f = p.stderr
        #     for line in f:
        #         self.log_error(line)
        #         sys.stdout.flush()
        #     f.close()

        output, errors = p.communicate()

        # p.communicate() give us raw byte streams, which we then throw to files/output as raw byte streams
        # There's only unicode issues if the input and output encoding doesn't match (and there's no way to tell that).

        if output_file:
            with file(output_file, 'w') as f: f.write(output);  f.write(errors)
            sys.stderr.write( errors )
        else:
            sys.stdout.write( output )
            sys.stderr.write( errors )

        #exit_code = os.waitpid(p.pid, 0)[1]
        exit_code = p.returncode

        return exit_code


    def run_commands_lines(self, name, commands_lines, working_dir, delete_intermediate_files=True):
        ''' Accept dict of command lines, run them in paralell (constarained by int in `jobs`) and and return dict of results

            name - name prefix for intermediate results file names (ie Job Name)

            working_dir - path to working directory

            Example commands_lines:
            {
                "name-of-job1" : "<command line for job1>",
                "job2"         : "<command line for job2>",
            }

            return value:
            {
                  "name-of-job1": {
                    "output": "stdout + stderr of job1 command line",
                    "result": <int exit code>
                  },
                  "job2": {
                    "output": "stdout + stderr of job2 command line",,
                    "result": <int exit code>
                  },
            }

        '''
        signal.signal(signal.SIGINT, self.signal_handler)

        file_name = os.path.join(working_dir, name)

        results = {}

        for c in commands_lines:
            results[c] = {}

            output_file = os.path.abspath( file_name + '.{}.output'.format(c) )
            result_file = os.path.abspath( file_name + '.{}.result'.format(c) )

            results[c]['output_file'] = output_file
            results[c]['result_file'] = result_file

            if os.path.isfile(output_file): os.remove(output_file)

            pid = self.mfork()
            if not pid:  # we are the child process
                result = self.runCommandLine('', '', commands_lines[c], output_file=output_file) # + ' 2>&1 1>>{0} 2>>{0}'.format(output_file) )
                with file(result_file, 'w') as fh: fh.write( '{}'.format(result) )
                sys.exit(0)

        for p in self.jobs: os.waitpid(p, 0)  # waiting for all child process to termintate...

        r = {}
        for c in results:
            with open( results[c]['result_file'] ) as f: result = json.load(f)
            with open( results[c]['output_file'] ) as f: output = f.read()

            r[c] = dict(result = result, output = output)

            if not self.quiet: print(c, r[c]['result'], r[c]['output'])

            if delete_intermediate_files:
                if os.path.isfile(results[c]['result_file']): os.remove(results[c]['result_file'])
                if os.path.isfile(results[c]['output_file']): os.remove(results[c]['output_file'])

        return r



    def run(self, files):
        signal.signal(signal.SIGINT, self.signal_handler)
        for f in files:

            if f.endswith('.json'):
                file_name = f[:-len('.json')]

                commands_lines = json.load( file(f) )

                results = {}

                for c in commands_lines:
                    results[c] = {}

                    output_file = os.path.abspath( file_name + '.{}.output'.format(c) )
                    result_file = os.path.abspath( file_name + '.{}.result'.format(c) )

                    results[c]['output_file'] = output_file
                    results[c]['result_file'] = result_file

                    if os.path.isfile(output_file): os.remove(output_file)

                    pid = self.mfork()
                    if not pid:  # we are the child process
                        result = self.runCommandLine(f, c, commands_lines[c], output_file=output_file) # + ' 2>&1 1>>{0} 2>>{0}'.format(output_file) )
                        with file(result_file, 'w') as fh: fh.write( '{}'.format(result) )
                        sys.exit(0)

                for p in self.jobs: os.waitpid(p, 0)  # waiting for all child process to termintate...

                results = { c: dict(result=json.load(file(results[c]['result_file'])), output=file(results[c]['output_file']).read()) for c in results }

                for c in results: print( c, results[c]['result'], results[c]['output'] )

                with file( file_name + '.results.json', 'w') as fh: json.dump(results, fh, sort_keys=True, indent=2)


            else:
                # Preserving old behavior for jobs specified in ‘flat’ plain-text files

                prefix = Options.prefix
                if len(files) > 1  and  prefix:
                    prefix += '_' + f

                for i, l in enumerate(file(f)):
                    pid = self.mfork()
                    if not pid:  # we are the child process
                        self.runCommandLine(f, i, l)
                        if prefix: file(prefix + '.%.4d' % i, 'w').write(self.output)
                        sys.exit(0)

                for p in self.jobs: os.waitpid(p, 0)  # waiting for all child process to termintate...



def main(args):
    ''' Script to run Jobs in parallel.

        Input file could be ether plain text file with each line containing the command line to run or json file

        If input is file.json then the following content is expected:

        {
            "name-of-job1" : "<command line for job1>",
            "name-of-job2" : "<command line for job2>",
        }

        Example input file:
        {
            "c1" : "ls",
            "c2" : "echo 'this is command line2!'",
            "ce" : "some_error_command..."
        }

        If input specified as json file then as output file.reuslts.json will be enerated with following structure:

        {
              "name-of-job1": {
                "output": "stdout + stderr of job1 command line",
                "result": <int exit code>
              },
              "c2": {
                "output": "stdout + stderr of job2 command line",,
                "result": <int exit code>
              },
        }

        Example output:

        {
          "c1": {
            "output": "test.c1.result\ntest.c2.output\ntest.c2.result\ntest.ce.result\ntest.json\ntest.results.json\n",
            "result": 0
          },
          "c2": {
            "output": "this is command line2!\n",
            "result": 0
          },
          "ce": {
            "output": "/bin/sh: some_error_command...: command not found\n",
            "result": 127
          }
        }
    '''
    parser = OptionParser(usage="usage: %prog [OPTIONS] file_with_command_lines[.json] [file2[.json]] [file3[.json]] ...")
    parser.set_description(main.__doc__)


    parser.add_option("-j", "--jobs",
      default=1,
      type="int",
      help="Number of processors to use when running testss (default: 1)",
    )

    parser.add_option("-p", '--prefix',
      default='',
      action="store",
      help="Specify the prefix for files name where output is saved. Default is '' - which mean no output is saved.",
    )

    parser.add_option('-q', "--quiet", action="store_true", dest="quiet", default=False,
      help="Suppress (mute) output to std::out."
    )

    parser.add_option('-Q', "--quiet_errors", action="store_true", dest="quiet_errors", default=False,
      help="Suppress (mute) even error output (also implies -q)"
    )

    (options, args) = parser.parse_args(args=args[1:])

    if options.quiet_errors:
        options.quiet = True

    global Options;  Options = options

    if len(args) > 0:
        tests = args
    else:
        sys.stderr("Must specify file name with command lines to run!\n")
        sys.exit(1)

    R = Runner(options.jobs, options.quiet, options.quiet_errors)
    R.run(args)



if __name__ == "__main__": main(sys.argv)
