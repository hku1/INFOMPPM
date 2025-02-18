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
data_dir = os.path.join(os.getcwd(), 'Week 01', 'data')
app_dir = os.path.join(os.getcwd(), 'Week 01', 'app')

# load data
books = pd.read_csv(os.path.join(data_dir, 'user_reviews.csv'))

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

# note: for demo purposes, we will use a subset of the data, as the full dataset is too large to process in a reasonable amount of time
# keep only users with 10 or more book ratings and remove ratins with 0

books = books[books['Book-Rating'] != 0]

x = books['ISBN'].value_counts() >= 20
idx = x[x].index
ratings = books[books['ISBN'].isin(idx)]

x = ratings['User-ID'].value_counts() >= 10
idx = x[x].index
books = ratings[ratings['User-ID'].isin(idx)]

books.shape

from itertools import permutations

def create_combinations(x):
    ''''
    function to create combinations of books reviewed by the same user
    x: pandas series containing the ISBNs reviewed by a user
    '''

    # create combinations of 2 books
    combinations = pd.DataFrame(list(permutations(x.values, 2)), columns=['book_a', 'book_b'])

    return combinations

# use the function to create combinations

book_combinations = books.groupby('User-ID')['ISBN'].apply(create_combinations)

book_combinations = book_combinations.reset_index(drop=True)

# count the combinations

combinations_counts = book_combinations.groupby(['book_a', 'book_b']).size()
combinations_counts = combinations_counts.to_frame(name='count').reset_index()

# keep top 10 and write to csv file

combinations_counts = combinations_counts.sort_values('count', ascending=False)

# only select top 10 per combination

df1 = combinations_counts.sort_values('count', ascending=False).groupby('book_a').head(10)

df1.to_csv(os.path.join(app_dir, 'recommendations-seeded-freq.csv'), index=False, sep=';')


# Recommendations based on Frequently Reviewed Together (association rules)
# For the final segment of this assignment, refer to section 5.4 of the Practical Recommender Systems book (pages 113-127). After reading, download the code provided by the book and focus on the association_rules_calculator.py in the builder directory. Your task is to adapt this code for use in this notebook, translating its steps into a format suitable for our environment. Here's a simplified outline based on the source code:
#
# The steps found in the source code are:
#
# Load the data
# Generate transactions or, in our case reviews
# Calculate the Support Confidence
# Save the results

df_users = books.groupby('User-ID')['ISBN'].count().reset_index(name='counts')
users = list(df_users[(df_users['counts'] > 100) & (df_users['counts'] < 200)]['User-ID'])

# books.loc[books['User-ID'].isin(users)]

# 2. Generating the reviews
# In this context, transactions are the reviews. You need to compile a list of lists, where each inner list contains
# reviews that are related, similar to how shopping lists are grouped in the example: [['eggs','milk','bread'], ['bacon', 'bread'], [...], [...]]


df_reviews = books.groupby('User-ID')['ISBN'].apply(list)
reviewed = df_reviews.values.tolist()

# 3. Calculate the Support Confidence
# This requires some puzzling, but looking at the source code will give you a clear idea. You can reuse the subroutines in the source code and pass along the list containing the reviews belonging together. Play around with the minimum support parameter. Too strict will result in fewer associations.


# this code originated from the book Practical Recommender System.
# Some minor tweaks to make it work with the current dataset.

from collections import defaultdict
from itertools import combinations
from datetime import datetime

def calculate_itemsets_one(reviewed, min_sup=0.01):
    N = len(reviewed)
    print(N)
    temp = defaultdict(int)
    one_itemsets = dict()

    for items in reviewed:
        for item in items:
            inx = frozenset({item})
            temp[inx] += 1

    print("temp:")
    i = 0
    # remove all items that is not supported.
    for key, itemset in temp.items():
        #print(f"{key}, {itemset}, {min_sup}, {min_sup * N}")
        if itemset > min_sup * N:
            i = i + 1
            one_itemsets[key] = itemset
    print(i)
    return one_itemsets

def calculate_itemsets_two(reviewed, one_itemsets):
    two_itemsets = defaultdict(int)

    for items in reviewed:
        items = list(set(items))  # remove duplications

        if (len(items) > 2):
            for perm in combinations(items, 2):
                if has_support(perm, one_itemsets):
                    two_itemsets[frozenset(perm)] += 1
        elif len(items) == 2:
            if has_support(items, one_itemsets):
                two_itemsets[frozenset(items)] += 1
    return two_itemsets

def calculate_association_rules(one_itemsets, two_itemsets, N):
    timestamp = datetime.now()

    rules = []
    for source, source_freq in one_itemsets.items():
        for key, group_freq in two_itemsets.items():
            if source.issubset(key):
                target = key.difference(source)
                support = group_freq / N
                confidence = group_freq / source_freq
                rules.append((timestamp, next(iter(source)), next(iter(target)),
                              confidence, support))
    return rules

def has_support(perm, one_itemsets):
  return frozenset({perm[0]}) in one_itemsets and \
    frozenset({perm[1]}) in one_itemsets


min_sup = 0.01
N = len(reviewed)

one_itemsets = calculate_itemsets_one(reviewed, min_sup)
two_itemsets = calculate_itemsets_two(reviewed, one_itemsets)
rules = calculate_association_rules(one_itemsets, two_itemsets, N)

# check how many associations are made
len(rules)






