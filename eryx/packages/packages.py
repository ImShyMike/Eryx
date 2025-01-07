"""Module for managing Eryx packages."""

import io
import json
import os
import shutil
import zipfile

import requests
import toml

packages_dir = os.path.dirname(os.path.realpath(__file__))


CFG_FILE = "packages.json"
INSTALLED_PACKAGES_LOC = "installed"
DEFAULT_SERVER = "https://eryx-packages.shymike.tech"


def get_config() -> dict:
    """Initialize the package manager."""
    config_path = os.path.join(packages_dir, CFG_FILE)
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf8") as file:
            file.write("{}")

    try:
        with open(config_path, "r", encoding="utf8") as file:
            config = json.load(file)
    except json.JSONDecodeError:
        config = {}

    return config


class Config:
    """Class for managing the configuration file."""

    def __init__(self):
        self.config = get_config()

        if not self.config.get("installed_packages"):
            self.config["installed_packages"] = {}

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value
        with open(os.path.join(packages_dir, CFG_FILE), "w", encoding="utf8") as file:
            json.dump(self.config, file)

    def save(self) -> None:
        """Save the configuration file."""
        with open(os.path.join(packages_dir, CFG_FILE), "w", encoding="utf8") as file:
            json.dump(self.config, file)


CONFIG = Config()


def unzip_safe_from_buffer(
    path: str, zip_buffer: bytes, max_files: int = 100, max_size: int = 10**7
):  # 10MB
    """Unzip a buffer safely from a buffer."""
    # Process the zip buffer
    with zipfile.ZipFile(io.BytesIO(zip_buffer), "r") as zip_ref:
        # Ensure that the number of files and the total uncompressed size are within limits
        file_count = len(zip_ref.infolist())
        if file_count > max_files:
            raise ValueError(
                f"Too many files in the zip archive: {file_count} > {max_files}"
            )

        total_size = sum(file.file_size for file in zip_ref.infolist())
        if total_size > max_size:
            raise ValueError(
                f"Total size of uncompressed files exceeds limit: {total_size} > {max_size}"
            )

        # Extract files if safe
        zip_ref.extractall(path)


def get_folder_size(path: str) -> int:
    """Get the size of a folder."""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def install(package: str, server: str, upgrade: bool) -> None:
    """Install an Eryx package."""

    if not server.startswith("http://") and not server.startswith("https://"):
        server = "https://" + server

    if not server.endswith("/"):
        server += "/"

    print(f"Installing package '{package}'")

    if "@" not in package:
        package_name = package
        if CONFIG["installed_packages"] and package in CONFIG["installed_packages"]:
            if not upgrade:
                print(f"Package '{package}' already installed")
                return

            package_path = os.path.join(
                packages_dir, INSTALLED_PACKAGES_LOC, package_name
            )
            if upgrade and os.path.exists(package_path):
                shutil.rmtree(package_path)
                del CONFIG["installed_packages"][package_name]

            try:
                if not os.path.exists(
                    os.path.join(packages_dir, INSTALLED_PACKAGES_LOC)
                ):
                    os.mkdir(os.path.join(packages_dir, INSTALLED_PACKAGES_LOC))
            except FileNotFoundError:
                pass

        try:
            response = None
            response = requests.get(f"{server}download/{package}", timeout=5)
            response.raise_for_status()
            version = (
                response.url.split("/")[-1].split("?")[0].rsplit(".", 1)[0] or "error"
            )

            package_file = response.content
        except requests.RequestException as e:
            if response:
                if response.status_code == 404:
                    print(f"Package '{package}' not found")
                else:
                    print(f"Error downloading package '{package}': {e}")
            else:
                print("Error downloading package: ", e)
            return

    else:
        package_name, version = package.split("@")

        if CONFIG["installed_packages"] and package in CONFIG["installed_packages"]:
            if not upgrade:
                print(
                    f"Package '{package}' already installed "
                    f"(installed version: {CONFIG['installed_packages'][package_name]})"
                )
                return

            package_path = os.path.join(
                packages_dir, INSTALLED_PACKAGES_LOC, package_name
            )
            if upgrade and os.path.exists(package_path):
                shutil.rmtree(package_path)
                del CONFIG["installed_packages"][package_name]

            try:
                if not os.path.exists(
                    os.path.join(packages_dir, INSTALLED_PACKAGES_LOC)
                ):
                    os.mkdir(os.path.join(packages_dir, INSTALLED_PACKAGES_LOC))
            except FileNotFoundError:
                pass

        try:
            response = None
            response = requests.get(
                f"{server}download/{package_name}/{version}", timeout=5
            )
            response.raise_for_status()
            package_file = response.content
        except requests.RequestException as e:
            if response:
                if response.status_code == 404:
                    try:
                        versions_response = requests.get(
                            f"{server}api/versions/{package_name}", timeout=5
                        )
                        versions_response.raise_for_status()
                        versions = versions_response.json().get("versions", [])
                        print(
                            f"Version '{version}' not found for package '{package_name}'"
                        )
                        print("Available versions:", ", ".join(versions))
                    except requests.RequestException:
                        print(f"Package '{package_name}' not found")
                else:
                    print(f"Error downloading package '{package_name}@{version}': {e}")
            else:
                print("Error downloading package: ", e)
            return

    CONFIG["installed_packages"][package_name] = version
    CONFIG.save()

    if not os.path.exists(os.path.join(packages_dir, INSTALLED_PACKAGES_LOC)):
        os.mkdir(os.path.join(packages_dir, INSTALLED_PACKAGES_LOC))

    unzip_safe_from_buffer(
        os.path.join(packages_dir, INSTALLED_PACKAGES_LOC, package_name), package_file
    )

    print(f"Package '{package_name}@{version}' installed successfully")


