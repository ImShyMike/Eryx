"""Web IDE for Eryx."""

import io
import re
import time
import uuid
from contextlib import redirect_stdout

from colorama import Fore
from flask import Flask, abort, jsonify, render_template, request

from eryx.__init__ import CURRENT_VERSION
from eryx.frontend.lexer import tokenize
from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
parser = Parser()
environments = {}

# https://stackoverflow.com/questions/19212665/python-converting-ansi-color-codes-to-html
COLOR_DICT = {
    "31": ["hotpink", "mediumvioletred"],
    "32": ["limegreen", "darkgreen"],
    "33": ["gold", "darkgoldenrod"],
    "34": ["cyan", "teal"],
    "35": ["hotpink", "mediumvioletred"],
    "36": ["cyan", "teal"],
    "37": ["white", "silver"],
}

COLOR_REGEX = re.compile(r"\[(?P<arg_1>\d+)(;(?P<arg_2>\d+)(;(?P<arg_3>\d+))?)?m")

TEMPLATE = '<span style="color: {}">'


def ansi_to_html(text):
    """Format ANSI color codes to HTML with reduced DOM lag."""

    def single_sub(match):
        argsdict = match.groupdict()
        if argsdict["arg_3"] is None:
            if argsdict["arg_2"] is None:
                color = argsdict["arg_1"]
            else:
                color = argsdict["arg_1"]
        else:
            color = argsdict["arg_2"]

        if color == "39":
            return "</span>"

        color_name = COLOR_DICT[color][0]
        return TEMPLATE.format(color_name)

    return COLOR_REGEX.sub(single_sub, text).replace("\u001b", "")


# ========


class TokenList:
    """List of tokens to use with the pretty printer."""

    def __init__(self, tokens: list):
        self.tokens = tokens


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


@app.route("/<path>", methods=["POST"])
def handle_actions(path):
    """Handle all IDE actions."""
    if path not in ["tokenize", "ast", "run", "result"]:
        abort(404)

    request_json = request.get_json()
    source_code = request_json["source_code"]
    if path == "tokenize":
        try:
            tokens = tokenize(source_code)
        except RuntimeError as e:
            return jsonify({"error": ansi_to_html(Fore.RED + str(e))})
        return jsonify(
            {"result": ansi_to_html(pprint(TokenList(tokens), print_output=False))}
        )

    try:
        ast_nodes = parser.produce_ast(source_code)
        if path == "ast":
            return jsonify(
                {"result": ansi_to_html(pprint(ast_nodes, print_output=False))}
            )
    except RuntimeError as e:
        return jsonify({"error": ansi_to_html(Fore.RED + str(e))})
    try:
        env = None
        if "env_uuid" in request_json:
            env_uuid = request_json["env_uuid"]
            env = environments.get(env_uuid)
        env = env["env"] if env else Environment()
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            result = evaluate(ast_nodes, env)
            if path == "result":
                return jsonify(
                    {"result": ansi_to_html(pprint(result, print_output=False))}
                )
    except RuntimeError as e:
        return jsonify({"error": ansi_to_html(Fore.RED + str(e))})

    if path == "run":
        captured_output = output_buffer.getvalue()
        return jsonify({"result": ansi_to_html(captured_output)})


@app.route("/repl", methods=["POST", "DELETE"])
def repl():
    """REPL route."""
    if request.method == "POST":
        environment = Environment()
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


def start_ide(host="0.0.0.0", port=80):
    """Start the web IDE."""
    app.run(host=host, port=port, debug=False, use_reloader=False)


@app.before_request
def before_req_handler():
    """Delete expired environments when a request is received."""
    for env_uuid, env_data in environments.items():
        if time.time() > env_data["expiry"]:
            del environments[env_uuid]


if __name__ == "__main__":
    start_ide()
