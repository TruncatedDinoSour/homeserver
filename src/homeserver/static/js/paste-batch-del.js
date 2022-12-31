"use strict";

function main() {
    document.querySelectorAll("a").forEach((a) => {
        a.addEventListener("click", (ev) => {
            ev.preventDefault();

            if (confirm(`Do you want to delete ${a.href} ?`))
                fetch(`${a.href}/delete`)
                    .then(() => a.parentElement.remove())
                    .catch((e) => alert(e));
            else window.open(a.href, "_blank");
        });
    });
}

document.addEventListener("DOMContentLoaded", main);
