"""TechNova Inventory Management — Flask application factory."""
import os
import logging

from flask import Flask
from prometheus_flask_instrumentator import PrometheusMetrics
from .models import db
from .routes import api


def create_app(testing=False):
    app = Flask(__name__)

    # Config
    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "DATABASE_URL", "sqlite:///inventory.db"
        )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Extensions
    db.init_app(app)
    app.register_blueprint(api)

    # Prometheus metrics (skip in testing)
    if not testing:
        PrometheusMetrics(app)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