def uninstall(package: str) -> None:
    """Uninstall an Eryx package."""

    if not CONFIG["installed_packages"]:
        print("No packages installed")
        return

    if "@" in package:
        package_name, version = package.split("@")
    else:
        package_name = package
        version = None

    print(f"Uninstalling package '{package}'")

    if package not in CONFIG["installed_packages"]:
        if not version:
            print(f"Package '{package}' not installed")
            return
        if (
            package_name in CONFIG["installed_packages"]
            and CONFIG["installed_packages"][package_name] != version
        ):
            print(f"Package '{package_name}@{version}' not installed")
            return

    del CONFIG["installed_packages"][package_name]
    CONFIG.save()

    if not os.path.exists(os.path.join(packages_dir, INSTALLED_PACKAGES_LOC)):
        os.mkdir(os.path.join(packages_dir, INSTALLED_PACKAGES_LOC))

    try:
        shutil.rmtree(os.path.join(packages_dir, INSTALLED_PACKAGES_LOC, package_name))
    except FileNotFoundError:
        pass

    print(f"Package '{package}' uninstalled successfully")


def list_packages() -> None:
    """List all installed packages."""
    if not CONFIG["installed_packages"]:
        print("No packages installed")
        return

    print("Installed packages:")
    for package in CONFIG["installed_packages"]:
        print(f"  {package[0]}@{package[1]}")


def upload_package(package_folder: str, server: str) -> None:
    """Upload a package to the server."""

    if not server.startswith("http://") and not server.startswith("https://"):
        server = "https://" + server

    if not server.endswith("/"):
        server += "/"

    key = get_key(server)

    print(f"Uploading package from '{package_folder}'")

    if not os.path.exists(package_folder):
        print(f"Directory '{package_folder}' does not exist")
        return

    if not os.path.isdir(package_folder):
        print(f"'{package_folder}' is not a directory")
        return

    # Perform file checks
    if not os.path.exists(os.path.join(package_folder, "package.toml")):
        print("Missing 'package.toml' file")
        return

    if not os.path.exists(os.path.join(package_folder, "main.eryx")):
        print("Missing 'main.eryx' directory (package entry point)")
        return

    if get_folder_size(package_folder) > 10**7:
        print("Unzipped package too large: >10MB")
        return

    with open(
        os.path.join(package_folder, "package.toml"), "r", encoding="utf8"
    ) as file:
        try:
            package_data = toml.load(file)
        except toml.TomlDecodeError:
            print("Error decoding 'package.toml'")
            return

    if not package_data.get("package"):
        print("Missing 'package' table in 'package.toml'")
        return

    package_data = package_data["package"]

    package_name = str(package_data.get("name"))
    if not package_name:
        print("Missing 'name' field in 'package.toml'")
        return

    if not package_name.isalnum():
        print("Invalid package name, must be alphanumeric")
        return

    package_version = str(package_data.get("version"))
    if not package_version:
        print("Missing 'version' field in 'package.toml'")
        return

    if not package_data.get("description"):
        print("Missing 'description' field in 'package.toml'")
        return

    # Zip the package
    shutil.make_archive(os.path.join(packages_dir, "temp"), "zip", package_folder)

    with open(os.path.join(packages_dir, "temp.zip"), "rb") as package_file:
        files = {"package_file": package_file.read()}

        if len(files["package_file"]) > 10**7:
            print("Zipped package too large: >1MB")
            return

        # Upload the package
        try:
            response = None
            response = requests.post(
                f"{server}/api/upload",
                headers={"X-API-Key": str(key)},
                files=files,
                timeout=5,
            )
            response.raise_for_status()
            print(f"Package '{package_name}@{package_version}' uploaded successfully")
        except requests.RequestException:
            if response:
                if response.status_code in (400, 401, 403):
                    CONFIG["api_key"] = None
                    print("Invalid API key")
                else:
                    try:
                        print(response.json()["error"])
                    except json.JSONDecodeError:
                        print("Error uploading package: ", response.text)
            else:
                print("Error uploading package")

    os.remove(os.path.join(packages_dir, "temp.zip"))


def delete_package(package: str, server: str) -> None:
    """Delete a package from the server."""

    if not server.startswith("http://") and not server.startswith("https://"):
        server = "https://" + server

    if not server.endswith("/"):
        server += "/"

    key = get_key(server)

    while True:
        answer = input(
            f"Are you sure you want to delete '{package}'\n"
            "THIS ACTION IS PERMANENT AND CANNOT BE UNDONE\n(y/N): "
        )
        if answer.lower() in ["y", "yes"]:
            break
        if answer.lower() in ["n", "no", ""]:
            print("Deletion cancelled")
            return
        print("Invalid input")

    try:
        response = None
        response = requests.post(
            f"{server}/api/delete",
            headers={"X-API-Key": str(key), "Content-Type": "application/json"},
            data=json.dumps({"package": package}).encode("utf-8"),
            timeout=5,
        )
        response.raise_for_status()
        print(f"Package '{package}' deleted successfully")
    except requests.RequestException:
        if response:
            if response.status_code == 401:
                CONFIG["api_key"] = None
            try:
                print(response.json()["error"])
            except json.JSONDecodeError:
                print("Error uploading package: ", response.text)
        else:
            print("Error uploading package")
        return


def get_key(server: str) -> str | None:
    """Get and save the API key."""

    cfg = get_config()

    if cfg.get("api_key"):
        return cfg["api_key"]

    print(f"\nPlease visit the following url to get your API key:\n{server}dashboard")

    key = input("\nAPI Key: ")
    with open(os.path.join(packages_dir, CFG_FILE), "w", encoding="utf8") as file:
        cfg["api_key"] = key
        json.dump(cfg, file)

    return key
