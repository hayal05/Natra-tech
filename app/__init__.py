"""Application factory."""
from datetime import datetime

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from . import db
from .config import Config
from .content import COMPANY
from . import errors, videos
from .routes import admin, apply, careers, main, seo as seo_routes
from .security import init_csrf, init_headers
from .seo import site_url


def create_app():
    Config.validate()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = Config.SECRET_KEY or "dev-only-insecure-key"

    app.jinja_env.globals["now_year"] = datetime.now().year
    app.jinja_env.globals["company"] = COMPANY
    if Config.ENV == "production":  # Render sits behind a proxy
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    db.init_app(app)
    init_csrf(app)
    init_headers(app)
    errors.init_app(app)
    app.jinja_env.globals["site_url"] = site_url
    app.jinja_env.globals["video_thumb"] = videos.thumbnail
    app.jinja_env.filters["lines"] = lambda t: [l.strip(" -•") for l in (t or "").splitlines() if l.strip()]
    app.register_blueprint(main.bp)
    app.register_blueprint(careers.bp)
    app.register_blueprint(apply.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(seo_routes.bp)
    return app
