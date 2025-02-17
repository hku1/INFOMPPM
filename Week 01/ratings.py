# You will create your first recommendations using average ratings. This method highlights books with high reader ratings,
# combining popularity with quality. You'll calculate each book's average rating and choose the top-rated ones for
# your recommendations.
#
# load libraries

import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt

# pip install PyQt5
matplotlib.use('Qt5Agg')

# create file_path to data directory
file_path = os.path.join(os.getcwd(), 'seminars/Week 01/')

# load data
books = pd.read_csv(file_path + '/data/user_reviews.csv')

# 1. Calculate the average ratings
# Calculate the average ratings and the number of reviews (count) for the books in your new dataset(s).

average_ratings = books.groupby('ISBN')['Book-Rating'].agg(['mean', 'count']).reset_index()

# 2. Save the recommendations
# Choose the top 10 based on ratings and save them as recommendations-ratings-avg.csv, replacing the existing file in
# the app directory. Ensure the file includes the columns: ISBN;mean. After you have saved it you can refresh Streamlit
# to see the results

top_10_avg_ratings = average_ratings.sort_values(by='mean', ascending=False).head(10)

top_10_avg_ratings.to_csv(file_path + 'app/recommendations/recommendations-ratings-avg.csv', sep=';', index=False)

# Recommendations based on weighted ratings
# Considering the drawbacks of using average ratings, you will now develop recommendations based on the weighted average
# for each book. Refer to the article Building a Recommendation System using weighted-average score to understand and
# apply this concept.
#
# 1. Calculate Weightage Average for Individual books average rating
# Determine the mean vote value (C) for the entire dataset.

# write function to calculate weighted average using the IMDB formula

def weighted_rating(x, m=None):
    ''''
    function to calculate weighted rating using the IMDB formula
    x: pandas series containing the count and mean rating of each book
    m: minimum number of votes required to be listed
    C: the mean vote value for the entire dataset
    '''

    # Calculate m based on the 80th percentile of x['count'] if not provided
    if m is None:
        m = x['count'].quantile(0.8)

    # calculate C
    C = x['mean'].mean()

    # calculate the weighted rating and append to x dataframe named weight
    x['weight'] = x.apply(lambda x: (x['count'] / (x['count'] + m) * x['mean']) + (m / (m + x['count']) * C), axis=1)

    return x

# calculate weighted ratings

weighted_ratings = weighted_rating(average_ratings)

# 2. Save the recommendations
# Choose the top 10 books based on their weighted ratings and save these recommendations as recommendations-ratings-weight.csv.
#
# Then, update the app directory by replacing the existing file. Ensure the file includes the columns: ISBN;weight.

top_10_weighted_ratings = weighted_ratings.sort_values(by='weight', ascending=False).head(10)

top_10_weighted_ratings.to_csv(file_path + 'app/recommendations/recommendations-ratings-weight.csv', sep=';', index=False)

# 2. Count the combinations of books reviewed together

# Create combinations of books reviewed by same user with permutations and count how often each combination occurs. This process might be time-consuming,
# depending on your initial data exploration.

from itertools import permutations














