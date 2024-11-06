import requests
from flask_migrate import Migrate
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db, User, Movie


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

OMDB_API_KEY = "7428de20"
OMDB_API_URL = "http://www.omdbapi.com/"

# Initialize SQLAlchemy with the app
db.init_app(app)
migrate = Migrate()

migrate.init_app(app, db)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Instantiate the data manager
data_manager = SQLiteDataManager(app)


@app.route("/")
def home():
    return "Welcome to MoviWeb App!"


# Route to display a form for adding a new user
@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_name = request.form.get('name').strip().lower()

        existing_user = User.query.filter(User.name.ilike(user_name)).first()
        if existing_user:
            flash('User already exists')
            return redirect(url_for('list_users'))

        # Add new user if not exists
        new_user = User(name=user_name)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully')
        print("User added successfully")
        return redirect(url_for('add_user'))

    # If GET request, show the form
    return render_template('add_user.html')


@app.route("/users/<int:user_id>/delete", methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User does not exist')
        return redirect(url_for('list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    print("User deleted successfully")
    return redirect(url_for('list_users'))


@app.route("/users")
def list_users():
    users = data_manager.get_all_users()
    print("USER RETRIEVED: ", users)
    return render_template("users.html", users=users)


@app.route("/users/<int:user_id>")
def user_movies(user_id):
    user = data_manager.get_user(user_id)
    app.logger.debug("Data retrieved for user %s: % s", user_id, user)

    if not user:
        app.logger.warning("User %s not found", user_id)
        return render_template("404.html"), 404

    movies = data_manager.get_user_movies(user_id)

    if not movies:
        movies = []
        app.logger.info("No movies for user %s", user_id)
    else:
        app.logger.info("Movies for user %s: %s", user_id, movies)

    return render_template("user_movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/add_movie", methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == "POST":
        print("Received POST request")

        # Extract data from the JSON payload
        name = request.form.get("name").strip()

        if not name:
            flash('Movie name is required.', 'error')
            return redirect(url_for('user_movies', user_id=user_id))

        existing_movie = Movie.query.filter_by(name=name, user_id=user_id).first()
        if existing_movie:
            flash('Movie already exists for this user.', 'error')
            return redirect(url_for('user_movies', user_id=user_id))

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
                        flash('Year must be between 1900 and current year.', 'error')
                        return redirect(url_for('user_movies', user_id=user_id))
                except ValueError:
                    flash('Invalid year format received from OMDb.', 'error')
                    return redirect(url_for('add_movie', user_id=user_id))

                try:
                    rating_float = float(rating)
                    if not (1 <= rating_float <= 10):
                        flash('Rating must be between 1 and 10.', 'error')
                        return redirect(url_for('add_movie', user_id=user_id))
                except ValueError:
                    flash('Invalid rating format received from OMDb.', 'error')
                    return redirect(url_for('add_movie', user_id=user_id))

                new_movie = Movie(name=name, director=director, year=year, rating=rating, user_id=user_id)
                db.session.add(new_movie)
                db.session.commit()
                print("NEW MOVIE ADDED: ", new_movie)
                flash("Movie added successfully", "success")
            else:
                flash("Movie not found in OMDb.", "error")
        else:
            flash("Error fetching movie details from OMDb.", "error")

        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    # Retrieve the movie by ID
    movie = db.session.query(Movie).get(movie_id)
    print(movie)

    if not movie:
        flash("Movie not found.")
        return redirect(url_for("user_movies", user_id=user_id))

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

        if name:
            movie.name = name
        if director:
            movie.director = director
        movie.year = year
        movie.rating = rating

        db.session.commit()
        flash("Movie updated successfully", "success")

        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("update_movie.html", user_id=user_id, movie=movie)


@app.route("/users/<int:user_id>/delete_movie/<int:movie_id>", methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    movie = db.session.query(Movie).get(movie_id)
    if movie and movie.user_id == user_id:
        db.session.delete(movie)
        db.session.commit()
        flash("Movie deleted successfully.")
    else:
        flash("Movie not found or unauthorized.")
    return redirect(url_for("user_movies", user_id=user_id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # rollback in this case to any transaction issues
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)
