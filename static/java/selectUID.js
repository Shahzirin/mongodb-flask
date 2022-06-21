function addRoleTable(data2) {
    var table = '';
    table += '<table class="table table-success table-striped">';
    table += '<thead>';
    table += '<tr>';
    table += '<th scope="col">Project</th>';
    table += '<th scope="col">Role</th>';
    table += '<th scope="col">Assigned Employee</th>';
    table += '</tr> </thead><tbody>';
    $.each(data2, function (i, obj) {
        console.log(obj.project)
        table += '<tr>';
        table += '<th scope="row">' + obj.project + '</th>'
        table += '<td>' + obj.role + '</td>';
        table += '<td>' + obj.uid + '</td>';
        table += '</tr>';
    })

    table += '</tbody></table>'
    return table

}

$(document).ready(function () {
    $('#addOn2').hide();
    $.each(data, function (i, obj) {
        var x = document.createElement("OPTION");
        x.setAttribute("value", obj.uid);
        var t = document.createTextNode("UT Code: " + obj.uid + " Name: " + obj.name);
        x.appendChild(t);
        document.getElementById("selectUID").appendChild(x);
        
    })


    roleTable = addRoleTable(data2)
    $('#assignedRole').append(roleTable);

})

    function clicked() {
        document.getElementById("associateRoleButton").submit();

}

function onSelectProject() {
    const valueX = document.getElementById("project").value;
    $('#addOn1').empty()
    var x = '<label for="" class="form-label">List of Roles</label>'

    x += '<select required="required" id="role" name="role" class="form-select" style = "width:250px" onchange="onSelectRole()"> \
        <option disabled selected value > Select Role</option > \
        <option value="Business Analyst">' + valueX + ' / Business Analyst</option> \
        <option value="Developer">' + valueX + ' / Developer</option> \
    </select>'

    $('#addOn1').append(x);


}

function onSelectRole() {

    $('#addOn2').show();


}

