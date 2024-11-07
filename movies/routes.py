from flask import Blueprint, render_template, redirect, url_for, flash, request
from datamanager.models import db, Movie
import requests
from datetime import datetime

movies_bp = Blueprint('movies', __name__, template_folder='templates')

OMDB_API_KEY = "7428de20"
OMDB_API_URL = "http://www.omdbapi.com/"

@movies_bp.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == "POST":
        name = request.form.get("name").strip()
        if not name:
            flash('Movie name is required.', 'error')
            return redirect(url_for('users.user_movies', user_id=user_id))

        existing_movie = Movie.query.filter_by(name=name, user_id=user_id).first()
        if existing_movie:
            flash('Movie already exists for this user.', 'error')
            return redirect(url_for('users.user_movies', user_id=user_id))

        response = requests.get(OMDB_API_URL, params={
            'apikey': OMDB_API_KEY,
            't': name
        })
        if response.status_code == 200:
            movie_data = response.json()
            if movie_data.get('Response') == 'True':
                director = movie_data.get('Director', "N/A")
                year = movie_data.get('Year', "N/A")
                rating = movie_data.get('imdbRating', "N/A")

                try:
                    year_int = int(year)
                    current_year = datetime.now().year
                    if not (1900 <= year_int <= current_year):
                        flash(f'Invalid year {year}. Year must be between 1900 and {current_year}.', 'error')
                        return redirect(url_for('users.user_movies', user_id=user_id))
                except ValueError:
                    flash('Invalid year format received from OMDb.', 'error')
                    return redirect(url_for('movies.add_movie', user_id=user_id))

                try:
                    rating_float = float(rating)
                    if not (1 <= rating_float <= 10):
                        flash(f'Invalid rating {rating}. Rating must be between 1 and 10.', 'error')
                        return redirect(url_for('movies.add_movie', user_id=user_id))
                except ValueError:
                    flash('Invalid rating format received from OMDb.', 'error')
                    return redirect(url_for('movies.add_movie', user_id=user_id))

                new_movie = Movie(name=name, director=director, year=year, rating=rating, user_id=user_id)
                db.session.add(new_movie)
                db.session.commit()
                print("NEW MOVIE ADDED: ", new_movie)
                flash("Movie added successfully", "success")
            else:
                flash("Movie not found in OMDb. Ensure the title is spelled correctly or try another title.", "error")
        else:
            flash("Error fetching movie details from OMDb. Please try again later.", "error")

        return redirect(url_for('users.user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@movies_bp.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    # Retrieve the movie by ID
    movie = db.session.query(Movie).get(movie_id)
    if not movie:
        flash("Movie not found.")
        return redirect(url_for("users.user_movies", user_id=user_id))

    if request.method == "POST":
        # Retrieve form data
        name = request.form.get("name")
        director = request.form.get("director")

        try:
            year = int(request.form.get("year")) if request.form.get("year") else movie.year
        except ValueError:
            flash("Invalid year format received from OMDb.", "error")
            return redirect(url_for("update_movie", user_id=user_id, movie_id=movie_id))

        try:
            rating = float(request.form.get("rating")) if request.form.get("rating") else movie.rating
        except ValueError:
            flash("Invalid rating format received from OMDb.", "error")
            return redirect(url_for("update_movie", user_id=user_id, movie_id=movie_id))

        movie.name = name or movie.name
        movie.director = director or movie.director
        movie.year = year
        movie.rating = rating

        db.session.commit()
        flash("Movie updated successfully", "success")

        return redirect(url_for("users.user_movies", user_id=user_id))

    return render_template("update_movie.html", user_id=user_id, movie=movie)


@movies_bp.route('/<int:user_id>/delete_movie/<int:movie_id>', methods=['POST'])
def delete_movie(user_id, movie_id):
    movie = db.session.query(Movie).get(movie_id)
    if movie and movie.user_id == user_id:
        db.session.delete(movie)
        db.session.commit()
        flash("Movie deleted successfully.")
    else:
        flash("Movie not found or unauthorized.")
    return redirect(url_for("users.user_movies", user_id=user_id))

