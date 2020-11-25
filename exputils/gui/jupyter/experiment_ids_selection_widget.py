from exputils.gui.jupyter.multi_selection_widget import MultiSelectionWidget
import exputils as eu

class ExperimentIDsSelectionWidget(MultiSelectionWidget):
    '''
    MultiSelectionWidget to select experiment ids in a experiment_data dict.
    '''

    @staticmethod
    def default_config():
        dc = eu.gui.jupyter.MultiSelectionWidget.default_config()

        dc.title = 'TITLE_LABELS'
        dc.title_labels = []

        dc.label_template = '<name> <description>'

        dc.title_label_template = '<short_name>'

        # if true, returns 'all' for selected_experiment_ids property if all experiments
        # are selected instead of a list of all experiments
        dc.is_return_all_string = False

        return dc

    def __init__(self, experiment_data, experiment_descriptions=None, config=None, **kwargs):
        self.config = eu.combine_dicts(kwargs, config, self.default_config())

        # get experiment ids
        self.experiment_ids = []

        # choice strings that are displayed to the user, can include ids, name, short_name, ...
        choices = []
        title_labels = []

        if experiment_descriptions is None:
            # detect ids from the experiment data
            for exp_id in experiment_data.keys():
                self.experiment_ids.append(exp_id)
                choices.append(exp_id)
                title_labels.append(exp_id)

        else:
            # detect ids from the experiment_descriptions
            for exp_descr in experiment_descriptions.values():
                self.experiment_ids.append(exp_descr['id'])

                choice_str = eu.misc.replace_str_from_dict(
                    self.config.label_template,
                    exp_descr,
                    pattern_format='<{}>')
                choices.append(choice_str)

                title_str = eu.misc.replace_str_from_dict(
                    self.config.title_label_template,
                    exp_descr,
                    pattern_format='<{}>')
                title_labels.append(title_str)

        if not self.config.title_labels:
            self.config.title_labels = title_labels

        super().__init__(choices, **self.config)

    @property
    def selected_experiment_ids(self):

        if self.config.is_return_all_string and self.is_all_selected:
            selected_choices = 'all'
        else:
            # find experiment_ids to selected choices
            selected_choices = []
            selected_choices_idxs = self.selected_choices_idxs
            for selected_idx in selected_choices_idxs:
                selected_choices.append(self.experiment_ids[selected_idx])

        return selected_choices

    @selected_experiment_ids.setter
    def selected_experiment_ids(self, selected_experiment_ids):

        if selected_experiment_ids == 'all':
            self.selected_choices = 'all'
        else:
            selected_choices_idxs = []
            for exp_id in selected_experiment_ids:
                # find exp_id in  self.experiment_ids
                selected_choices_idxs.append(self.experiment_ids.index(exp_id))

            self.selected_choices_idxs = selected_choices_idxs