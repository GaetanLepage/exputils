Current version: 0.3.4 (08/03/2023)

# Introduction

Experiment Utilities (exputils) contains various tools for the management of scientific experiments and their experimental data.
It is especially designed to handle experimental repetitions, including to run different repetitions, to effectively store and load data for them, and to visualize their results.  
 
Main features:
* Easy definition of default configurations using nested python dictionaries.
* Setup of experimental configuration parameters using an ODF file.
* Running of experiments and their repetitions in parallel.
* Logging of experimental data (numpy, json).
* Loading and filtering of experimental data.
* Interactive Jupyter widgets to load, select and plot data as line, box and bar plots.  

# <a name="requirements"></a>Requirements

Developed and tested for Python 3.6 to 3.9 on Linux (Ubuntu 18.04).

Depends on the following python packages which will be automatically installed during the setup:
* numpy >= 1.19.5
* six >= 1.15.0
* ipywidgets >= 7.5.1,<= 7.6.5
* qgrid >= 1.3.1
* plotly >= 4.13.0
* cloudpickle >= 1.6.0
* dill >= 0.3.3
* odfpy >= 1.4.1
* tabulate >= 0.8.9
* scipy >= 1.5.4
* tensorboard >= 1.15.0
* fasteners >= 0.18
* pyyaml >= 6.0


# <a name="setup"></a>Setup

__1) Exputils__

*Via PIP*

    pip install experiment-utilities

*From Source*

Clone the repository via git and install via pip:
    
    git clone git@gitlab.inria.fr:creinke/exputils.git .
    pip install ./exputils

(To install the library as a developer so that changes to its source code are directly usable in other projects:
`pip install -e ./exputils`)


__2) Jupiter Notebook__

For using the exputils GUIs for loading and plotting of data in Jupyter Notebook, the *qgrid* widget must be activated.
(Note: The GUI is currently only tested for Jupyter notebooks. For Jupyterlab, other installation procedures are necessary.)
Activate *qgrid* with:

    jupyter nbextension enable --py --sys-prefix qgrid

It is recommended to use the [Jupyter Notebooks Extensions](https://github.com/ipython-contrib/jupyter_contrib_nbextensions) to allow folding of code and headlines.
This makes the notebooks more readable.
Install the extensions with:

    pip install jupyter_contrib_nbextensions 
    jupyter contrib nbextension install --user

# <a name="overview"></a>Overview

Besides the exputils library (the python package) the project also contains example code and unit tests. 
It is recommended to look at these items to learn about the usage of the exputils components. 

The exputils package has the following structure:
 - **manage**: Managing of experiments. Generation of code for experiments and repetitions from ODS configurations and source templates. Running of experiments and repetitions (can be used to run experiments on clusters.)   
 - **data**: Logging and loading of experimental data including filtering of data. 
 - **gui**: GUI components for Jupyter to load and plot experimental data.
 - **misc**: Miscellaneous helper functions.
 - **io**: Input-output functions to save and load data of various formats, including numpy and json.

Experiments are stored in a specific folder structure which allows to save and load experimental data in a structured manner.
Please note that  it represents a default structure which can be adapted if required.
Elements in brackets (\<custom name>\) can have custom names.   
Folder structure:
 * **\<main\>** folder: Holds several experimental campaigns. A campaign holds experiments of the same kind but with different parameters.
    * **analyze** folder: Scripts such as Jupyter notebooks to analyze the different experimental campaigns in this main-folder.
    * **\<experimental campaign\>** folders:
        * **analyze** folder: Scripts such as Jupyter notebooks to analyze the different experiments in this experimental campaign. 
        * **experiment_configurations.ods** file: ODS file that contains the configuration parameters of the different experiments in this campaign.
        * **src** folder: Holds code templates of the experiments.
            * **\<repetition code\>** folders: Code templates that are used under the repetition folders of th experiments. These contain the acutal experimental code that should be run.
            * **\<experiment code\>** folders: Code templates that are used under the experiment folder of the experiment. These contain usually code to compute statistics over all repetitions of an experiment.
        * **generate_code.sh** file: Script file that generates the experimental code under the **experiments** folder using the configuration in the **experiment_configurations.ods** file and the code under the **src** folder.               
        * **experiments** folder: Contains generated code for experiments and the collected experimental data.
            * **experiment_{id}** folders:
                * **repetition_{id}** folders:
                    * **data** folder: Experimental data for the single repetitions, such as logs.
                    * code files: Generated code and resource files.
                * **data** folder: Experimental data for the whole experiment, e.g. statistics that are calculated over all repetitions.   
                * **\<code\>** files: Generated code and resource files.
        * **\<run scripts\>.sh** files: Various shell scripts to run experiments and calculate statistics locally or on clusters.

# <a name="team-members"></a>Development Team

__Main__

* [Chris Reinke](http:www.scirei.net): <chris.reinke@inria.fr>

__Contributors__

 * Gaetan Lepage