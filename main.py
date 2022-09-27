
from flask import Flask,render_template,request
import pickle 
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import requests
from datetime import date, datetime

# Book Recommended System
pop_df = pickle.load(open('pickle/popular.pkl','rb'))
pt = pickle.load(open('pickle/pt.pkl','rb'))
book = pickle.load(open('pickle/book.pkl','rb'))
ss = pickle.load(open('pickle/similarity_score.pkl','rb'))

# Movie Recommended System
filename = 'pickle/nlp_model.pkl'
clf = pickle.load(open(filename, 'rb'))
vectorizer = pickle.load(open('pickle/tranform.pkl','rb'))


app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

# Books Recommended System
@app.route('/books')
def books():
    return render_template('books.html',
                           book_name = list(pop_df['Book-Title'].values),
                           author = list(pop_df['Book-Author'].values),
                           image = list(pop_df['Image-URL-M'].values),
                           publisher = list(pop_df['Publisher'].values),
                           votes = list(pop_df['num_rating'].values),
                           rating = list(pop_df['avg_rating'].values),
                           )

@app.route('/recommended')
def recommended():
    return render_template('recommended.html')

@app.route('/recommended_books',methods=['post'])
def recommended_b():
    user_input = request.form.get('user_input')
    index = np.where(pt.index==user_input)[0][0]
    similar_item = sorted(list(enumerate(ss[index])),key=lambda x:x[1],reverse=True)[1:5]
    data = []
    for i in similar_item:
        item = []
        temp_df = book[book['Book-Title']==pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)
    print(data)
    return render_template('recommended.html',data=data)

# Movie Recommended System

def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

# convert list of numbers to list (eg. "[1,2,3]" to [1,2,3])
def convert_to_list_num(my_list):
    my_list = my_list.split(',')
    my_list[0] = my_list[0].replace("[","")
    my_list[-1] = my_list[-1].replace("]","")
    return my_list

def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

@app.route("/recommend",methods=['GET', 'POST'])
def recommend():
    # getting data from AJAX request
    title = request.form['title']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    rel_date = request.form['rel_date']
    release_date = request.form['release_date']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']
    rec_movies_org = request.form['rec_movies_org']
    rec_year = request.form['rec_year']
    rec_vote = request.form['rec_vote']

    # get movie suggestions for auto complete
    suggestions = get_suggestions()

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies_org = convert_to_list(rec_movies_org)
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    
    # convert string to list (eg. "[1,2,3]" to [1,2,3])

    rec_vote = convert_to_list_num(rec_vote)
    rec_year = convert_to_list_num(rec_year)
    
    
    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: [rec_movies[i],rec_movies_org[i],rec_vote[i],rec_year[i]] for i in range(len(rec_posters))[:5]}

    # web scraping to get user reviews from IMDB site
    sauce = urllib.request.urlopen('https://www.imdb.com/title/{}/reviews?ref_=tt_ov_rt'.format(imdb_id)).read()
    soup = bs.BeautifulSoup(sauce,'lxml')
    soup_result = soup.find_all("div",{"class":"text show-more__control"})

    # getting current date
    movie_rel_date = ""
    curr_date = ""
    if(rel_date):
        today = str(date.today())
        curr_date = datetime.strptime(today,'%Y-%m-%d')
        movie_rel_date = datetime.strptime(rel_date, '%Y-%m-%d')    

    # passing all the data to the html file
    return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
        vote_count=vote_count,release_date=release_date,movie_rel_date=movie_rel_date,curr_date=curr_date,genres=genres,movie_cards=movie_cards)


@app.route('/movies')
def movies(): 
    suggestions = get_suggestions()
    return render_template('movies.html',suggestions=suggestions)

if __name__ == "__main__":
    app.run(debug=True)