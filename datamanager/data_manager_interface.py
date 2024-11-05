from abc import ABC, abstractmethod

class DataManagerInterface(ABC):
    @abstractmethod
    def get_all_users(self):
        """Retrieve all users"""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """Retrieve all movies for specific user"""
        pass

    @abstractmethod
    def add_user(self, user_id):
        """Add new user"""
        pass

    @abstractmethod
    def add_movie(self, movie_id):
        """Add new movie"""
        pass

    @abstractmethod
    def update_movie(self, movie_id, updated_info):
        """Update movie information"""
        pass

    @abstractmethod
    def delete_movie(self, movie_id):
        """Delete a movie"""
        pass
