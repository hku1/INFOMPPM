# Import necessary libraries
import streamlit as st
import pandas as pd
import template as t 

# Configure the layout of the Streamlit page to use a wide format for more space
st.set_page_config(layout="wide")

# Load the dataset containing book information
# Note: Adjust the file path to where your BX-Books.csv is located.
df_books = pd.read_csv('../data/BX-Books.csv', sep=';', encoding='latin-1', low_memory=False)


# Initialize a session state for storing the current book's ISBN if not already present
if 'ISBN' not in st.session_state:
  st.session_state['ISBN'] = '0385504209'  # Default ISBN to kickstart the app

# Filter the dataset to only include the selected book using the stored ISBN
df_book = df_books[df_books['ISBN'] == st.session_state['ISBN']]

# Create two columns for displaying the book cover and information side by side
cover, info = st.columns([2, 3])

# Display the book cover in the 'cover' column
with cover:
  st.image(df_book['Image-URL-L'].iloc[0], caption="Book Cover")

# Display the book's title, author, and publication details in the 'info' column
with info:
  st.title(df_book['Book-Title'].iloc[0])
  st.markdown(f"**Author:** {df_book['Book-Author'].iloc[0]}")
  st.caption(f"{df_book['Year-Of-Publication'].iloc[0]} | {df_book['Publisher'].iloc[0]}")

# Display recommendations based on the most reviewed books
st.subheader('Recommendations based on most reviewed')
df_most_reviewed = pd.read_csv('recommendations/recommendations-most-reviewed.csv', sep=';', encoding='latin-1', dtype=object)
df_most_reviewed = df_most_reviewed.merge(df_books, on='ISBN')
t.recommendations(df_most_reviewed)

# Display recommendations based on average rating
st.subheader('Recommendations based on average rating')
df_avg_rating = pd.read_csv('recommendations/recommendations-ratings-avg.csv', sep=';', encoding='latin-1', dtype=object)
df_avg_rating = df_avg_rating.merge(df_books, on='ISBN')
t.recommendations(df_avg_rating)

# Display recommendations based on weighted rating
st.subheader('Recommendations based on weighted rating')
df_weighted_rating = pd.read_csv('recommendations/recommendations-ratings-weight.csv', sep=';', encoding='latin-1', dtype=object)
df_weighted_rating = df_weighted_rating.merge(df_books, on='ISBN')
t.recommendations(df_weighted_rating)

st.subheader('Recommendations based on Frequently Reviewed Together (frequency)')
df = pd.read_csv('recommendations/recommendations-seeded-freq.csv', sep=';', encoding='latin-1', dtype=object)
isbn = st.session_state['ISBN']
df_recommendations = df[df['book_a'] == isbn].sort_values(by='count', ascending=False)
df_recommendations = df_recommendations.rename(columns={"book_b": "ISBN"})
df_recommendations = df_recommendations.merge(df_books, on='ISBN')
t.recommendations(df_recommendations)

st.subheader('Recommendations based on Frequently Reviewed Together (associations)')
df = pd.read_csv('recommendations/recommendations-seeded-associations.csv', sep=';', encoding='latin-1', dtype=object)
isbn = st.session_state['ISBN']
df_recommendations = df[df['source'] == isbn].sort_values(by='confidence', ascending=False).head(10)
df_recommendations = df_recommendations.rename(columns={"target": "ISBN"})
df_recommendations = df_recommendations.merge(df_books, on='ISBN')
t.recommendations(df_recommendations)