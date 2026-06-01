from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
ma = Marshmallow()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    db.init_app(app)
    ma.init_app(app)

    # ── Routes de base ────────────────────────────────────────────────────────
    @app.route("/")
    def home():
        return "✅ SmartBacklog OK — accède au frontend sur <a href='/test'>/test</a> ou <a href='/test2'>/test2</a> "

    @app.route("/test")
    def test_page():
        # Ici Flask(__name__) → __name__ = "app" → cherche dans app/templates/
        return render_template("front_test.html")

    @app.route("/test2")
    def test2_page():
        # Ici Flask(__name__) → __name__ = "app" → cherche dans app/templates/
        return render_template("index.html")

    from app.models import user, sprint, ticket, project, project_member  # noqa

    with app.app_context():
        db.create_all()
        print("✅ Base de données prête (SQLite)")

    # ── Enregistrement des blueprints ─────────────────────────────────────────
    from app.routes.auth     import bp as auth_bp
    from app.routes.users    import bp as users_bp
    from app.routes.sprints  import bp as sprints_bp
    from app.routes.tickets  import bp as tickets_bp
    from app.routes.projects import bp as projects_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(sprints_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(projects_bp)

    return app