import glob
import os
import subprocess
import time
import exputils
import numpy as np
from datetime import datetime
import fasteners

STATUS_FILE_EXTENSION = '.status'

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


def start_experiments(directory=None, start_scripts='*.sh', start_command='{}', parallel=True, is_chdir=True, verbose=False, post_start_wait_time=0):
    """

    :param directory: Directory in which the start scripts are searched.
    :param start_scripts: Filename of the start script file. Can include * to search for scripts.
    :param start_command:
    :param parallel: True if processes are started and executed in parallel. False if they are executed one after the other.
                     A integer number defines how many processes can run in parallel.
    :param is_chdir: Before starting a script, should the main process change to its working directory. (Default: True)
    :param verbose:
    :param post_start_wait_time:
    :return:
    """

    # TODO: remove the is_rerun argument, as it is not used anymore. This makes also changes in the commands necessary!

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

    if is_chdir:
        cwd = os.getcwd()

    # get all scripts
    all_scripts = get_scripts(directory=directory, start_scripts=start_scripts)

    ignored_scripts = []
    todo_scripts = []
    # check their initial status and write one for the scripts that will be started
    for script in all_scripts:

        # lock processing of the script, so that no other running experimentstarter is updating its status in parallel
        with get_script_lock(script):

            status = get_script_status(script)

            if status is None:
                update_script_status(script, 'todo')
                todo_scripts.append(script)

            elif status.lower() != 'finished':
                todo_scripts.append(script)

            else:
                ignored_scripts.append(script)

    # start all in parallel if wanted
    if n_parallel == np.inf:
        n_parallel = len(todo_scripts)

    # started process and their corresponding scripts
    started_processes = []
    started_scripts = []
    finished_processes_idxs = []

    next_todo_script_idx = 0
    n_active_processes = 0

    # run as long as there is an active process or we did not finish all processes yet
    while n_active_processes > 0 or next_todo_script_idx < len(todo_scripts):

        # start as many processes as parallel processes are allowed
        for i in range(n_parallel - n_active_processes):

            # stop starting processes when all scripts are started
            if next_todo_script_idx < len(todo_scripts):

                script = todo_scripts[next_todo_script_idx]
                next_todo_script_idx += 1

                # lock processing of the script, so that no other running experimentstarter is starting it in parallel
                with get_script_lock(script):

                    # check the script status, only start if needed
                    status = get_script_status(script)
                    if status is None or status.lower() == 'none' or status.lower() == 'todo' or status.lower() == 'error' or status.lower() == 'unfinished':

                        update_script_status(script, 'running')

                        # start
                        script_directory = os.path.dirname(script)

                        print('{} start {!r} (previous status: {}) ...'.format(datetime.now().strftime("%H:%M:%S"), script, status))

                        if is_chdir:
                            os.chdir(script_directory)
                            process = subprocess.Popen(start_command.format(os.path.join('.', os.path.basename(script))).split())
                            os.chdir(cwd)
                        else:
                            process = subprocess.Popen(start_command.format(script).split(), cwd=script_directory)

                        started_processes.append(process)
                        started_scripts.append(script)

                        if post_start_wait_time > 0:
                            time.sleep(post_start_wait_time)

                    else:
                        # do not start
                        ignored_scripts.append(script)

        # check the activity of the started processes
        n_active_processes = 0
        for p_idx, process in enumerate(started_processes):

            if p_idx not in finished_processes_idxs:

                if process.poll() is None:
                    n_active_processes += 1
                else:
                    finished_processes_idxs.append(p_idx)
                    if process.returncode == 0:
                        status = 'finished'
                    else:
                        status = 'error'
                    update_script_status(started_scripts[p_idx], status)

                    print('{} finished {!r} (status: {})'.format(datetime.now().strftime("%H:%M:%S"), started_scripts[p_idx], status))

        if n_active_processes > 0:
            time.sleep(0.5) # sleep half a second before checking again

    if verbose:
        if ignored_scripts:
            print('Ignored scripts:')
            for [script_path, status] in ignored_scripts:
                print('\t- {!r} (status: {})'.format(script_path, status))


def get_script_lock(script):
    return fasteners.InterProcessLock(script + '.lock')


def update_script_status(script, status):
    """
    Updates the status for the given script.

     :param script: Path to the script.
     :param status: New status.
    """

    status_file_path = script + STATUS_FILE_EXTENSION

    time_str = datetime.now().strftime("%H:%M:%S")

    with open(status_file_path, 'a+') as file:
        file.write( time_str + "\n" + status + "\n")


def get_scripts(directory=None, start_scripts='*.sh'):
    """
    Idenitfies all scripts.

     :param directory: Directory in which the start scripts are searched.
     :param start_scripts: Filename of the start script file. Can include * to search for scripts.

     :return: List of scripts (pathes).
    """

    if directory is None:
        directory = os.path.join('.', exputils.DEFAULT_EXPERIMENTS_DIRECTORY)

    # find all start scripts
    scripts = glob.iglob(os.path.join(directory, '**', start_scripts), recursive=True)

    scripts = list(scripts)

    return scripts


def get_script_status(script_file):
    """
    Returns the status of the given script file.

    :param script_file: Path to the script file.

    :return: Status as a string. ('error', 'running', 'finished'). None if not status exists.
    """
    status = None

    status_file_path = script_file + STATUS_FILE_EXTENSION

    if os.path.isfile(status_file_path):
        # read status
        with open(status_file_path, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) > 0:
                status = lines[-1]

    return status


def get_number_of_scripts_to_execute(directory=None, start_scripts='*.sh'):
    """
    Returns the number scripts that have to be executed

    :param directory: Directory in which the start scripts are searched.
    :param start_scripts: Filename of the start script file. Can include * to search for scripts.

    :return: Number of scripts that have to be executed (int).
    """

    scripts = get_scripts(directory=directory, start_scripts=start_scripts)

    n = 0
    for script in scripts:
        status = get_script_status(script)
        if status is None or status.lower() == 'todo' or status.lower() == 'none' or status.lower() == 'not started' or status.lower() == 'error' or status.lower() == 'unfinished':
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




