function displayObject(obj) {
    return JSON.stringify(obj, null, 4); // beautiful indented obj.
}
function history_format(msg_content){
    return {'date':getTodayDate(), 'msg':displayObject(msg.content)};
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
