from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
site = "https://api.themoviedb.org/3/search/movie"
key = "6284076e41d9e9269b9241e02ec11f29"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db = SQLAlchemy()
db.init_app(app)

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, unique = True)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)

with app.app_context():
    db.create_all()

class editForm(FlaskForm):
    rating = FloatField("Your rating out of 10", [DataRequired(), NumberRange(min=1, max=10, message="Please Enter Rating Between 1 and 10")])
    review = StringField("Your review",[DataRequired()])
    submit = SubmitField("Done")

class addForm(FlaskForm):
    name = StringField("Movie Title", [DataRequired()])
    submit = SubmitField("Add Movie")

@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.ranking).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies)-i
    db.session.commit()
    return render_template("index.html", movies = all_movies)

@app.route("/add", methods = ["POST", "GET"])
def add():
    form = addForm()
    if form.validate_on_submit():
        title = form.name.data
        response = requests.get(site, params={
            "api_key":key,
            "query":title
        })
        arr = response.json()["results"]
        return render_template("select.html", arr = arr)
    return render_template("add.html", form = form)

@app.route("/edit", methods = ["GET", "POST"])
def edit():
    form = editForm()
    movie_id = request.args.get("id")
    print(movie_id)
    movie = Movies.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect("/")

    return render_template("edit.html", movie = movie, form = form)

@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movies.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect("/")

@app.route("/find")
def find_movie():
    movie_id = request.args.get("id")
    print()
    if movie_id:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={
                "api_key":key
            }
        ).json()
        new_movie = Movies(
            title = response["title"],
            year = response["release_date"].split("-")[0],
            img_url = f"https://image.tmdb.org/t/p/original{response['poster_path']}",
            description = response["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit",id=new_movie.id))
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=8000)
