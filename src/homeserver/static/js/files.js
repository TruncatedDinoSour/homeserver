"use strict";

function main() {
    document.getElementById("signout").addEventListener("click", () =>
        fetch("account/signout", { method: "POST" })
            .then(() => window.location.reload())
            .catch((e) => alert(e))
    );

    document.getElementById("delete-account").addEventListener("click", () =>
        fetch("account", { method: "DELETE" })
            .then(() => window.location.reload())
            .catch((e) => alert(e))
    );
}

document.addEventListener("DOMContentLoaded", main);
