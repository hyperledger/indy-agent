function removeElementById(id) {
    // removes element from DOM by its ID
    var element = document.getElementById(id);
    element.parentNode.removeChild(element);
}

function getTodayDate() {
    var tdate = new Date();
    var dd = tdate.getDate(); //yields day
    var MM = tdate.getMonth(); //yields month
    var yyyy = tdate.getFullYear(); //yields year

    var s = tdate.getSeconds();
    var m = tdate.getMinutes();
    var h = tdate.getHours();

    var currentDate = dd + "-" + (MM + 1) + "-" + yyyy + " " + h + ":" + m + ":" + s;

    return currentDate;
}