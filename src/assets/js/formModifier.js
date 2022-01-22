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

 		startSelect.options[startSelect.options.length] = new Option(stations[i] + " ("+ i+ ")"  , i);
 		

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

$(function(){
        $('#startSelect option').click(function(){

        endSelect = document.getElementById('endSelect');

       	$("#endSelect").empty();

        for (i = parseInt($(this).val())+1 ; i< stations.length ; i++)
        
        	endSelect.options[endSelect.options.length] = new Option(stations[i] + " ("+ i+ ")"  , i);

        });

        $("#price").text("$ 1");

       

    });

$('#startSelect').click(function () {  

	$('#buyButton').prop('disabled', false);
});

$('#endSelect').change(function () {   
   
	var firstValue = $("#endSelect").val();
	var secondValue = $("#startSelect").val();
	var numberOfStationCrossed = firstValue - secondValue;
	var price = "$ 1";

	if(numberOfStationCrossed >= 5 && numberOfStationCrossed < 13 )
		price = "$ 2";
	else
		if(numberOfStationCrossed >= 13)
			price = "$ 3";

	$("#price").text(price);

	$('#buyButton').prop('disabled', false);

});