import glob
import os
import subprocess
import time
import exputils
import numpy as np

def start_slurm_experiments(directory=None, start_scripts='*.slurm', is_parallel=True, verbose=False, post_start_wait_time=0):

    return start_experiments(directory=directory,
                             start_scripts=start_scripts,
                             start_command='sbatch {}',
                             parallel=is_parallel,
                             is_chdir = True,  # added, otherwise the sbatch does not work
                             verbose=verbose,
                             post_start_wait_time=post_start_wait_time)


def start_torque_experiments(directory=None, start_scripts='*.torque', is_parallel=True, verbose=False, post_start_wait_time=0):

    return start_experiments(directory=directory,
                             start_scripts=start_scripts,
                             start_command='qsub {}',
                             parallel=is_parallel,
                             is_chdir = True,  # added, otherwise the sbatch does not work
                             verbose=verbose,
                             post_start_wait_time=post_start_wait_time)


def start_experiments(directory=None, start_scripts='*.sh', start_command='{}', parallel=True, is_chdir=False, verbose=False, post_start_wait_time=0, is_rerun=False):
    """

    :param directory: Directory in which the start scripts are searched.
    :param start_scripts: Filename of the start script file. Can include * to search for scripts.
    :param start_command:
    :param parallel: True if processes are started and executed in parallel. False if they are executed one after the other.
                     A integer number defines how many processes can run in parallel.
    :param is_chdir:
    :param verbose:
    :param post_start_wait_time:
    :param is_rerun: Should finished scripts be rerun. (default: False)
    :return:
    """

    # TODO: do not restart experiments that have been added as jobs but have not been started yet

    if directory is None:
        directory = os.path.join('.', exputils.DEFAULT_EXPERIMENTS_DIRECTORY)

    # handle number of parallel processes
    if isinstance(parallel, bool):
        if parallel:
            n_parallel = np.inf
        else:
            n_parallel = 1
    elif isinstance(parallel, int):
        if parallel <= 0:
            raise ValueError('Number of parallel processes must be larger 0!')
        else:
            n_parallel = parallel
    else:
        raise ValueError('Argument \'parallel\' must be either a bool or an integer number!')

    # get the scripts and their status
    scripts = get_scripts(directory=directory, start_scripts=start_scripts)

    # the processes that are started for each script
    processes = []

    ignored_scripts = []

    if is_chdir:
        cwd = os.getcwd()

    # start every found script
    for [script_path, status] in scripts:

        if is_rerun or (status is None or status.lower() == 'none' or status.lower() == 'not started' or status.lower() == 'error' or status.lower() == 'unfinished'):
            # start the script

            if verbose:
                print('start {!r} (status: {}) ...'.format(script_path, status))

            script_directory = os.path.dirname(script_path)

            if is_chdir:
                os.chdir(script_directory)
                process = subprocess.Popen(start_command.format(os.path.join('.', os.path.basename(script_path))).split())
            else:
                process = subprocess.Popen(start_command.format(script_path).split(), cwd=script_directory)

            # if not parallel, then wait until current process is finished
            if n_parallel == 1:
                process.wait()
            else:
                # parallel is a number that tell how many process can be open at the same time

                is_wait = True
                while is_wait:

                    # detect number of active processes
                    n_active_proceeses = 0
                    for p in processes:
                        if p.poll() is None:
                            n_active_proceeses += 1

                    # wait if the maximum number of processes are currently running
                    is_wait = n_active_proceeses >= parallel

                    if is_wait:
                        time.sleep(0.5) # sleep half a second before checking again

            if post_start_wait_time > 0:
                time.sleep(post_start_wait_time)

            processes.append(process)

            if is_chdir:
                os.chdir(cwd)

        else:
            ignored_scripts.append((script_path, status))

    if verbose:

        if ignored_scripts:
            print('Ignored scripts:')

            for [script_path, status] in ignored_scripts:
                print('\t- {!r} (status: {})'.format(script_path, status))

    # wait until all processes are finished
    for process in processes:
        process.wait()


def get_scripts(directory=None, start_scripts='*.sh'):
    """
    Idenitfies all scripts and their status.

     :param directory: Directory in which the start scripts are searched.
     :param start_scripts: Filename of the start script file. Can include * to search for scripts.

     :return: List of tuples with (script_path, script_status)
    """

    if directory is None:
        directory = os.path.join('.', exputils.DEFAULT_EXPERIMENTS_DIRECTORY)

    # holds tuples of (startscript_path, status)
    scripts = []

    # find all start scripts
    files = glob.iglob(os.path.join(directory, '**', start_scripts), recursive=True)

    # find if they have a job status
    for file in files:

        status_file_path = file + '.status'

        if os.path.isfile(status_file_path):
            # read status
            with open(status_file_path, 'r') as f:
                lines = f.read().splitlines()
                if len(lines) > 0:
                    status = lines[-1]
                else:
                    status = 'none'
        else:
            status = 'none'

        scripts.append((file, status))

    return scripts


def get_number_of_scripts_to_execute(directory=None, start_scripts='*.sh'):
    """
    Returns the number scripts that have to be executed

    :param directory: Directory in which the start scripts are searched.
    :param start_scripts: Filename of the start script file. Can include * to search for scripts.

    :return: Number of scripts that have to be executed (int).
    """

    scripts = get_scripts(directory=directory, start_scripts=start_scripts)

    n = 0
    for (_, status) in scripts:
        if status is None or status.lower() == 'none' or status.lower() == 'not started' or status.lower() == 'error' or status.lower() == 'unfinished':
            n += 1

    return n


def get_number_of_scripts(directory=None, start_scripts='*.sh'):
    """
    Returns the number scripts of all scripts regardless of their run status.

    :param directory: Directory in which the start scripts are searched.
    :param start_scripts: Filename of the start script file. Can include * to search for scripts.

    :return: Number of scripts (int).
    """

    scripts = get_scripts(directory=directory, start_scripts=start_scripts)
    return len(scripts)




