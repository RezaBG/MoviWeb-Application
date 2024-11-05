from .data_manager_interface import DataManagerInterface
from datamanager.models import db, User, Movie

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        """Initialize the SQLiteDateManager with the Flask app context."""
        self.app = app


    def get_all_users(self):
        """Retrieve all users."""
        with self.app.app_context():
            return db.session.query(User).all()

    def get_user_movies(self, user_id):
        """Retrieve all movies for a specific user."""
        return db.session.query(Movie).filter_by(user_id=user_id).all()

    def add_user(self, user):
        """Add a user."""
        db.session.add(user)
        db.session.commit()

    def add_movie(self, movie):
        """Add a movie."""
        db.session.add(movie)
        db.session.commit()

    def update_movie(self, movie_id, updated_movie):
        """Update a movie information."""
        movie = db.session.query(Movie).get(movie_id)
        if movie:
            for key, value in updated_movie.items():
                setattr(movie, key, value)
            db.session.commit()

    def delete_movie(self, movie_id):
        """Delete a movie."""
        movie = db.session.query(Movie).get(movie_id)
        if movie:
            db.session.delete(movie)
            db.session.commit()

    def get_user(self, user_id):
        """Retrieve a user by ID"""
        with self.app.app_context():
            return db.session.query(User).get(user_id)