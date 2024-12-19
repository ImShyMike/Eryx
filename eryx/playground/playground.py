"""Web playground for Eryx."""

import io
import json
import re
import uuid
from contextlib import redirect_stdout

from flask import Flask, jsonify, render_template, request

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
    "31": [(255, 105, 180), (128, 105, 180)],
    "32": [(57, 255, 20), (57, 128, 20)],
    "33": [(255, 193, 7), (128, 193, 7)],
    "34": [(0, 255, 255), (0, 128, 128)],
    "35": [(255, 105, 180), (128, 105, 180)],
    "36": [(0, 255, 255), (0, 128, 128)],
    "37": [(255, 255, 255), (192, 192, 192)],
}

COLOR_REGEX = re.compile(r"\[(?P<arg_1>\d+)(;(?P<arg_2>\d+)(;(?P<arg_3>\d+))?)?m")

BOLD_TEMPLATE = '<span style="color: rgb{}; font-weight: bolder">'
LIGHT_TEMPLATE = '<span style="color: rgb{}">'


def ansi_to_html(text):
    """Format ANSI color codes to HTML."""
    text = text.replace("[m", "</span>")

    def single_sub(match):
        argsdict = match.groupdict()
        if argsdict["arg_3"] is None:
            if argsdict["arg_2"] is None:
                color, bold = argsdict["arg_1"], 0
            else:
                color, bold = argsdict["arg_1"], int(argsdict["arg_2"])
        else:
            color, bold = argsdict["arg_2"], int(argsdict["arg_3"])

        if bold:
            return BOLD_TEMPLATE.format(COLOR_DICT[color][1])
        return LIGHT_TEMPLATE.format(COLOR_DICT[color][0])

    return COLOR_REGEX.sub(single_sub, text)


# ========


class TokenList:
    """List of tokens to use with the pretty printer."""

    def __init__(self, tokens: list):
        self.tokens = tokens


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


@app.route("/ast", methods=["POST"])
def ast():
    """Ast route."""
    source_code = request.get_json()["source_code"]
    try:
        ast_nodes = parser.produce_ast(source_code)
    except RuntimeError as e:
        return jsonify({"error": str(e)})
    return jsonify(
        {
            "result": ansi_to_html(pprint(ast_nodes, print_output=False))
            .replace("\n", "<br>")
            .replace("\u001b", "")
        }
    )


@app.route("/result", methods=["POST"])
def result_route():
    """Result route."""
    request_json = request.get_json()
    source_code = request_json["source_code"]
    try:
        ast_nodes = parser.produce_ast(source_code)
    except RuntimeError as e:
        return jsonify({"error": str(e)})
    try:
        env = None
        if "env_uuid" in request_json:
            env_uuid = request_json["env_uuid"]
            env = environments.get(env_uuid)
        env = env if env else Environment()
        result = evaluate(ast_nodes, env)
    except RuntimeError as e:
        return jsonify({"error": str(e)})
    return jsonify(
        {
            "result": ansi_to_html(pprint(result, print_output=False))
            .replace("\n", "<br>")
            .replace("\u001b", "")
        }
    )


@app.route("/run", methods=["POST"])
def run():
    """Run route."""
    request_json = request.get_json()
    source_code = request_json["source_code"]
    try:
        ast_nodes = parser.produce_ast(source_code)
    except RuntimeError as e:
        return jsonify({"error": str(e)})
    try:
        env = None
        if "env_uuid" in request_json:
            env_uuid = request_json["env_uuid"]
            env = environments.get(env_uuid)
        env = env if env else Environment()
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            evaluate(ast_nodes, env)
        captured_output = output_buffer.getvalue()
    except RuntimeError as e:
        return jsonify({"error": str(e)})
    return jsonify({"result": ansi_to_html(captured_output).replace("\n", "<br>")})


@app.route("/tokenize", methods=["POST"])
def tokenize_route():
    """Run route."""
    request_json = request.get_json()
    source_code = request_json["source_code"]
    try:
        tokens = tokenize(source_code)
    except RuntimeError as e:
        return jsonify({"error": str(e)})
    return jsonify(
        {
            "result": ansi_to_html(pprint(TokenList(tokens), print_output=False))
            .replace("\n", "<br>")
            .replace("\u001b", "")
        }
    )


@app.route("/repl", methods=["POST"])
def repl():
    """REPL route."""
    try:
        request_json = request.get_json()
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"})

    if not request_json:
        return jsonify({"error": "No JSON provided"})

    if "action" not in request_json:
        return jsonify({"error": "No action provided"})

    action = request_json["action"]

    if action == "token":
        environment = Environment()
        env_uuid = get_unique_uuid(environments)
        environments[env_uuid] = environment
        return jsonify({"env_uuid": env_uuid})

    if action == "delete":
        if "env_uuid" not in request_json:
            return jsonify({"error": "No environment UUID provided"})

        env_uuid = request_json["env_uuid"]
        if env_uuid in environments:
            del environments[env_uuid]
        return jsonify({})

    return jsonify({"error": "Invalid action"})


@app.route("/static/<path:path>", methods=["GET"])
def static_route(path):
    """Static file route."""
    return app.send_static_file(path)


@app.route("/favicon.ico")
def favicon():
    """Serve the favicon."""
    return app.send_static_file("favicon.ico")


def start_playground(host="0.0.0.0", port=80):
    """Start the web playground."""
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    start_playground()
