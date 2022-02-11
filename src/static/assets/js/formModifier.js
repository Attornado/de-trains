var stations = new Array();

$(document).ready(function(){


	
	populateStation();


	daySelect = document.getElementById('daySelect');

	var dateToInsert = new Date();
	var dayFormat;

	for(i = 0; i < 30 ; i++){

		dayFormat = dateToInsert.getDate() + "/" + (dateToInsert.getMonth()+1) +  "/" + dateToInsert.getFullYear();

 		daySelect.options[daySelect.options.length] = new Option(dayFormat, dayFormat);
 		dateToInsert.setDate(dateToInsert.getDate() + 1);

 	}


 	startSelect = document.getElementById('startSelect');

	for(i = 0; i < stations.length ; i++){

 		startSelect.options[startSelect.options.length] = new Option(stations[i] + " ("+ i+ ")"  , stations[i]);
 		

 	}



});


function populateStation(){

	stations[0] = "Pozzuoli";
	stations[1] = "Bagnoli";
	stations[2] = "Cavalligeri";
	stations[3] = "Edenlandia";
	stations[4] = "Campi flegrei";
	stations[5] = "Leopardi";
	stations[6] = "Mergellina";
	stations[7] = "Amedeo";
	stations[8] = "Montesanto";
	stations[9] = "Cavour";
	stations[10] = "Garibaldi";
	stations[11] = "Gianturco";
	stations[12] = "SanGiovanni";
	stations[13] = "Pietrarsa";
	stations[14] = "Portici";
	stations[15] = "Ercolano";
	

}

function findNumOfStation(station){

	return stations.indexOf(station);


}

$(function(){
        $('#startSelect option').click(function(){

        endSelect = document.getElementById('endSelect');

       	$("#endSelect").empty();

        for (i = findNumOfStation($(this).val())+1 ; i< stations.length ; i++)
        
        	endSelect.options[endSelect.options.length] = new Option(stations[i] + " ("+ i+ ")"  , stations[i]);

        });

        $("#price").text("$ 1");

		$("#buyButton").on("click", ev => {
			ev.preventDefault();
			$.ajax("buy_ticket?date=" + $("#daySelect").val() + "&start_station=" + $("#startSelect").val() +
				"&end_station=" + $("#endSelect").val() + "&station_num=" + $("#hiddenNumStation").val(), {
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
					msg = "Ticket bought successfully! Ticket id is: " + ticket.Ticket__id + "\nTicket URI is: " + ticketUri;
					let type = "success";
					showPopupMessage(type, msg);
				}
			});
		});
});

$('#startSelect').click(function () {
	$("#hiddenNumStation").val(1);
	$('#buyButton').prop('disabled', false);
});

$('#endSelect').change(function () {   
   
	var firstValue = findNumOfStation($("#endSelect").val());
	var secondValue = findNumOfStation($("#startSelect").val());
	var numberOfStationCrossed = firstValue - secondValue;
	var price = "$ 1";

	if(numberOfStationCrossed >= 5 && numberOfStationCrossed < 13 )
		price = "$ 2";
	else
		if(numberOfStationCrossed >= 13)
			price = "$ 3";

	$("#price").text(price);

	$('#hiddenNumStation').val(numberOfStationCrossed);

	$('#buyButton').prop('disabled', false);

});