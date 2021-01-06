import numpy as np


def get_ordered_experiment_ids_from_descriptions(experiment_descriptions):
    '''
    Returns a sorted list of experiment ids according to the order in the experiment descriptions.
    '''
    if not experiment_descriptions:
        return []

    experiment_descriptions_values = list(experiment_descriptions.values())
    order = [descr['order'] for descr in experiment_descriptions_values]
    sorted_experiment_ids = [experiment_descriptions_values[idx]['id'] for idx in np.argsort(order)]
    return sorted_experiment_ids