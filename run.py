from flask import Flask
from config.settings import Config
from app.routes.recommend_routes import recommend_bp
from app.routes.index_routes import index_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all routes

    # Register Blueprints
    app.register_blueprint(recommend_bp, url_prefix='/api')
    app.register_blueprint(index_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
