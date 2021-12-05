source ~/opt/anaconda3/etc/profile.d/conda.sh
conda deactivate
conda env remove -n ace-distance
conda env create -f environment.yml