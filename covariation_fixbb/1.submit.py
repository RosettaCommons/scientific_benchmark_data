#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# :noTabs=true:

# (c) Copyright Rosetta Commons Member Institutions.
# (c) This file is part of the Rosetta software suite and is made available under license.
# (c) The Rosetta software is developed by the contributing members of the Rosetta Commons.
# (c) For more information, see http://www.rosettacommons.org. Questions about this can be
# (c) addressed to University of Washington CoMotion, email: license@uw.edu.

## @file  _template_/1.submit.py
## @brief this script is part of <template> scientific test
## @author Sergey Lyskov

import os, sys, time
import benchmark

benchmark.load_variables()  # Python black magic: load all variables saved by previous script into globals
config = benchmark.config()

#==> EDIT HERE
testname    = "covariation_fixbb"

debug       = config['debug']
rosetta_dir = config['rosetta_dir']
working_dir = config['working_dir']
hpc_driver  = benchmark.hpc_driver()
extension   = benchmark.calculate_extension()

#==> EDIT HERE
command_line = '''
-database {rosetta_dir}/database
-in:file:s {rosetta_dir}/tests/scientific/data/{testname}/inputs/{target}.pdb
-in:file:native {rosetta_dir}/tests/scientific/data/{testname}/{target}.pdb
-nstruct {nstruct}
-parser:protocol {working_dir}/{testname}.xml
-out:file:scorefile {prefix}/{target}.score

–resfile ALLAA.res
–ex1
–ex2
–extrachi_cutoff 0
–linmem_ig 10
–no_his_his_pairE
–minimize_sidechains

-multiple_processes_writing_to_one_directory
-no_color
'''.replace('\n', ' ').replace('  ', ' ')

#==> EDIT HERE
nstruct = 2 if debug else 500

#==> EDIT HERE
targets = '1AQT 1BXY 1CTF 1CZP 1FB0 1FQT 1GN0 1GUU 1JL3 1MVO 1OAP 1PTF 1T8K 1TEN 1TZV 1U2H 1UCS 1UNQ 1WVN 1Z2U 2A0B 2BWF 2EVB 2H3L 2O37 2O9S 2PND 2PPN 2QLC 2X1B 2Z3V 2ZXJ 3BR8 3F04 3FYM 3GQS 3GVA 3I2Z 3JVL 3MQI'.split()
targets = targets[:2] if debug else targets

#print(f'extension: {extension}')
#print(f'command_line: {command_line}')
#print(f'config: {benchmark.config()}')
#print(hpc_driver)

hpc_logs = f'{working_dir}/hpc-logs'
if not os.path.exists(hpc_logs): os.makedirs(hpc_logs)
hpc_job_ids = []
for target in targets:
    prefix = f'{working_dir}/output/{target}'
    if not os.path.exists(prefix): os.makedirs(prefix)

    hpc_job_ids.append( hpc_driver.submit_hpc_job(
        name=f'{testname}-{target}',

        #==> EDIT HERE
        executable = f'{rosetta_dir}/source/bin/fixbb.{extension}',
        arguments = command_line.format_map(vars()),
        working_dir = prefix,
        jobs_to_queue = min(nstruct, 50),
        log_dir = hpc_logs,
        time=24,
        block=False)
    )


# if not debug:
#     hpc_driver.wait_until_complete(hpc_job_ids, silent=True)
#     time.sleep(64)  # waiting for NFS caching
hpc_driver.wait_until_complete(hpc_job_ids, silent=True)


'''
# Submitting PyRosetta job
hpc_job_ids.append( hpc_driver.submit_hpc_job(
    name=f'{testname}-{PyRosetta-example-job}',

    #==> EDIT HERE, substitute <MyPythonScript.py> and <script-arguments-if-any> with name of your PyRosetta Python script (located inside your test dir) and command line flags for it
    executable = config["python_virtual_environment"]["python"],
    arguments = '<MyPythonScript.py> <script-arguments-if-any>',
    working_dir = prefix,
    jobs_to_queue = min(nstruct, 50),
    log_dir = hpc_logs,
    time=24,
    block=False)
)
'''

#==> EDIT HERE
benchmark.save_variables('debug targets nstruct working_dir testname')  # Python black magic: save all listed variable to json file for next script use (save all variables if called without argument)
