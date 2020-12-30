import os

def makedirs(path):
    '''
    Creates the directories of the given path if they do not exist.

    :param path:  Directory path.
    :return:
    '''

    if not os.path.isdir(path):
        os.makedirs(path)


def makedirs_for_file(filepath):
    '''
    Creates the directory of the given filepath if it does not exist.

    :param filepath: Filepath for which the directories it points to are created.
    :return:
    '''

    directory_path, _ = os.path.split(filepath)
    makedirs(directory_path)
