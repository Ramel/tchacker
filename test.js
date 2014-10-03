var assigned_to = new Option();
var not_assigned_to = new Option();
$(document).ready(function () {
    assigned_to.value = $('#assigned-to option:selected' ).attr("value");
    assigned_to.text = $('#assigned-to option:selected' ).attr("text");
    not_assigned_to = $('#assigned-to option:not(:selected)');
    //not_assigned_to;
    //console.log(assigned_to);
});

$('#assigned-to').change(function () {
  //$('#other').html(''); //Clear
  //var not_assigned_to = $('#other option:not(:selected)').length;
  //alert(assto[0].value + ", " + assto.length);
  console.log("assigned_to.text = " + assigned_to.text);
  console.log("not_assigned_to = " + not_assigned_to);
  // Check if the value does not exists
  for (var i = 0; i < not_assigned_to.length; i++) {
    console.log("LOOP:not_assigned_to["+i+"] = " + not_assigned_to[i].text);
    //console.log("not_assigned_to["+i+"]" + not_assigned_to[i][1]);
    /*
    if (not_assigned_to[i][1] == assigned_to[1]) {
      $("#cc-list option:last").after($('<option value="' + assigned_to[0] + '">' +  assigned_to[1] + '</option>'));
      assigned_to[0] = $('#assigned-to option:selected' ).attr("value");
      assigned_to[1] = $('#assigned-to option:selected' ).attr("text");
    }*/
  }
});

