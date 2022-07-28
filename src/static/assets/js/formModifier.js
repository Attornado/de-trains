$(document).ready(function(){
	let daySelect = document.getElementById('daySelect');
	let dateToInsert = new Date();
	let dayFormat;

	for(let i = 0; i < 365 ; i++){
		let month = (dateToInsert.getMonth() + 1);
		if (month < 10){
			month = "0" + month;
		}
		let day = dateToInsert.getDate();
		if (day < 10){
			day = "0" + day
		}
		dayFormat = dateToInsert.getFullYear() + "-" + month +  "-" + day;
 		daySelect.options[daySelect.options.length] = new Option(dayFormat, dayFormat);
 		dateToInsert.setDate(dateToInsert.getDate() + 1);
 	}
});

$(function(){

	$(".buy-btn").on("click", ev => {
		ev.preventDefault();
		$.ajax("buy_ticket?" +
			"start_date=" + $(ev.target).parent().find(".start_date").val() +
			"&origin=" + $(ev.target).parent().find(".origin").val() +
			"&destination=" + $(ev.target).parent().find(".destination").val() +
			"&end_date=" + $(ev.target).parent().find(".end_date").val()  +
			"&train_class=" + $(ev.target).parent().find(".train_class").val() +
			"&train_type=" + $(ev.target).parent().find(".train_type").val() +
			"&fare=" + $(ev.target).parent().find(".fare").val() +
			"&db_id=" + $(ev.target).parent().find(".db_id").val() +
			"&price=" + $(ev.target).parent().find(".price").val(), {
			method: "GET",
			error: responseObject => {
				let msg = responseObject.message;
				let type = "error";
				showPopupMessage(type, msg);
			},
			success: responseObject => {
				let msg;
				let ticket = JSON.parse(responseObject.ticket);
				let ticketUri = responseObject.ticket_uri
				msg = "Ticket " + ticket._Ticket__id + " bought successfully! \nURI: " + ticketUri;
				let type = "success";
				showPopupMessage(type, msg);
			}
		});
	});
});