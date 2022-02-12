/*
    //INPUT: type: tipo di messaggio da mostrare, msg: messaggio da mostrare, timeoutSec: tempo di scadenza del messaggio
    //OUTPUT: Mostra un messaggio pop-up di tipo type a fondo pagina, con messaggio msg, che viene nascosto dopo
              timeoutSec secondi. Non viene nascosto mai se timeoutSec=0.
*/
function showPopupMessage(type= "notice", msg= "", timeoutSec= 0){
    let $popupMessageBox = $(".popupBox");
    $popupMessageBox.removeClass((index, classListString) => {
        //splittiamo la classList in più stringhe
        let classList = classListString.split(" ");
        //filtriamole in modo da avere solo quelle che matchano con la regex ^.+(-popup)$
        classList = classList.filter(value => new RegExp("^.+(-popup)$").test(value));
        //riunifichiamo l'array in modo da ottenere la stringa delle classi da rimovere
        return classList.join(" ");
    });
    $popupMessageBox.addClass(type + "-popup"); //impostiamo la classe corrispondente al tipo di messaggio
    $popupMessageBox.find($popupMessageBox.prop("id") + " .msgContent").text(msg); //impostiamone il contenuto
    $popupMessageBox.addClass("visible"); //rendiamolo visibile
    if(timeoutSec !== 0)
        setTimeout(() => $popupMessageBox.removeClass("visible"), timeoutSec*1000);

}

$(function(){
    $(".popupBox .closeButton").on("click", ev => {
        $(".popupBox").removeClass("visible");
    });
});