
function addRequestTable(data) {
    var table = '';
    table += '<table class="table table-success table-striped">';
    table += '<thead>';
    table += '<tr>';
    table += '<th scope="col">Request ID</th>';
    table += '<th scope="col">UT code</th>';
    table += '<th scope="col">App Raised</th>';
    table += '<th scope="col">Request Type</th>';
    table += '<th scope="col">Status</th>';
    table += '<th scope="col">Time Raised</th>';
    table += '<th scope="col">Raised by</th>';

    table += '</tr> </thead><tbody>';
    $.each(data, function (i, obj) {
        table += '<tr>';
        table += '<th scope="row">' + obj.requestID + '</th>'
        table += '<td>' + obj.uid + '</td>';
        table += '<td>' + obj.selectApp + '</td>';
        table += '<td>' + obj.requestType + '</td>';
        table += '<td>' + obj.status + '</td>';
        table += '<td>' + obj.requestRaised + '</td>';
        table += '<td>' + obj.raisedBy + '</td>';
        table += '</tr>';
    })

    table += '</tbody></table>'
    return table

}
$(document).ready(function () {

    requestTable = addRequestTable(data)
    $('#requestAvailable').append(requestTable);

})
