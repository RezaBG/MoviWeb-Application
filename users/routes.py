from flask import render_template, url_for, flash, redirect, Blueprint, request, current_app
from datamanager.models import db, User
from datamanager.sqlite_data_manager import SQLiteDataManager

# Define Blueprint
users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/')
def list_users():
    users = User.query.all()
    print("Users retrieved from database:", users)
    return render_template('users.html', users=users)

@users_bp.route('/add', methods=['GET','POST'])
def add_user():
    if request.method == 'POST':
        user_name = request.form.get('name').strip().lower()

        existing_user = User.query.filter(User.name.ilike(user_name)).first()
        if existing_user:
            flash(f"User '{user_name}' already exists. Redirecting to user's page.", 'warning')
            return redirect(url_for('users.user_movies', user_id=existing_user.id))

        # Add new user if not exists
        new_user = User(name=user_name)
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {user_name} added successfully')
        return redirect(url_for('users.list_users'))

    # If GET request, show the form
    return render_template('add_user.html')


@users_bp.route('/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found')
        return redirect(url_for('users.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('users.list_users'))


@users_bp.route('/<int:user_id>')
def user_movies(user_id):
    user = User.query.get(user_id)
    current_app.logger.debug("Data retrieved for user %s: %s", user_id, user)

    if not user:
        current_app.logger.warning("User %s not found", user_id)
        return render_template("404.html"), 404

    movies = user.movies

    if not movies:
        current_app.logger.info("No movies for user %s", user_id)
    else:
        current_app.logger.info("Movies for user %s: %s", user_id, movies)

    return render_template("user_movies.html", user=user, movies=movies)
