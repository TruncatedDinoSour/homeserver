#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""homeserver config"""

import os
from secrets import SystemRandom

PROD: bool = os.environ.get("PROD") is not None

HOST: str = "0.0.0.0" if PROD else "127.0.0.1"
PORT: int = 80 if PROD else 8080

RANDOM: SystemRandom = SystemRandom()

# this get populated automatically, but you can add more if it cant detect your app as valid
SUBAPPS: dict[str, str] = {}

DB_DIR: str = "db"
FILES_DIR: str = os.path.join(DB_DIR, "files")

SALT_SIZE: int = 64
SECRET_KEY_SIZE: int = 4096

PASSWORD_HASH_ITER: int = 100000
PASSWORD_END: str = "$"

MAX_CONTENT_LENGTH: int = 10 * 1000 * 1000 * 1000  # 10 GB
