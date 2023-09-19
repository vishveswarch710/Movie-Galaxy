import streamlit as st
import pickle
import pandas as pd
import requests
from PIL import Image
import numpy as np
import re
from io import BytesIO
import time
import base64
import streamlit.components.v1 as components
st.set_page_config(page_title='Movie Recommendation System', layout='wide')
# mood_dict = {'Happy': 'Horror', 'Sad': 'Drama', 'Satisfied': 'Animation', 'Angry': 'Romance', 'Peaceful': 'Fantasy',
#              'Fearful': 'Adventure', 'Excited': 'Crime', 'Depressed': 'Comedy', 'Content': 'Mystery', 'Sorrowful': 'Action'}


def local_css(file_name):
    html_string = ''
    with open(file_name) as f:
        html_string = html_string+f.read()
    return html_string


def icon(icon_name):
    return f'<i class="material-icons">{icon_name}</i>'


def generate_set(attribute):
    Set = set()
    movies[attribute] = movies[attribute].apply(
        lambda x: [] if x != x else (x if isinstance(x, list) else [x]))
    for x in [movies.iloc[x] for x in range(len(list(movies[attribute])))]:
        for y in x.get(attribute):
            Set.add(y)
    if('' in Set):
        Set.remove('')
    return list(Set)


def fetch_poster(index):
    path = movies.iloc[index].poster_path
    if(path != path):
        path = "data:image/png;base64,{0}".format(
            base64.b64encode(open('poster.png', 'rb').read()).decode('utf-8'))
    else:
        response = requests.get(path)
        if(response.status_code != 200):
            path = "data:image/png;base64,{0}".format(
                base64.b64encode(open('poster.png', 'rb').read()).decode('utf-8'))
    #     else:
    #         path = BytesIO(response.content)
    # return Image.open(path).resize((400, 600))
    return path


def get_year(index):
    html_string = ''
    if(movies.iloc[index].year_of_release == movies.iloc[index].year_of_release):
        html_string += '<h6>' + \
            str(int(movies.iloc[index].year_of_release))+'</h6>'
    return html_string


def get_runtime(index):
    html_string = ''
    if(movies.iloc[index].runtime == movies.iloc[index].runtime):
        html_string += '<div style="display:inline-flex">'+icon('timer')+'<h6>' + \
            str(int(movies.iloc[index].runtime))+'min</h6></div>'
    return html_string


def get_rating(index):
    html_string = ''
    if(movies.iloc[index].imdb_rating == movies.iloc[index].imdb_rating):
        html_string += '<div style="display:inline-flex">'+icon('star')+'<h6>' + \
            str(int(movies.iloc[index].imdb_rating))+'/10</h6></div>'
    return html_string


def get_story(index):
    html_string = ''
    if(movies.iloc[index].story == movies.iloc[index].story):
        html_string += '<p>' + \
            movies.iloc[index].story[0:min(
                len(movies.iloc[index].story), 200)]
        if(html_string[-1] != '.'):
            html_string += "..."
        html_string += '</p>'
    return html_string


def get_genres(index):
    html_string = ''
    for genre in movies.iloc[index].genres:
        html_string += '<div class="genre">' + \
            genre+'</div>'
    return html_string


def display_poster(index_list):
    html_string = """
    <style>{style}</style>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <div class="recommendations">
    """.format(style=local_css("style.css"))
    for i in index_list:
        html_string += """<div class = "card" >
    <div class = "card-header" style = "position:relative" >
    <img src = "{img_url}" alt = "image not found" style = "width:100%; height:350px" >
    <div class = "movie_details" >
    <h2 class = "title" > {title} </h2>
    <div class = "year_runtime">
    {year}
    {runtime}
    {rating}
    </div>
    <div class = "genres">
    {genres}
    </div >
    <div class = "story">
    {story}
    </div >
    <div class = "more_info">
    <a href = "https://www.imdb.com/title/{imdb_id}" target = "_blank"> <button type = "button" class = "btn"> Read More </button> </a>
    </div>
    </div>
    </div>
<div class = "card-body" >
    <h5 class = "card-title" > {title} </h5>
  </div>  
</div>
    """.format(imdb_id=movies.iloc[i].imdb_id, story=get_story(i), genres=get_genres(i), rating=get_rating(i), year=get_year(i), runtime=get_runtime(i), img_url=fetch_poster(i), title=movies.iloc[i].title)
    html_string += "</div>"
    components.html(html_string, height=2100, scrolling=True)


def recommend_from_name(movie, adult):
    movie_index = movies[movies['title'] == movie].index[0]
    # print(movie_index)
    distances = similarity[movie_index]
    movies_list = [
        x for x in distances if adult or not movies.iloc[x[0]].adult][1:26]
    sorted_list = [x[0] for x in movies_list]
    return sorted_list


def recommend_from_mood(emotion, adult):
    sorted_list = sorted([x for x in movies.index if movies.iloc[x].story == movies.iloc[x].story and (adult or not movies.iloc[x[0]].adult)],
                         key=lambda x: movies.iloc[x].Emotion[0][emotion], reverse=True)[0:25]
    # for i in sorted_list:
    #     print(movies.iloc[i].Emotion[0][emotion])
    return sorted([x for x in movies.index if movies.iloc[x].story == movies.iloc[x].story and (adult or not movies.iloc[x[0]].adult)],
                  key=lambda x: movies.iloc[x].Emotion[0][emotion], reverse=True)[0:25]


