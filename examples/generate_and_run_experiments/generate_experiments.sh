#!/bin/bash 


echo "Generate experiments ..."
python -c "import exputils
exputils.manage.generate_experiment_files()"

echo "Finished."

#$SHELL