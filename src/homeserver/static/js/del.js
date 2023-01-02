"use strict";

import register_keys from "./keys.js";

function on_long_press(element, callback) {
    let timer;

    element.addEventListener("touchstart", () => {
        timer = setTimeout(() => {
            timer = null;
            callback();
        }, 404);
    });

    function cancel() {
        clearTimeout(timer);
    }

    element.addEventListener("touchend", cancel);
    element.addEventListener("touchmove", cancel);
}

function main() {
    register_keys((e) => (window.ctrled = e.ctrlKey));

    function da(a) {
        if (confirm(`do you want to delete ${a.href} ?`))
            fetch(`${a.href}`, { method: "DELETE" })
                .then(() => {
                    let uc = a.parentElement.parentElement.children.length;
                    (window.del_cb ?? (() => a.parentElement.remove()))();
                    if (!(uc - 1)) window.location.reload();
                })
                .catch((e) => alert(e));
    }

    document.querySelectorAll("a").forEach((a) => {
        on_long_press(a, () => da(a));

        a.addEventListener("click", (ev) => {
            ev.preventDefault();

            if (window.ctrled) da(a);
            else window.open(a.href, "_blank");
        });
    });
}

document.addEventListener("DOMContentLoaded", main);
