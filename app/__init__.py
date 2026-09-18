from flask import Flask, render_template
from config import Config
from app.routes.api import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    @app.route("/")
    def home():
        return render_template("index.html")

    app.register_blueprint(api)
    
    return app


