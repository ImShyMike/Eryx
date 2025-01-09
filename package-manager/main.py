"""Package manager for Eryx."""

import os
import uuid
import zipfile
from datetime import datetime, timedelta

import bleach
import markdown
import toml
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.contrib.github import github, make_github_blueprint
from flask_humanize import Humanize
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from markupsafe import Markup
from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import S3Error
from packaging.version import InvalidVersion, Version
from sqlalchemy import func
from werkzeug.middleware.proxy_fix import ProxyFix

# from flask_caching import Cache

load_dotenv()

WIPE_DATABASE = False  # THIS WILL WIPE THE DATABASE AND BUCKET ON STARTUP

PACKAGES_BUCKET = "eryx-packages"

ALLOWED_TAGS = [
    "p",
    "b",
    "i",
    "strong",
    "em",
    "ul",
    "ol",
    "li",
    "a",
    "code",
    "pre",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt", "title"],
}


def process_readme(raw_readme):
    """Turn a raw readme into sanitized HTML."""
    # Convert Markdown to HTML
    html_content = markdown.markdown(raw_readme)
    # Sanitize HTML
    sanitized_html = bleach.clean(
        html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES
    )
    return Markup(sanitized_html)


class ForceHTTPS:  # Needed on nest because of flask dance being dumb
    """Fix for Flask Dance OAuth issues with HTTPS."""

    def __init__(self, app):  # pylint: disable=redefined-outer-name
        self.app = app

    def __call__(self, environ, start_response):
        # Force the URL scheme to HTTPS
        environ["wsgi.url_scheme"] = "https"
        return self.app(environ, start_response)


app = Flask(__name__)
humanize = Humanize(app)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
)
app.wsgi_app = ForceHTTPS(app.wsgi_app)
app.secret_key = os.getenv("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

client = Minio(
    os.getenv("MINIO_URL", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=True,
)

# Configure flask limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"],
    storage_uri="memory://",
)

# Configure PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# Create cache
# cache = Cache(app, config={"CACHE_TYPE": "simple"})

csp = {
    "default-src": ["'self'"],
    "img-src": ["'self'", "https://avatars.githubusercontent.com"],
    "script-src-elem": ["'unsafe-inline'"],
    "script-src": ["'self'"],
}

# Enable HTTPS
Talisman(app, force_https=False, content_security_policy=csp)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize the login manager
login_manager = LoginManager(app)
login_manager.login_view = "github.login"  # type: ignore
login_manager.init_app(app)

# Set up the GitHub OAuth Blueprint
github_blueprint = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
)
app.register_blueprint(github_blueprint, url_prefix="/login")


class User(UserMixin, db.Model):
    """User db table"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    is_banned = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    github_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    username = db.Column(db.String(39), unique=True, nullable=False)
    api_key = db.Column(db.String(36), unique=True, nullable=True)


class OAuth(OAuthConsumerMixin, db.Model):
    """OAuth db table."""

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref="oauth_tokens")


github_blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)


class Package(db.Model):
    """Package db table."""

    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    description = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, default=db.func.now())
    download_count = db.Column(db.Integer, default=0)
    latest_version = db.Column(db.String(32))
    releases = db.relationship("Release", backref="package", lazy="dynamic")

    @property
    def latest_release(self):
        """Latest release for a package."""
        return self.releases.order_by(Release.release_date.desc()).first()  # type: ignore


class Release(db.Model):
    """Releases db table."""

    __tablename__ = "releases"
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), nullable=False)
    version = db.Column(db.String(32), nullable=False)
    release_date = db.Column(db.DateTime, default=db.func.now())
    download_count = db.Column(db.Integer, default=0)
    readme = db.Column(db.Text)
    file_path = db.Column(db.String(256), nullable=False)

    def update_parent_version(self):
        """Update the parent package's latest version."""
        self.package.latest_version = self.version  # type: ignore
        db.session.commit()

    def increment_download_count(self):
        """Increment the download count for a release."""
        self.download_count += 1
        self.package.download_count += 1  # type: ignore
        db.session.commit()


def get_release_by_version(package_id: int, version: str) -> Release | None:
    """Get a release by package id and version."""
    return Release.query.filter_by(package_id=package_id, version=version).first()


