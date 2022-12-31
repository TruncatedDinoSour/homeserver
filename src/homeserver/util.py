#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""utilities for subapps"""

from typing import Any

import sqlalchemy  # type: ignore
from flask import make_response, redirect, url_for
from werkzeug.wrappers.response import Response

from . import config


def sqlite_db_path(name: str) -> str:
    """returns a nice url for an sqlite3 db"""

    return f"sqlite:///{config.DB_DIR}/{name}.db?check_same_thread=False"


def plain_text_resp(text: str) -> Response:
    """returns a plain-text-only response"""

    r: Response = make_response(text, 200)
    r.mimetype = "text/plain"
    return r


def redirect_view(slug: str, code: int = 302) -> Response:
    """redirect to view rather than to a URL"""

    return redirect(url_for(slug), code=code)


def exec_commit(
    session: sqlalchemy.orm.Session,  # type: ignore
    query: Any,
) -> None:
    """execute a query on an SQL database and commit after"""

    session.execute(query)
    session.commit()
