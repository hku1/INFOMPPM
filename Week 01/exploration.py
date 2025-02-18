# Data exploration and preparation
# In this notebook, we'll examine the dataset and create a subset of it for further analysis. The dataset
# was relatively clean when downloaded, though we addressed some problematic delimiter issues for you.
# If you're interested in tackling these issues firsthand, the original dataset is available at the Book-Crossing Dataset.

# load libraries

import pandas as pd
import os
from collections import defaultdict, Counter
from rapidfuzz import fuzz
import pickle
import matplotlib
import matplotlib.pyplot as plt

# pip install PyQt5
matplotlib.use('Qt5Agg')

# current working directory
os.getcwd()

# create file_path to data directory

file_path = os.path.join(os.getcwd(), 'seminars/Week 01/data')

# load data

books = pd.read_csv(file_path + '/BX-Books.csv', sep=';', encoding='latin-1')
ratings = pd.read_csv(file_path + '/BX-Book-Ratings.csv', sep=';', encoding='latin-1')
users = pd.read_csv(file_path + '/BX-Users.csv', sep=';', encoding='latin-1')

# inspect data

books.head()
books.info()

ratings.head()
ratings.info()

users.head()
users.info()

# 2. Cleaning the data
# Ensure that all reviews are linked to a book. Investigate whether there are any reviews that lack a corresponding
# book or user. Verify the accuracy of author names and identify any anomalies, such as users who have submitted an
# unusually high number of reviews. Describe the process you followed to clean the data.


reviews_with_books = ratings.merge(books, how='left', on='ISBN')
missing_books_reviews = reviews_with_books[reviews_with_books['Book-Title'].isnull()]

reviews_with_users = ratings.merge(users, how='left', on='User-ID')
missing_users_reviews = reviews_with_users[reviews_with_users['Location'].isnull()]

# remove rows with missing books
reviews_with_books.dropna(subset=['Book-Title'], inplace=True)

# merge with users

reviews_users = reviews_with_books.merge(users, how='left', on='User-ID')


# Verify the accuracy of author names and identify any anomalies

len(set(reviews_users['Book-Author'])) # number of unique entries in the author column

# Preprocess author names to identify potential misspellings

def preprocess_name(name):
    """Preprocess a name by stripping whitespace, converting to lowercase, and removing unwanted characters."""
    return name.strip().lower().replace('"', '').replace(',', '')

def cluster_names(name_list, similarity_threshold=80):
    """
    Groups similar names and identifies potential misspellings.

    :param name_list: List of names (including correct and misspelled versions).
    :param similarity_threshold: Similarity ratio below which names are considered misspelled.
    :return: Dictionary with correct names as keys and lists of misspellings as values.
    """
    # Convert to string, drop NaN values, and remove non-string entries
    name_series = pd.Series(name_list).dropna().astype(str)

    if name_series.empty:
        return {}

    # Preprocess names
    name_list = [preprocess_name(name) for name in name_series]

    clusters = defaultdict(list)
    unique_names = set(name_list)

    # Step 1: Group names into clusters based on similarity
    for name in unique_names:
        # Find the best matching cluster
        best_match = None
        highest_similarity = 0
        for key in clusters.keys():
            similarity = fuzz.ratio(name, key)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = key

        # If a suitable cluster is found, add the name to it
        if highest_similarity > similarity_threshold:
            clusters[best_match].append(name)
        else:
            clusters[name].append(name)

    # Step 2: Determine the most common spelling in each cluster
    misspelled_names = {}
    for cluster in clusters.values():
        if len(cluster) > 1:  # optionally filteron cluster size
            # Count occurrences in the original list to determine the correct name
            cluster_counts = Counter(name_list)
            correct_name = max(cluster, key=lambda x: cluster_counts[x])
            misspellings = [name for name in cluster if name != correct_name]

            if misspellings:
                misspelled_names[correct_name] = misspellings

    # Capitalize every word in the correct names
    titled_misspelled_names = {correct_name.title(): misspellings for correct_name, misspellings in misspelled_names.items()}

    return titled_misspelled_names


def cluster_names_2(name_list, similarity_threshold=80):
    """
    Groups similar names and identifies potential misspellings.

    :param name_list: List of names (including correct and misspelled versions).
    :param similarity_threshold: Similarity ratio below which names are considered misspelled.
    :return: Dictionary with correct names as keys and lists of misspellings as values.
    """
    # Convert to string, drop NaN values, and remove non-string entries
    name_series = pd.Series(name_list).dropna().astype(str)

    if name_series.empty:
        return {}

    # Preprocess names
    name_list = [preprocess_name(name) for name in name_series]

    clusters = defaultdict(list)
    unique_names = set(name_list)

    # Step 1: Group names into clusters based on similarity
    # Block names by their first letter to reduce comparisons
    blocked_names = defaultdict(list)
    for name in unique_names:
        blocked_names[name[0]].append(name)

    for block in blocked_names.values():
        for name in block:
            # Find the best matching cluster within the block
            best_match = None
            highest_similarity = 0
            for key in clusters.keys():
                if key[0] != name[0]:
                    continue  # Skip keys not in the same block
                similarity = fuzz.ratio(name, key)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_match = key

            # If a suitable cluster is found, add the name to it
            if highest_similarity > similarity_threshold:
                clusters[best_match].append(name)
            else:
                clusters[name].append(name)

    # Step 2: Determine the most common spelling in each cluster
    misspelled_names = {}
    cluster_counts = Counter(name_list)  # Count occurrences once for efficiency
    for cluster in clusters.values():
        if len(cluster) > 1:  # optionally filter on cluster size
            # Determine the correct name
            correct_name = max(cluster, key=lambda x: cluster_counts[x])
            misspellings = [name for name in cluster if name != correct_name]

            if misspellings:
                misspelled_names[correct_name] = misspellings

    # Capitalize every word in the correct names
    titled_misspelled_names = {correct_name.title(): misspellings for correct_name, misspellings in misspelled_names.items()}

    return titled_misspelled_names

