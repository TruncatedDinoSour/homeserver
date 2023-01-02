"use strict";

function main() {
    document.getElementById("signout").addEventListener("click", () =>
        fetch("account/signout", { method: "POST" })
            .then(() => window.location.reload())
            .catch((e) => alert(e))
    );

    document.getElementById("delete-account").addEventListener("click", () => {
        if (confirm("are you sure you want to delete your account ?"))
            fetch("account", { method: "DELETE" })
                .then(() => window.location.reload())
                .catch((e) => alert(e));
    });
}

document.addEventListener("DOMContentLoaded", main);
