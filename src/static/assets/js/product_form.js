$("#button").on("click", ev => {
    ev.preventDefault();
    const form = document.getElementById("form");
    const action = form.action;
    $.ajax(`${action}?${new URLSearchParams(new FormData(form)).toString()}`, {
        method: "GET",
        error: responseObject => {
            let msg = responseObject.message;
            let type = "error";
            showPopupMessage(type, msg);
        },
        success: responseObject => {
            let msg = responseObject.message;
            let type = "success";
            showPopupMessage(type, msg);
        }
    });
    setTimeout(() => {
        window.location.href = "/products";
    }, 2500);
});