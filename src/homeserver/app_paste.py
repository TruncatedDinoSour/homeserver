#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""public sqlite3-based pastebin"""

from typing import Any

import sqlalchemy  # type: ignore
from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from werkzeug.wrappers.response import Response

from . import util
from .subapp_res import paste_res

paste: Blueprint = Blueprint("paste", __name__)
DB: dict[str, Any] = {}


def prep_paste(_) -> None:
    DB["engine"] = sqlalchemy.create_engine(util.sqlite_db_path("paste"))  # type: ignore
    DB["base"] = declarative_base()

    class Paste(DB["base"]):  # type: ignore
        __tablename__: str = "pastes"

        tid: sqlalchemy.Column = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
        content: sqlalchemy.Column = sqlalchemy.Column(sqlalchemy.String)

        def __init__(
            self,
            tid: sqlalchemy.Column,
            content: sqlalchemy.Column,
        ) -> None:
            self.tid: sqlalchemy.Column = tid
            self.content: sqlalchemy.Column = content

    DB["base"].metadata.create_all(DB["engine"])
    DB["session"] = sqlalchemy.orm.Session(DB["engine"])  # type: ignore

    DB["paste"] = Paste


def get_paste_by_tid(tid: str) -> str | None:
    return DB["session"].query(DB["paste"].content).filter_by(tid=tid).first()


@paste.get("/")
def index() -> str:
    return render_template("paste/index.j2")


@paste.post("/")
def paste_content() -> Response:
    if "content" not in request.form:
        return redirect("/", 400)

    tid: str = ""
    ok: int = False

    while not ok:
        tid = paste_res.generate_id()

        try:
            util.exec_add(  # type: ignore
                DB["session"],
                DB["paste"](
                    tid=tid,
                    content=request.form["content"],
                ),
            )
            ok = True
        except sqlalchemy.exc.IntegrityError:  # type: ignore
            DB["session"].rollback()

    return redirect(url_for("paste.index") + tid)


@paste.get("/<tid>")
def get_paste(tid: str) -> Response:
    return (
        util.redirect_view("paste.index", 404)
        if (paste := get_paste_by_tid(tid)) is None
        else util.plain_text_resp(paste.content)  # type: ignore
    )


@paste.route("/<tid>", methods=["DELETE"])
def delete_paste(tid: str) -> tuple[str, int]:
    status: int = 404

    if get_paste_by_tid(tid) is not None:
        util.exec_commit(  # type: ignore
            DB["session"],
            sqlalchemy.delete(DB["paste"]).where(DB["paste"].tid == tid),
        )
        status = 302

    return "", status


@paste.get("/list")
def list_pastes() -> str:
    return render_template(
        "paste/list.j2",
        pastes=tuple(
            DB["session"].execute(f"SELECT * FROM {DB['paste'].__tablename__!r}")
        ),
    )