def parse_toml_file(toml_content):
    """Parse TOML content from a string."""
    try:
        data = toml.loads(toml_content)  # Parse TOML content from a string
        return data
    except toml.TomlDecodeError as e:
        print(f"Failed to parse TOML: {e}")
        return None


def read_files_from_zip(
    file, files_to_read, max_size=1024 * 1024
):  # Default max size is 1MB
    """Reads specified files from an uploaded ZIP file without extracting them."""
    file_contents = {}

    # Ensure the uploaded file is a valid ZIP
    with zipfile.ZipFile(file.stream, "r") as z:
        for file_name in files_to_read:
            if file_name in z.namelist():
                info = z.getinfo(file_name)

                # Check the uncompressed file size
                if info.file_size > max_size:
                    raise ValueError(
                        f"The file '{file_name}' exceeds the maximum "
                        f"allowed size of {max_size} bytes."
                    )

                # Read the file's content
                with z.open(file_name) as f:
                    file_contents[file_name] = f.read().decode("utf-8")

    return file_contents


def get_package_stats():
    """Get the stats of packages on the server"""
    total_downloads = db.session.query(func.sum(Package.download_count)).scalar() or 0
    total_packages = db.session.query(func.count(Package.id)).scalar() or 0  # pylint: disable=E1102
    return {"total_downloads": total_downloads, "total_packages": total_packages}


@app.route("/api/upload", methods=["POST"])
@limiter.limit("5 per hour")
def api_upload_package():
    """Package upload endpoint for authenticated users."""
    api_key = request.headers.get("X-API-Key")
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    if user.is_banned:
        return jsonify({"error": "Your account is banned"}), 423

    file = request.files.get("package_file")

    if not file or not file.filename:
        return jsonify({"error": "Missing package file"}), 400

    file_stream = file.stream  # type: ignore
    file.seek(0)  # type: ignore

    files = read_files_from_zip(file, ["package.toml", "README.md", "main.eryx"])
    package_toml, readme, entrypoint = (
        files.get("package.toml"),
        files.get("README.md"),
        files.get("main.eryx"),
    )

    if not readme:
        return jsonify({"error": "Missing README.md file"}), 400

    if not package_toml:
        return jsonify({"error": "Missing package.toml file"}), 400

    if not entrypoint:
        return jsonify({"error": "Missing entrypoint file"}), 400

    parsed_toml = parse_toml_file(package_toml)
    if not parsed_toml:
        return jsonify({"error": "Invalid package.toml file"}), 400

    package_cfg = parsed_toml.get("package", {})
    name = package_cfg.get("name")
    version = package_cfg.get("version")
    description = package_cfg.get("description")

    try:
        version = Version(version)
    except InvalidVersion:
        return jsonify({"error": "Invalid version string"}), 409

    if not name or not version or not description:
        return jsonify({"error": "Invalid package data"}), 400

    existing_package = Package.query.filter_by(name=name).first()

    if existing_package:
        if not existing_package.author_id == user.id:
            return jsonify({"error": "You are not the owner of this package"}), 403

        if Version(existing_package.latest_version) >= version:
            return jsonify(
                {
                    "error": f"Can not update package, uploaded version <= current "
                    f"version ({version} <= {existing_package.latest_version})"
                }
            ), 409

    name = str(name).lower()

    if not name.isidentifier():
        return jsonify(
            {"error": "Package name can only contain letters, numbers and underscores"}
        ), 400

    if (request.content_length or 1e10) > 1024 * 1024:  # 1 MB
        return jsonify({"error": "Request size must be less than 1MB"}), 400

    filesize = len(file.read())
    file.seek(0)

    if not filesize or filesize == 0:
        return jsonify({"error": "Empty file"}), 400

    if filesize > 1024 * 1024:  # 1 MB
        return jsonify({"error": "File size must be less than 1MB"}), 400

    file_path = f"{name}/{version}.zip"

    if not existing_package:
        new_package = Package(
            name=name,  # type: ignore
            author_id=user.id,  # type: ignore
            description=description,  # type: ignore
        )

        db.session.add(new_package)
        db.session.commit()

        new_package_info = Package.query.filter_by(name=name).first()
        if not new_package_info:
            return jsonify({"error": "Failed to create package"}), 500

        new_release = Release(
            package_id=new_package_info.id,  # type: ignore
            version=str(version),  # type: ignore
            file_path=file_path,  # type: ignore
            readme=readme,  # type: ignore
        )
    else:
        new_release = Release(
            package_id=existing_package.id,  # type: ignore
            version=str(version),  # type: ignore
            file_path=file_path,  # type: ignore
            readme=readme,  # type: ignore
        )

    try:
        client.put_object(
            PACKAGES_BUCKET,
            file_path,
            file_stream,  # type: ignore
            length=-1,
            part_size=5 * 1024 * 1024,
        )
    except S3Error as e:
        print("Failed to upload file", e)
        return jsonify({"error": "Failed to upload file"}), 500

    db.session.add(new_release)
    db.session.commit()

    Release.update_parent_version(new_release)

    return jsonify({"message": "Package uploaded successfully"}), 201


