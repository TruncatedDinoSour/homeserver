#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""public sqlite3-based pastebin"""

from typing import Any

import sqlalchemy  # type: ignore
from flask import (Blueprint, make_response, redirect, render_template,
                   request, url_for)
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from werkzeug.wrappers.response import Response

from . import config
from .subapp_res import paste as paste_res

paste: Blueprint = Blueprint("paste", __name__)
DB: dict[str, Any] = {}


def get_paste_by_tid(tid: str) -> str | None:
    return DB["session"].query(DB["paste"].content).filter_by(tid=tid).first()


def prep_paste(_) -> None:
    DB["engine"] = sqlalchemy.create_engine(f"sqlite:///{config.DB_DIR}/paste.db?check_same_thread=False")
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


@paste.post("/")
def paste_content() -> Response:
    if "content" not in request.form:
        return redirect("/", 400)

    tid: str = ""
    ok: int = False

    while not ok:
        tid = paste_res.generate_id()

        try:
            DB["session"].add(
                DB["paste"](
                    tid=tid,
                    content=request.form["content"],
                )
            )
            DB["session"].commit()
            ok = True
        except sqlalchemy.exc.IntegrityError:
            DB["session"].rollback()

    return redirect(url_for("paste.index") + tid)


@paste.get("/")
def index() -> str:
    return render_template("paste.j2")


@paste.get("/<tid>")
def get_paste(tid: str) -> Response:
    if (paste := get_paste_by_tid(tid)) is not None:
        r: Response = make_response(paste[0], 200)
        r.mimetype = "text/plain"
        return r

    return redirect(url_for("paste.index"), 404)


@paste.get("/<tid>/delete")
def delete_paste(tid: str) -> Response:
    status: int = 404

    if get_paste_by_tid(tid) is not None:
        DB["session"].execute(
            sqlalchemy.delete(DB["paste"]).where(DB["paste"].tid == tid)
        )
        DB["session"].commit()
        status = 302

    return redirect(url_for("paste.index"), status)


@paste.get("/list")
def list_pastes() -> str:
    return render_template(
        "list-pastes.j2", pastes=DB["session"].execute(f"SELECT * FROM {DB['paste'].__tablename__!r}"),
    )