# Example usage
names = [
    "Jonathan", "Jonatan", "Johnathan", "Jonnathan", "Jonathan", "Jonathon", "Jonthan",
    "Anna", "Ana", "Annah", "Anna", "Anne", "Anna",
    "Samuel", "Samual", "Sammuel", "Samwell", "Samuel",
    None, 123, float('nan'), "123", " jonathan ", "ANNA", '"Samuel"', 'Sam,uel'
]

misspelled_test = cluster_names(names, similarity_threshold=50)

# Print results
for correct_name, misspellings in misspelled_test.items():
    print(f"Correct: {correct_name}, Misspellings: {misspellings}")


misspelled_authors = cluster_names_2(reviews_users['Book-Author'], similarity_threshold=90)

for correct_name, misspellings in misspelled_authors.items():
    print(f"Correct: {correct_name}, Misspellings: {misspellings}")

# save the dictionary in the data directory as pickle, for later use

# with open(file_path + '/misspelled_authors.pkl', 'wb') as f:
#     pickle.dump(misspelled_authors, f)

# load the dictionary from the pickle file

with open(file_path + '/misspelled_authors.pkl', 'rb') as f:
    misspelled_authors = pickle.load(f)

# add a column with the correct author name to reviews_users dataframe

def correct_author_name(author, misspelled_dict):
    """Correct author name based on the provided dictionary."""
    # Convert the author to lowercase for comparison
    author_lower = author.lower()

    # Iterate over the dictionary items
    for correct_name, misspelled_names in misspelled_dict.items():
        # Check if the provided author matches any misspelled name
        if author_lower in [name for name in misspelled_names]:
            return correct_name

    # If the author's name is in all caps, convert to title case
    if author.isupper():
        return author.title()

    # Return the original author if no match is found
    return author

reviews_users['Corrected-Author'] = reviews_users['Book-Author'].apply(lambda x: correct_author_name(x, misspelled_authors))

chk1 = reviews_users[(reviews_users['Book-Author'] == 'Ernest Heminway')]
chk2 = reviews_users[(reviews_users['Book-Author'] == 'Helen Hoover Santmyer')]

## find  users who have submitted an unusually high number of reviews

user_review_counts = reviews_users['User-ID'].value_counts()
user_review_counts.describe()

# plot histogram of user review counts

user_review_counts.hist(bins=100)
plt.show()

# create dataframe of users with more than 15 reviews

prolific_users = user_review_counts[user_review_counts > 15].reset_index() #dataset is 4-week crawl, i.e. 15 book ratings is 1 book every 2 days

# Hence, we discarded all books missing taxonomic descriptions, along with all ratings referring to them.
# Next, we also removed book titles with fewer than 20 overall mentions.
# Only community members with at least five ratings each were kept.

# remove books with fewer than 20 overall mentions in original dataset

book_counts = reviews_users['Book-Title'].value_counts()
popular_books = book_counts[book_counts >= 20].index
reviews_users = reviews_users[reviews_users['Book-Title'].isin(popular_books)]

# remove users with fewer than 5 ratings

user_review_counts = reviews_users['User-ID'].value_counts()
active_users = user_review_counts[user_review_counts >= 5].index
reviews_users = reviews_users[reviews_users['User-ID'].isin(active_users)]

# calculate the fraction of books with a rating of 0

zero_ratings = reviews_users['Book-Rating'].value_counts().get(0, 0)

fraction_zero = zero_ratings / len(reviews_users)

# reduce # of reviews for demo purposes

books = books[books['Book-Rating'] != 0]

x = books['ISBN'].value_counts() >= 20
idx = x[x].index
ratings = books[books['ISBN'].isin(idx)]

x = ratings['User-ID'].value_counts() >= 10
idx = x[x].index
books = ratings[ratings['User-ID'].isin(idx)]

# Examine the BX-Books.csv file specifically for the book Robots and Empire by Isaac Asimov.
# Identify any issues you come across. Would you address these issues?

rbts_empire = books[(books['Book-Title'] == 'Robots and Empire') & (books['Book-Author'] == 'Isaac Asimov')]

# write user_reviews to csv

reviews_users.to_csv(data_dir + '/user_reviews.csv', index=False)

# books.to_csv(data_dir + '/user_reviews.csv', index=False)