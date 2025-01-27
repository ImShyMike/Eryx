"""Web IDE for Eryx."""

import io
import re
import time
import uuid
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import List

from colorama import Fore
from flask import Flask, abort, jsonify, render_template, request

from eryx.__init__ import CURRENT_VERSION
from eryx.frontend.lexer import Token, tokenize
from eryx.frontend.parser import Parser
from eryx.frontend.transpiler import transpile
from eryx.runtime.environment import Environment, get_value
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 600
parser = Parser()
environments = {}


@dataclass()
class Config:
    """Web IDE configuration class."""

    disable_file_io: bool = False


config = Config()

# https://stackoverflow.com/questions/19212665/python-converting-ansi-color-codes-to-html
COLOR_DICT = {
    "31": ["hotpink"],
    "32": ["limegreen"],
    "33": ["gold"],
    "34": ["cyan"],
    "35": ["hotpink"],
    "36": ["cyan"],
    "37": ["white"],
}

COLOR_REGEX = re.compile(r"\[(?P<arg>\d+)m")

TEMPLATE = '<span style="color: {}">'


def ansi_to_html(text):
    """Format ANSI text with color codes to HTML while also escaping it."""

    text = escape_html(text)

    def single_sub(match):
        color = match.groupdict().get("arg", "39")

        if color == "39":
            return "</span>"

        color_name = COLOR_DICT[color][0]
        return TEMPLATE.format(color_name)

    return COLOR_REGEX.sub(single_sub, text).replace("\u001b", "")


# ========


@dataclass()
class TokenList:
    """List of tokens to use with the pretty printer."""

    tokens: List[Token]


def escape_html(text):
    """Escape a string"""
    escape_dict = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;"}

    return "".join(escape_dict.get(c, c) for c in text)


def refresh_env_uuid(env_uuid):
    """Refresh the expiry time of an environment."""
    environments[env_uuid]["expiry"] = time.time() + 600


def get_unique_uuid(dictionary):
    """Get a unique UUID that does not exist in dictionary."""
    while True:
        uid = uuid.uuid4().hex
        if uid not in dictionary:
            return uid


@app.route("/")
def index():
    """Main page."""
    return render_template("index.html", version=CURRENT_VERSION)


@app.route("/<action>", methods=["POST"])
def handle_actions(action):
    """Handle all IDE actions."""
    if action not in ["tokenize", "ast", "run", "result", "transpile"]:
        abort(404)

    request_json = request.get_json()
    source_code = request_json["source_code"]
    if action == "tokenize":
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            try:
                tokens = tokenize(source_code)
            except (RuntimeError, SystemExit) as e:
                if isinstance(e, SystemExit):
                    return jsonify(
                        {"error": ansi_to_html(Fore.RED + output_buffer.getvalue())}
                    )
                return jsonify({"error": ansi_to_html(Fore.RED + str(e))})
            return jsonify(
                {"result": ansi_to_html(pprint(TokenList(tokens), print_output=False))}
            )

    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        try:
            ast_nodes = parser.produce_ast(source_code)
            if action == "ast":
                return jsonify(
                    {"result": ansi_to_html(pprint(ast_nodes, print_output=False))}
                )
            if action == "transpile":
                return jsonify(
                    {
                        "result": ansi_to_html(
                            transpile(ast_nodes.body, return_value=True)
                        )
                    }
                )
        except (SyntaxError, RuntimeError, SystemExit) as e:
            if isinstance(e, SystemExit):
                return jsonify(
                    {"error": ansi_to_html(Fore.RED + output_buffer.getvalue())}
                )
            return jsonify({"error": ansi_to_html(Fore.RED + str(e))})
    try:
        env = None
        is_repl = False
        if "env_uuid" in request_json:
            env_uuid = request_json["env_uuid"]
            env = environments.get(env_uuid)
            is_repl = True
        env = env["env"] if env else Environment(disable_file_io=config.disable_file_io)
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            result = evaluate(ast_nodes, env)
            if action == "result":
                return jsonify(
                    {"result": ansi_to_html(pprint(result, print_output=False))}
                )
        if action == "run":
            output = output_buffer.getvalue()
            if is_repl and not output:
                return jsonify({"result": ansi_to_html(get_value(result))})
            return jsonify({"result": ansi_to_html(output)})
    except RuntimeError as e:
        return jsonify({"error": ansi_to_html(Fore.RED + str(e))})

    return jsonify({})


@app.route("/repl", methods=["POST", "DELETE"])
def repl():
    """REPL route."""
    if request.method == "POST":
        environment = Environment(disable_file_io=config.disable_file_io)
        env_uuid = get_unique_uuid(environments)
        environments[env_uuid] = {
            "env": environment,
            "expiry": time.time() + 600,
        }  # 10 minutes
        return jsonify({"env_uuid": env_uuid})

    # If method is DELETE
    if "envId" not in request.args:
        return jsonify({"error": "No environment UUID provided"})
    env_uuid = request.args["envId"]
    if env_uuid in environments:
        del environments[env_uuid]
    return jsonify({})


@app.route("/static/<path:path>", methods=["GET"])
def static_route(path):
    """Static file route."""
    return app.send_static_file(path)


@app.route("/favicon.ico")
def favicon():
    """Serve the favicon."""
    return app.send_static_file("eryx.ico")


def start_ide(host: str = "0.0.0.0", port: int = 80, disable_file_io: bool = False):
    """Start the web IDE."""
    config.disable_file_io = disable_file_io
    app.run(host=host, port=port, debug=False, use_reloader=False)


@app.before_request
def before_req_handler():
    """Delete expired environments when a request is received."""
    for env_uuid, env_data in environments.items():
        if time.time() > env_data["expiry"]:
            del environments[env_uuid]


if __name__ == "__main__":
    start_ide()
