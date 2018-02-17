# Licensed under the MIT License - see LICENSE.rst
"""
Launch a batch of hyak runs
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

submit_template = """#!/bin/bash
## --------------------------------------------------------
## NOTE: to submit jobs to Hyak use
##       qsub <script.sh>
##
## #PBS is a directive requesting job scheduling resources
## and ALL PBS directives must be at the top of the script,
## standard bash commands can follow afterwards.
## NOTE: Lines that begin with #PBS are commands to PBS,
##       and they are not comment lines.  To comment out
##       use "#  PBS".
## --------------------------------------------------------

## Job name
#PBS -N {job_name}

## DIRECTORY where this job is run
#PBS -d {run_dir}

## GROUP to run under
#PBS -W group_list=hyak-stf
## PBS -q bf

## NUMBER nodes, CPUs per node, and MEMORY
#PBS -l nodes=1:ppn=16,mem=20gb,feature=intel,feature=16core

## WALLTIME (defaults to 1 hour as the minimum, specify > 1 hour longer jobs)
#PBS -l walltime={walltime}

## LOG the (stderr and stdout) job output in the directory
#PBS -j oe -o {log_dir}

## EMAIL to send when job is aborted, begins, and terminates
#PBS -m abe -M {email}

## Some applications, particularly FORTRAN applications require
##  a larger than usual data stack size. Uncomment if your
##  application is exiting unexpectedly.
#ulimit -s unlimited

## Disable regcache
export MX_RCACHE=0

## --------------------------------------------------------
## END of PBS commands ... only BASH from here and below
## --------------------------------------------------------

## LOAD any appropriate environment modules and variables
module load gcc_4.4.7-impi_5.1.2

### Debugging information
### Include your job logs which contain output from the below commands
###  in any job-related help requests.
# Total Number of processors (cores) to be used by the job
HYAK_NPE=$(wc -l < $PBS_NODEFILE)
# Number of nodes used
HYAK_NNODES=$(uniq $PBS_NODEFILE | wc -l )
echo "**** Job Debugging Information ****"
echo "This job will run on $HYAK_NPE total CPUs on $HYAK_NNODES different nodes"
echo ""
echo "Node:CPUs Used"
uniq -c $PBS_NODEFILE | awk '{{print $2 ":" $1}}'
echo "SHARED LIBRARY CHECK"
echo "[skipped]"
echo "ENVIRONMENT VARIABLES"
set
echo "**********************************************"
### End Debugging information

# Prevent tasks from exceeding the total RAM of the node
# Requires HYAK_NPE and HYAK_NNODE or HYAK_TPN to be set.
HYAK_TPN=$((HYAK_NPE/HYAK_NNODES))
NODEMEM=`grep MemTotal /proc/meminfo | awk '{{print $2}}'`
NODEFREE=$((NODEMEM-2097152))
MEMPERTASK=$((NODEFREE/HYAK_TPN))
ulimit -v $MEMPERTASK

## --------------------------------------------------------
## RUN your specific applications/scripts/code here
## --------------------------------------------------------

## CHANGE directory to where job was submitted
## (careful, PBS defaults to user home directory)
cd $PBS_O_WORKDIR

echo "which python:"
which python
python archive_fit_hyak.py {planet_letter}
"""

def launch_hyak_run(planets, run_script, run_dir, job_name='libra',
                    log_dir='/gscratch/stf/bmmorris/libra/logs',
                    submit_script_dir='/gscratch/stf/bmmorris/libra/submit_scripts'):

    for planet_letter in planets:
        walltime = '04:00:00'
        email = 'bmmorris@uw.edu'

        submit_script_name = 'submit_script_{0}.sh'.format(planet_letter)

        submit_script = submit_template.format(job_name=job_name,
                                               run_dir=run_dir,
                                               log_dir=log_dir,
                                               walltime=walltime,
                                               email=email,
                                               run_script=run_script,
                                               planet_letter=planet_letter)

        submit_script_path = os.path.join(submit_script_dir, submit_script_name)
        with open(submit_script_path, 'w') as f:
            f.write(submit_script)
        os.system('qsub {0}'.format(submit_script_path))
    #
    # walltime = '04:00:00'
    # email = 'bmmorris@uw.edu'
    # with open('launchscript.sh', 'w') as w:
    #     for planet_letter in planets:
    #         w.write('python {0} {1}\n'.format(run_script, planet_letter))
    #
    # submit_script = submit_template.format(job_name=job_name,
    #                                        run_dir=run_dir,
    #                                        log_dir=log_dir,
    #                                        walltime=walltime,
    #                                        email=email,
    #                                        run_script=run_script,
    #                                        planet_letter=planet_letter)
    #
    # submit_script_path = os.path.join(submit_script_dir, "gnu_parallel_job.sh")
    # with open(submit_script_path, 'w') as f:
    #     f.write(submit_script)
    # os.system('qsub {0}'.format(submit_script_path))

launch_hyak_run(list('h'), '/usr/lusers/bmmorris/git/libra/archive_fit_hyak.py', '/usr/lusers/bmmorris/git/libra/')
