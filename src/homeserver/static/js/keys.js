"use strict";

export default function register_keys(cb) {
    document.addEventListener("keydown", cb);
    document.addEventListener("keyup", cb);
}