@app.route("/api/versions/<package_name>")
def package_versions(package_name):
    """Package versions endpoint."""
    package = Package.query.filter_by(name=package_name).first()
    if package:
        releases = package.releases.all()
        return jsonify({"versions": [r.version for r in releases]})
    return render_template("notfound.html"), 404


@app.route("/api/delete", methods=["POST"])
@limiter.limit("10 per hour")
def delete_package():
    """Endpoint to delete a package (and all its releases)."""
    json_data = request.json

    if not json_data:
        return jsonify({"error": "Missing JSON data"}), 400

    package = json_data.get("package")
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return jsonify({"error": "Invalid API key"}), 401

    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    if user.is_banned:
        return jsonify({"error": "Your account is banned"}), 423

    if not package:
        return jsonify({"error": "Missing package name"}), 400

    package = Package.query.filter_by(name=package).first()
    if not package:
        return jsonify({"error": "Package not found"}), 404

    if (not package.author_id == user.id) and (not user.is_admin):
        return jsonify({"error": "You are not the owner of this package"}), 403

    for release in package.releases.all():
        db.session.delete(release)
        try:
            client.remove_object(PACKAGES_BUCKET, release.file_path)
        except S3Error as e:
            print("Failed to delete file", e)
            return jsonify({"error": "Failed to delete package"}), 500

    db.session.delete(package)
    db.session.commit()

    return jsonify({"message": "Package deleted successfully"}), 200


@app.route("/api/refresh-key", methods=["POST"])
@limiter.limit("10 per hour")
def refresh_api_key():
    """Endpoint to refresh an API key."""
    api_key = request.headers.get("X-API-Key")
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    if user.is_banned:
        return jsonify({"error": "Your account is banned"}), 423

    user.api_key = str(uuid.uuid4())
    db.session.add(user)
    db.session.commit()

    return jsonify({"key": user.api_key}), 200


@app.route("/package/<package_name>")
def package_detail(package_name):
    """Package details endpoint."""
    package = Package.query.filter_by(name=package_name).first()
    if package:
        latest_release = package.latest_release  # pylint: disable=no-member
        if not latest_release:
            return render_template("notfound.html"), 404

        user = User.query.filter_by(id=package.author_id).first()
        if user:
            user = user.username

        return render_template(
            "package.html",
            package=package,
            latest_release=latest_release,
            readme=process_readme(latest_release.readme),
            author=user,
        )

    return render_template("notfound.html"), 404


@app.route("/download/<package_name>")
def download_package(package_name):
    """Package download endpoint."""
    package = Package.query.filter_by(name=package_name).first()
    if package:
        release = package.latest_release  # pylint: disable=no-member
        if not release:
            return "Package not found", 404

        Release.increment_download_count(release)

        return redirect(
            client.presigned_get_object(
                PACKAGES_BUCKET, release.file_path, expires=timedelta(minutes=1)
            )
        )
    return "Package not found", 404


@app.route("/download/<package_name>/<version>")
def download_package_version(package_name, version):
    """Package version download endpoint."""
    package = Package.query.filter_by(name=package_name).first()
    if package:
        release = get_release_by_version(package.id, version)
        if not release:
            return "Package version not found", 404

        Release.increment_download_count(release)

        return redirect(
            client.presigned_get_object(
                PACKAGES_BUCKET, release.file_path, expires=timedelta(minutes=1)
            )
        )
    return "Package not found", 404


