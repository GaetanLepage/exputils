import exputils as eu
import dill
import os
from glob import glob

DILL_FILE_EXTENSION = 'dill'

def save_dill(obj, file_path):

    if not file_path.endswith('.' + DILL_FILE_EXTENSION):
        file_path += '.' + DILL_FILE_EXTENSION

    eu.io.makedirs_for_file(file_path)
    with open(file_path, 'wb') as fh:
        dill.dump(obj, fh)


def load_dill(file_path):
    with open(file_path, 'rb') as fh:
        obj = dill.load(fh)
    return obj


def load_dill_files(directory):
    '''Loads data from all dill files in a given directory.'''

    if not os.path.isdir(directory):
        raise FileNotFoundError('Directory {!r} does not exist!'.format(directory))

    data_dict = eu.AttrDict()

    for file in glob(os.path.join(directory, '*.' + DILL_FILE_EXTENSION)):
        data_name = os.path.splitext(os.path.basename(file))[0]
        data = load_dill(file)
        data_dict[data_name] = data

    return data_dict