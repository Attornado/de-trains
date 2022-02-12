$(function(){

    $("#withdrawBtn").on("click", ev => {
        ev.preventDefault();
        $.ajax("admin/withdraw?address=" + $("#address_to_deposit").val(), {
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
        ev.preventDefault();
        $.ajax("admin/register_admin?address=" + $("#address_to_admin").val(), {
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

    /*$("#removeAdminBtn").on("click", ev => {
        ev.preventDefault();
        $.ajax("admin/remove_admin?address=" + $("#address_to_remove_admin").val(), {
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
    }); */

    $("#registerUsageSetterBtn").on("click", ev => {
        ev.preventDefault();
        $.ajax("admin/register_ticket_usage_setter?address=" + $("#create_usage_setter_addr").val(), {
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

    /*
    $("#removeUsageSetterBtn").on("click", ev => {
        ev.preventDefault();
        $.ajax("admin/remove_ticket_usage_setter?address=" + $("#remove_usage_setter_addr").val(), {
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
    }); */

});