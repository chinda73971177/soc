from flask import Blueprint, render_template, redirect, url_for

ui = Blueprint("ui", __name__)


@ui.route("/")
def index():
    return render_template("index.html")


@ui.route("/login")
def login_page():
    return render_template("index.html")
