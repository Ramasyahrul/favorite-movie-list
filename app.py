import os
from os.path import join, dirname
from dotenv import load_dotenv
from http import client
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/movie", methods=["POST"])
def movie_post():
    # Meneriman data dari sisi client yang dikirimkan dengan ajax
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']

    # melakukan request ke halaman web
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive,headers=headers)

    # melakukan web scraping
    soup = BeautifulSoup(data.text, 'html.parser')
    og_image = soup.select_one('meta[property="og:image"]')     
    og_title = soup.select_one('meta[property="og:title"]')
    og_description = soup.select_one('meta[name="description"]')
    image = og_image['content']
    title = og_title['content']
    desc = og_description['content']

    # memasukkan data ke dalam MongoDb
    doc = {
        'image':image,
        'title':title,
        'description':desc,
        'star':star_receive,
        'comment':comment_receive
    }

    db.movies.insert_one(doc)


    # response dari sisi server
    return jsonify({'msg':'POST request!'})

@app.route("/movie", methods=["GET"])
def movie_get():
    # Mendapatkan data di MongoDb
    movie_list = list(db.movies.find({}, {'_id': False}))

    # Mengirimkan response pada client dengan membawa data dari MongoDb
    return jsonify({'movies': movie_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)