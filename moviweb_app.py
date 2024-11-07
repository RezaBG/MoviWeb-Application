from flask import Flask, render_template
from flask_migrate import Migrate
from datamanager.models import db
from movies.routes import movies_bp
from users.routes import users_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Migrate with the app
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(movies_bp, url_prefix='/movies')

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # rollback in this case to any transaction issues
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
