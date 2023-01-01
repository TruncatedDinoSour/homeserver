#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""save files, privately"""

import os
import shutil
from html import escape as html_escape
from typing import Any
from urllib.parse import quote as url_escape

import flask
import sqlalchemy  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from werkzeug.wrappers.response import Response

from . import config, util

files: flask.Blueprint = flask.Blueprint("files", __name__)
DB: dict[str, Any] = {}


def prep_files(_) -> None:
    DB["engine"] = sqlalchemy.create_engine(util.sqlite_db_path("files-accounts"))  # type: ignore
    DB["base"] = declarative_base()

    class User(DB["base"]):  # type: ignore
        __tablename__: str = "users"

        username_hash: sqlalchemy.Column = sqlalchemy.Column(
            sqlalchemy.String, primary_key=True
        )
        pw_hash: sqlalchemy.Column = sqlalchemy.Column(sqlalchemy.String)
        pw_salt: sqlalchemy.Column = sqlalchemy.Column(
            sqlalchemy.String(config.SALT_SIZE)
        )

        def __init__(
            self,
            username_hash: sqlalchemy.Column,
            pw_hash: sqlalchemy.Column,
            pw_salt: sqlalchemy.Column,
        ) -> None:
            self.username_hash: sqlalchemy.Column = username_hash
            self.pw_hash: sqlalchemy.Column = pw_hash
            self.pw_salt: sqlalchemy.Column = pw_salt

    DB["base"].metadata.create_all(DB["engine"])
    DB["session"] = sqlalchemy.orm.Session(DB["engine"])  # type: ignore

    DB["user"] = User


def get_user_by_id(username_hash: str) -> Any:
    return (
        DB["session"].query(DB["user"]).filter_by(username_hash=username_hash).first()
    )


def get_fp(name: str) -> str:
    return os.path.join(config.FILES_DIR, name)


def get_ufp(path: str) -> str:
    return os.path.join(get_fp(flask.session["user-id"]), path)  # type: ignore


def rm(path: str) -> None:
    def os_rm(f: str) -> None:
        if os.path.exists(f):
            os.remove(f)

    shutil.rmtree(path, onerror=lambda *d: os_rm(d[1]))  # type: ignore


def generate_filetree(fp: str, d: str = "") -> str:
    cwd: str = os.getcwd()
    os.chdir(fp)

    listing: list[str] = os.listdir()

    d = url_escape(d, safe="/")
    final: str = (
        f'<li><a href="f/{d}">{html_escape(os.path.basename(d.rstrip("/")))}/</a></li>'
        if d
        else ""
    ) + "<ul>"

    if listing:
        for file in listing:
            final += (
                generate_filetree(file, d + file + "/")
                if os.path.isdir(file)
                else f'<li><a href="f/{d}{url_escape(file)}">{html_escape(file)}</a></li>'
            )

    os.chdir(cwd)

    final += "</ul>"

    return final if listing else ""


@files.get("/")
def index() -> Response | str:
    if not flask.session.get("user-id"):  # type: ignore
        return flask.redirect(flask.url_for("files.index") + "/account")

    return flask.render_template(
        "files/index.j2", files=generate_filetree(get_fp(flask.session["user-id"]))  # type: ignore
    )


@files.post("/")
def upload() -> Response:
    if not flask.session.get("user-id") or not flask.request.files:  # type: ignore
        return flask.redirect(flask.url_for("files.index"))

    for file in flask.request.files.getlist("file[]"):
        if not file.filename:  # type: ignore
            continue

        d: str = get_ufp(os.path.dirname(file.filename))  # type: ignore

        os.makedirs(d, exist_ok=True)
        file.save(os.path.join(d, os.path.basename(file.filename)))  # type: ignore

    return util.redirect_view("files.index")


@files.get("/f", defaults={"path": ""})
@files.get("/f/<path:path>")
def get_file(path: str) -> Response | str:
    if not path or not flask.session.get("user-id"):  # type: ignore
        return util.redirect_view("files.index")

    p: str = get_ufp(path)
    return (
        util.send_directory(p)
        if os.path.isdir(p)
        else flask.send_from_directory(os.getcwd(), p, as_attachment=True)  # type: ignore
    )


@files.get("/export")
def get_export() -> Response:
    return (
        util.redirect_view("files.index")
        if not flask.session.get("user-id")  # type: ignore
        else util.send_directory(get_fp(flask.session["user-id"]))  # type: ignore
    )


@files.route("/f", defaults={"path": ""}, methods=["DELETE"])
@files.route("/f/<path:path>", methods=["DELETE"])
def remove_file(path: str) -> Response | tuple[str, int]:
    if not path:
        return util.redirect_view("files.index")

    status: int = 404

    if flask.session.get("user-id"):  # type: ignore
        if os.path.exists(up := get_ufp(path)):
            rm(up)
            status = 200
    else:
        status = 401

    return "", status


@files.get("/account")
def account() -> Response | str:
    return (
        util.redirect_view("files.index")
        if flask.session.get("user-id")  # type: ignore
        else flask.render_template("files/account.j2")
    )


@files.post("/account/signout")
def signout() -> Response:
    if not flask.session.get("user-id"):  # type: ignore
        return util.redirect_view("files.index", 401)

    del flask.session["user-id"]
    return util.redirect_view("files.index")


@files.route("/account", methods=["DELETE"])
def delete_acc() -> tuple[str, int]:
    if not flask.session.get("user-id"):  # type: ignore
        return "", 401

    util.exec_commit(  # type: ignore
        DB["session"],
        sqlalchemy.delete(DB["user"]).where(
            DB["user"].username_hash == flask.session["user-id"]
        ),
    )

    rm(get_fp(flask.session["user-id"]))  # type: ignore

    del flask.session["user-id"]

    return "", 200


@files.post("/account/signup")
def signup() -> Response:
    if flask.session.get("user-id") or not flask.request.form.get("username"):  # type: ignore
        return util.redirect_view("files.index", 400)

    salt: str = util.random_string(config.SALT_SIZE)
    username_hash: str = util.insecure_hash(flask.request.form["username"])

    try:
        util.exec_add(  # type: ignore
            DB["session"],
            DB["user"](
                username_hash=username_hash,
                pw_hash=util.hashsalt_pw(
                    flask.request.form.get("password") or "", salt
                ),
                pw_salt=salt,
            ),
        )

        flask.session["user-id"] = username_hash
    except sqlalchemy.exc.IntegrityError:  # type: ignore
        DB["session"].rollback()
        return util.redirect_view("files.index", 401)

    os.makedirs(get_fp(username_hash), exist_ok=True)
    return util.redirect_view("files.index")


@files.post("/account/signin")
def signin() -> Response:
    if flask.session.get("user-id") or not flask.request.form.get("username"):  # type: ignore
        return util.redirect_view("files.index", 400)

    user: Any = get_user_by_id(util.insecure_hash(flask.request.form["username"]))

    if user is None:
        return util.redirect_view("files.index", 404)
    elif not util.hashsalt_pw_check(
        flask.request.form.get("password") or "", user.pw_hash, user.pw_salt
    ):
        return util.redirect_view("files.index", 401)

    flask.session["user-id"] = user.username_hash
    return util.redirect_view("files.index")