@app.route("/")
@limiter.limit("30 per minute")
def home():
    """Homepage endpoint."""
    top_packages = (
        db.session.query(
            Package.id,
            Package.name,
            Package.latest_version,
            Package.download_count,
            Package.description,
            User.username.label("author_username"),
            Package.download_count.label("total_downloads"),
        )
        .join(User, User.id == Package.author_id)
        .order_by(db.desc(Package.download_count))
        .limit(12)
        .all()
    )
    return render_template(
        "index.html", top_packages=top_packages, stats=get_package_stats()
    )


@app.route("/dashboard")
@limiter.limit("30 per minute")
@login_required
def dashboard():
    """User dashboard endpoint for authenticated users."""
    if current_user and current_user.is_banned:
        return jsonify({"error": "Your account is banned"}), 423

    if github.authorized:  # Check if the user is authenticated with GitHub
        response = github.get("/user")
        if response.ok:
            github_user = response.json()
        else:
            return "Failed to fetch GitHub user information", 500
    else:
        return redirect(url_for("github.login"))

    if not current_user.api_key:
        current_user.api_key = str(uuid.uuid4())
        db.session.commit()

    user_packages = Package.query.filter_by(author_id=current_user.id).all()
    return render_template(
        "dashboard.html",
        user=github_user,
        user_packages=user_packages,
        api_key=current_user.api_key,
    )


@app.route("/logout")
@login_required
def logout():
    """Logout user."""
    logout_user()
    return redirect(url_for("home"))


@app.route("/static/<path:filename>")
def staticfiles(filename):
    """Serve static files."""
    return app.send_static_file(filename)


@app.route("/ping", methods=["GET"])
def ping():
    """Health check endpoint."""
    return "Server is running", 200


@oauth_authorized.connect_via(github_blueprint)
def github_login(blueprint, token):
    """Handle github logins."""
    if not github.authorized:
        return redirect(url_for("github.login"))

    try:
        account_info = github.get("/user")
        if account_info.ok:
            github_info = account_info.json()
            username = github_info["login"]
            # Check if user already exists in the database
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(
                    github_id=github_info["id"],  # type: ignore
                    username=username,  # type: ignore
                    api_key=str(uuid.uuid4()),  # type: ignore
                )
                db.session.add(user)
                db.session.commit()

            oauth = None
            existing_oauth = OAuth.query.filter_by(user_id=user.id).first()
            if existing_oauth:
                if existing_oauth.created_at > (
                    datetime.utcnow() - timedelta(hours=8)
                ):  # not expired
                    oauth = existing_oauth
                else:
                    db.session.delete(existing_oauth)
                    db.session.commit()

            if not oauth:
                oauth = OAuth(
                    user=user,  # type: ignore
                    user_id=user.id,  # type: ignore
                    token=token,  # type: ignore
                    provider=blueprint.name,  # type: ignore
                )

                db.session.add(oauth)
                db.session.commit()

            # Log the user in
            login_user(user, duration=timedelta(days=7))
            return redirect(url_for("home"))

        flash("Could not fetch your GitHub account info.", "error")
        return redirect(url_for("home"))
    except ValueError:
        flash("An error occurred during GitHub authentication.", "error")
        return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    """Load a user."""
    return User.query.filter_by(id=int(user_id)).first()


@app.context_processor
def inject_github():
    """Inject github object into all templates."""
    github_authorized = False
    if current_user.is_authenticated:
        try:
            github_authorized = github.authorized
        except ValueError:
            # Handle the case where there's no OAuth token
            github_authorized = False
    return {"github": github, "github_authorized": github_authorized}


def clear_bucket_batch(bucket_name):
    """Clear all objects in a bucket in a batch."""
    try:
        objects = client.list_objects(bucket_name)
        delete_objects = [
            DeleteObject(obj.object_name) for obj in objects if obj.object_name
        ]

        # Remove objects in batch
        if delete_objects:
            client.remove_objects(bucket_name, delete_objects)
            print(f"All objects in bucket '{bucket_name}' have been deleted.")
        else:
            print("No objects found in the bucket.")
    except S3Error as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    if WIPE_DATABASE:
        clear_bucket_batch(PACKAGES_BUCKET)
        with app.app_context():
            db.drop_all()
    with app.app_context():
        db.create_all()
    # if not client.bucket_exists(PACKAGES_BUCKET):
    #    client.make_bucket(PACKAGES_BUCKET)
    app.run(
        host="127.0.0.1",
        port=5000,
        ssl_context=("cert.pem", "key.pem"),  # Local certs for testing
        debug=False,
        use_reloader=False,
    )
