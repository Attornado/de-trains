$(function() {
    $("#refundBtn").on("click", ev => {
        ev.preventDefault();
        $.ajax("refund_ticket?ticket_id=" + $("#ticketId").val(), {
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
});