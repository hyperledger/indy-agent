function removeElementById(id) {
    // removes element from DOM by its ID
    var element = document.getElementById(id);
    element.parentNode.removeChild(element);
}

function removeRow(connName) {
    removeElementById(connName + '_row');
}

function displayObject(obj) {
    return JSON.stringify(obj, null, 4); // beautiful indented obj.
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

function showTab(id) {
        let i;
        let x = document.getElementsByClassName("tab");
        for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
        }
        document.getElementById(id).style.display = "block";
    }