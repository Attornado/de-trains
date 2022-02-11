$("#withdrawBtn").on("click", ev => {
    alert("dcc");
    ev.preventDefault();
    $.ajax("refund_ticket?ticket_id=" + $("#address_to_admin").val(), {
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
});

$("#useBtn").on("click", ev => {
    alert("dcc");
    ev.preventDefault();
    $.ajax("refund_ticket?ticket_id=" + $("#ticket_to_use").val(), {
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
});


$("#promoteBtn").on("click", ev => {
    alert("dcc");
    ev.preventDefault();
    $.ajax("refund_ticket?ticket_id=" + $("#address_to_admin").val(), {
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
});