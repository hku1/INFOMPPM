import streamlit as st
import pandas as pd
import template as t
import itertools

st.set_page_config(layout="wide")

# load the dataset with the ratings
df_ratings = pd.read_csv('../data/BX-Book-Ratings-Subset.csv', sep=';', encoding='latin-1', low_memory=False)
df_books = pd.read_csv('../data/BX-Books.csv', sep=';', encoding='latin-1', low_memory=False)


# initialize a session state with a user
if 'User-ID' not in st.session_state:
  st.session_state['User-ID'] = 98783

# which user do you want to see?
st.session_state['User-ID'] = 98783

def get_jaccard_recommendations(id):
  users = df_ratings.groupby('User-ID')['ISBN'].apply(list)
  new_content = []
  similar_users = []
  
  for user, value in users.items():
    a = set(users[id])
    b = set(users[user])
    
    # calculate jaccard
    distance = 1 - float(len(a.intersection(b))) / len(a.union(b))
    
    # tweak this parameter. Closer to 0.0 is more the same. 0.0 is the user.
    if distance < 0.8 and distance != 0.0:
      new = b.difference(a)
      new_content.append(new)
      similar_users.append(user)

  # flatten the list with the sets
  new_content = list(itertools.chain(*new_content))

  # select the books
  df_recommendations = df_ratings[df_ratings['User-ID'].isin(similar_users) & df_ratings['ISBN'].isin(new_content)]
  df_recommendations = df_recommendations.sort_values('Book-Rating', ascending=False)  
  
  return df_recommendations

# create a dataframe where you get all the ratings from the selected user
df_user_ratings = df_ratings[df_ratings['User-ID'] == st.session_state['User-ID']]

# display the reviews of the user
st.subheader('User '+str(st.session_state['User-ID'])+' reviewed')
df = df_user_ratings.merge(df_books, on='ISBN')
t.recommendations(df)

# display the recommendations for the user
st.subheader('Reviews based on Jaccard distance to other users')
df_recommendations = get_jaccard_recommendations(st.session_state['User-ID'])
df = df_recommendations.merge(df_books, on='ISBN').head(10)
t.recommendations(df)