def recommend_from_details(details):
    sorted_list = []
    for i in movies.index:
        take = True
        if(not movies['genres'][i] or not movies['actors'][i] or not movies['directors'][i] or not movies['writers'][i]):
            take = False
        if not all(genre in movies['genres'][i] for genre in details['genres']):
            take = False
        if float(movies['year_of_release'][i]) < details['release_year'][0] or float(movies['year_of_release'][i]) > details['release_year'][1]:
            take = False
        if movies['imdb_rating'][i] < details['rating'][0] or movies['imdb_rating'][i] > details['rating'][1]:
            take = False

        if float(movies['runtime'][i]) < details['runtime'][0] or float(movies['runtime'][i]) > details['runtime'][1]:
            take = False
        # if not all(production_company in movies['production_companies'][i] for production_company in details['production_companies']):
        #     take = False
        # if movies['release_date'][i] < details['release_date']:
        #     take = False
        # print(details['cast'])
        if not all(cast in movies['actors'][i] for cast in details['cast']):
            take = False
        if not all(director in movies['directors'][i] for director in details['director']):
            take = False
        if not all(writers in movies['writers'][i] for writers in details['writers']):
            take = False
        if(take):
            sorted_list.append(i)
    sorted_list = sorted([x for x in sorted_list],
                         key=lambda x: movies.iloc[x].imdb_rating, reverse=True)
    if(len(sorted_list) > 25):
        sorted_list = sorted_list[0:25]
    return sorted_list


def display_genres():
    selected_movie_genre = st.multiselect(
        'Enter movie genre', generate_set('genres'))
    details['genres'] = selected_movie_genre


def display_release_year_element():
    col1, col2 = st.columns(2)
    with col1:
        start_release_year = st.number_input(
            'Enter the minimum release year', key=8, min_value=1950, max_value=2019, value=1950)
    with col2:
        end_release_year = st.number_input(
            'Enter the maximum release year', key=9, min_value=1950, max_value=2019, value=2019)
    details['release_year'] = (
        start_release_year, end_release_year)


def display_cast_element():
    cast = st.multiselect(
        'Enter movie cast', generate_set('actors'))
    if(cast != ''):
        details['cast'] = cast


def display_rating_element():
    col1, col2 = st.columns(2)
    with col1:
        start_rating = st.number_input(
            'Enter the minimum rating', key=10, min_value=0.0, max_value=10.0, value=0.0, step=0.1)
    with col2:
        end_rating = st.number_input(
            'Enter the maximum rating', key=11, min_value=0.0, max_value=10.0, value=10.0, step=0.1)
    details['rating'] = (start_rating, end_rating)


def display_runtime_element():
    col1, col2 = st.columns(2)
    with col1:
        start_runtime = st.number_input(
            'Enter the minimum runtime', key=12, min_value=0, max_value=330, value=0, step=15)
    with col2:
        end_runtime = st.number_input(
            'Enter the maximum runtime', key=13, min_value=0, max_value=330, value=330, step=15)
    details['runtime'] = (start_runtime, end_runtime)


def display_director_element():
    director = st.selectbox(
        'Enter movie director\'s name', ['Choose an option']+generate_set('directors'))
    if(director != 'Choose an option'):
        details['director'] = list(director)


def display_writers_element():
    writers = st.multiselect(
        'Enter movie writers\' name', generate_set('writers'))
    details['writers'] = writers


similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_dict = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
st.title('Movie Recommender system')
strategy = st.subheader('Recommend according to:')
tab1, tab2, tab3 = st.tabs(["Movie name", "Mood", "Movie Details"])
with tab1:
    selected_movie_name = st.selectbox('Enter movie name',
                                       movies['title'].values.tolist())
    adult = False
    if(st.radio('Are you an adult?', ['Yes', 'No'], key=1) == 'Yes'):
        adult = True
    if st.button('Recommend', key=2):
        index_list = recommend_from_name(selected_movie_name, adult)
        display_poster(index_list)

with tab2:
    selected_emotion = st.selectbox('What kind of movie would you like to watch?', [
        'Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Trust'])
    adult = False
    if(st.radio('Are you an adult?', ['Yes', 'No'], key=3) == 'Yes'):
        adult = True
    if st.button('Recommend', key=4):
        index_list = recommend_from_mood(selected_emotion.lower(), adult)
        display_poster(index_list)

with tab3:
    if 'count' not in st.session_state:
        st.session_state['count'] = 0
    if 'check_placeholder' not in st.session_state:
        st.session_state['check_placeholder'] = [False]*6
    count = st.session_state['count']
    check_placeholder = st.session_state['check_placeholder']
    details = {'genres': [], 'release_year': (1950, 2019), 'rating': (
        0.00, 10.00), 'runtime': (0, 330), 'cast': [], 'director': [], 'writers': []}
    element = [display_release_year_element, display_cast_element, display_rating_element,
               display_runtime_element, display_director_element, display_writers_element]
    display_genres()
    for i in range(6):
        if(check_placeholder[i]):
            element[i]()
        else:
            break
    if(count < 6):
        if st.button("Add more filters"):
            st.session_state['count'] = count+1
            check_placeholder[count] = True
            st.session_state['check_placeholder'] = check_placeholder
            st.experimental_rerun()
    if(details['rating'][0] > details['rating'][1] or details['release_year'][0] > details['release_year'][1] or details['runtime'][0] > details['runtime'][1]):
        st.markdown(
            f'<p style="color:red">Please Enter valid movie details</p>', unsafe_allow_html=True)
    else:
        if st.button('Recommend', key=5):
            index_list = recommend_from_details(details)
            if(len(index_list)):
                display_poster(index_list)
            else:
                st.text("No results match your search")
