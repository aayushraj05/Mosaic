# env_setup.py
# Import this as FIRST import in every file
# Sets environment before any torch/numpy loads

import os

os.environ['OPENBLAS_NUM_THREADS']  = '1'
os.environ['OMP_NUM_THREADS']       = '1'
os.environ['MKL_NUM_THREADS']       = '1'
os.environ['NUMEXPR_NUM_THREADS']   = '1'
os.environ['VECLIB_MAXIMUM_THREADS']= '1'
os.environ['YOLO_VERBOSE']          = 'False'
os.environ['TF_CPP_MIN_LOG_LEVEL']  = '3'
