# Recommendations based on most reviewed books
# You will start by generating recommendations based on the most reviewed books.
# Although this approach is not personalized, it remains widely used and provides an opportunity to
# familiarize yourself with the Streamlit app located in the app directory.
#
# load libraries

import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt

# pip install PyQt5
matplotlib.use('Qt5Agg')


# current working directory
os.getcwd()

# create file_path to data directory

file_path = os.path.join(os.getcwd(), 'seminars/Week 01/')

# load data

books = pd.read_csv(file_path + '/data/user_reviews.csv')

books_unq = books.drop_duplicates(subset='ISBN')

# 1. Calculate the total reviews per book

total_reviews = books.groupby('ISBN').size().reset_index(name='count')

# 2. Save the recommendations
# Select the top 10 books based on the number of reviews. Save these recommendations in a file
# named recommendations-most-reviewed.csv. Then, update the app/recommendations directory by replacing the
# existing recommendations file with this new one. The current recommendations in the app require significant
# improvements. Ensure the file includes the following columns: ISBN;count.

top_10_books = total_reviews.sort_values(by='count', ascending=False).head(10)

# left join top10_books with books_unq to get the title of the books

# top_10_books = pd.merge(top_10_books, books_unq[['ISBN', 'Book-Title', 'Book-Author', 'Corrected-Author']],
#                         on='ISBN', how='left')

top_10_books.to_csv(file_path + 'app/recommendations/recommendations-most-reviewed.csv', sep=';', index=False)

# 3. Run the Streamlit app
# This might be your first experience running a Streamlit app. We've supplied you with boilerplate code to view
# your recommendations through a functional interface. As you progress, you may want to adjust some buttons or
# include additional metadata. Therefore, it's beneficial to familiarize yourself with the Streamlit documentation.
# For aspiring data scientists, the ability to create quick proofs-of-concept is essential.
#
# Install Streamlit
# Go to the terminal, navigate to the app folder and type streamlit run app.py

# cd "C:\Users\harmj\OneDrive\Documenten\MSc Data Science\courses\INFOMPPM\INFOMPPM_code\seminars\Week 01\app"
# streamlit run app.py

