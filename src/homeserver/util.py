#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""utilities for subapps"""

import base64
import hashlib
import io
import os
import tarfile
from typing import Any

import flask
import sqlalchemy  # type: ignore
from werkzeug.wrappers.response import Response

from . import config


def sqlite_db_path(name: str) -> str:
    """returns a nice url for an sqlite3 db"""

    return f"sqlite:///{config.DB_DIR}/{name}.db?check_same_thread=False"


def plain_text_resp(text: str) -> Response:
    """returns a plain-text-only response"""

    r: Response = flask.make_response(text, 200)
    r.mimetype = "text/plain"
    return r


def redirect_view(slug: str, code: int = 302) -> Response:
    """redirect to view rather than to a URL"""

    return flask.redirect(flask.url_for(slug), code=code)


def exec_commit(
    session: sqlalchemy.orm.Session,  # type: ignore
    query: Any,
) -> None:
    """execute a query on an SQL database and commit after"""

    session.execute(query)  # type: ignore
    session.commit()  # type: ignore


def exec_add(
    session: sqlalchemy.orm.Session,  # type: ignore
    what: Any,
) -> None:
    """add an entry into the database and commit after"""

    session.add(what)  # type: ignore
    session.commit()  # type: ignore


def insecure_hash(data: str) -> str:
    """insecure hash"""

    return hashlib.sha224(data.encode()).hexdigest()


def secure_hash(data: str, iterations: int = 10) -> str:
    """securely hash data"""

    final_hash = hashlib.sha512(data.encode())
    for _ in range(iterations):
        final_hash = hashlib.sha512(final_hash.digest())

    return final_hash.hexdigest()


def random_string(size: int = 64) -> str:
    """return a random string of size"""

    return (
        base64.b85encode(config.RANDOM.randbytes(size * 2)).decode().ljust(size)[:size]
    )


def hashsalt_pw(pw: str, salt: str) -> str:
    """hash and salt pw"""

    return secure_hash(
        pw + config.PASSWORD_END + salt,
        config.PASSWORD_HASH_ITER,
    )


def hashsalt_pw_check(pw: str, pw_hash: str, salt: str) -> bool:
    """check if salted and hashed pw is correct"""

    return hashsalt_pw(pw, salt) == pw_hash


def send_directory(path: str) -> Response:
    """send a directory"""

    arcname: str = os.path.basename(path.rstrip("/"))[:240]

    bio: io.BytesIO = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w:gz") as targz:
        targz.add(path, arcname=arcname)
    bio.seek(0)

    return flask.send_file(  # type: ignore
        bio,
        mimetype="application/x-compressed-tar",
        as_attachment=True,
        download_name=arcname + ".tar.gz",
    )
