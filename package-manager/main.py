"""Package manager for Eryx."""

import os
import uuid
import zipfile
from datetime import timedelta

import toml
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_caching import Cache
from flask_dance.contrib.github import github, make_github_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from minio import Minio
from minio.error import S3Error
from packaging.version import InvalidVersion, Version

load_dotenv()

PACKAGES_BUCKET = "eryx-packages"

app = Flask(__name__)
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
cache = Cache(app, config={"CACHE_TYPE": "simple"})

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Set up the GitHub OAuth Blueprint
github_blueprint = make_github_blueprint(
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
)
app.register_blueprint(github_blueprint, url_prefix="/login")

# Enable HTTPS
Talisman(app, content_security_policy=None)


class User(db.Model):
    """User db table"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    username = db.Column(db.String(39), nullable=False)
    api_key = db.Column(db.String(36), unique=True, nullable=True)


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
        self.package.latest_version = self.version  # type: ignore
        db.session.commit()

    def increment_download_count(self):
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


@app.route("/api/upload", methods=["POST"])
@limiter.limit("5 per hour")
def api_upload_package():
    """Package upload endpoint for authenticated users."""
    api_key = request.headers.get("X-API-Key")
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    file = request.files.get("package_file")

    file_stream = file.stream  # type: ignore
    file.seek(0)  # type: ignore

    if not file or not file.filename:
        return jsonify({"error": "Missing package file"}), 400

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

        if Version(existing_package.version) <= version:
            return jsonify({"error": "Invalid package version, version too low"}), 409

    name = str(name).lower()

    if not name.isalpha():
        return jsonify({"error": "Package name must be alphabetic"}), 400

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


@app.route("/api/refresh-key", methods=["POST"])
@limiter.limit("10 per hour")
def refresh_api_key():
    """Endpoint to refresh an API key."""
    api_key = request.headers.get("X-API-Key")
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    user.api_key = str(uuid.uuid4())
    db.session.add(user)
    db.session.commit()

    return jsonify({"key": user.api_key}), 200


@app.route("/package/<package_name>")
@cache.cached(timeout=30)
def package_detail(package_name):
    """Package details endpoint."""
    package = Package.query.filter_by(name=package_name).first()
    if package:
        latest_release = package.latest_release  # pylint: disable=no-member
        if not latest_release:
            return render_template("notfound.html"), 404
        author = User.query.filter_by(id=package.author_id).first()
        if author:
            return render_template(
                "package.html",
                package=package,
                author_name=author.username,
                latest_release=latest_release,
            )
        return render_template(
            "package.html", package=package, latest_release=latest_release
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

        return client.presigned_get_object(
            PACKAGES_BUCKET, release.file_path, expires=timedelta(minutes=1)
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

        return client.presigned_get_object(
            PACKAGES_BUCKET, release.file_path, expires=timedelta(minutes=1)
        )
    return "Package not found", 404


@app.route("/")
@cache.cached(timeout=30)
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
            Package.download_count.label("total_downloads"),
        )
        .order_by(db.desc(Package.download_count))
        .limit(10)
        .all()
    )
    return render_template("index.html", top_packages=top_packages)


@app.route("/dashboard")
@limiter.limit("30 per minute")
def dashboard():
    """User dashboard endpoint for authenticated users."""
    if not github.authorized:
        return redirect(url_for("github.login"))

    account_info = github.get("/user")
    if account_info.ok:
        account_data = account_info.json()
        user = User.query.filter_by(github_id=account_data["id"]).first()
        if not user:
            user = User(
                github_id=account_data["id"],  # type: ignore
                username=account_data["login"],  # type: ignore
                api_key=str(uuid.uuid4()),  # type: ignore
            )
            db.session.add(user)
            db.session.commit()
        elif not user.api_key:
            user.api_key = str(uuid.uuid4())
            db.session.commit()

        user_packages = Package.query.filter_by(author_id=user.id).all()
        return render_template(
            "dashboard.html",
            user=account_data,
            user_packages=user_packages,
            api_key=user.api_key,
        )
    return "Failed to fetch user info.", 500


@app.route("/logout")
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for("home"))


@app.route("/static/<path:filename>")
def staticfiles(filename):
    """Serve static files."""
    return app.send_static_file(filename)


@app.context_processor
def inject_github():
    """Inject github object into all templates"""
    return {"github": github}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    if not client.bucket_exists(PACKAGES_BUCKET):
        client.make_bucket(PACKAGES_BUCKET)
    app.run(host="localhost", port=5000, ssl_context=("cert.pem", "key.pem"))
