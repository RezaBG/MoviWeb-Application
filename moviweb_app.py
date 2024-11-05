from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.sqlite_data_manager import SQLiteDataManager
from datamanager.models import db, User, Movie

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Instantiate the data manager
data_manager = SQLiteDataManager(app)


@app.route("/")
def home ():
    return "Welcome to MoviWeb App!"


@app.route("/users")
def list_users ():
    users = data_manager.get_all_users()
    return render_template("users.html", users=users)


@app.route("/users/<int:user_id>")
def user_movies (user_id):
    user = data_manager.get_user(user_id)
    movies = data_manager.get_user_movies(user_id)
    app.logger.info("movies for user %s: %s", user_id, movies)
    return render_template("user_movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/add_movie", methods=['GET', 'POST'])
def add_movie (user_id):
    if request.method == "POST":
        print("Received POST request")

        # Get data from JSON request
        data = request.json
        print("Received data: ", data)

        # Extract data from the JSON payload
        name = data.get("name")
        director = data.get("director")
        year = data.get("year")
        rating = data.get("rating")

        if not name:
            flash("Movie name is required.")
            return redirect(url_for("user_movies", user_id=user_id))

        # check for duplicate movie title
        existing_movie = Movie.query.filter_by(name=name, user_id=user_id).first()
        if existing_movie:
            flash("Movie already exists for this user.")
            return redirect(url_for("user_movies", user_id=user_id))

        # Create a new Movie object and add it to the database
        new_movie = Movie(name=name, director=director, year=year, rating=int(rating), user_id=user_id)
        data_manager.add_movie(new_movie)

        flash("Movie added successfully.")
        return redirect(url_for("user_movies", user_id=user_id))

    # Render the add_movie from if the request method is GET
    return render_template("add_movie.html", user_id=user_id)


@app.route("/users/<int:user_id>/update_movie/<int:movie_id>", methods=['GET', 'POST'])
def update_movie (user_id, movie_id):
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
            year = int(request.form.get("year"))
            rating = int(request.form.get("rating"))
        except ValueError:
            return redirect(url_for("update_movie", user_id=user_id, movie_id=movie_id))

        # Update movie details
        movie.name = name
        movie.director = director
        movie.year = year
        movie.rating = rating

        # Commit changes
        db.session.commit()
        flash("Movie updated successfully.")

        # Redirect bac to the user's movie list
        return redirect(url_for("user_movies", user_id=user_id))

    # Redirect the update form with current movie details pre-filled
    return render_template("update_movie.html", user_id=user_id, movie=movie)


if __name__ == "__main__":
    app.run(debug=True)
