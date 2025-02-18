# load libraries

import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt

# pip install PyQt5
matplotlib.use('Qt5Agg')

# create file_path to data directory
data_dir = os.path.join(os.getcwd(), 'Week 02', 'data')
app_dir = os.path.join(os.getcwd(), 'Week 02', 'app')

# load data
books = pd.read_csv(os.path.join(data_dir, 'user_reviews.csv'))
