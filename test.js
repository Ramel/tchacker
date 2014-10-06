var assigned_to,
assigned_list;
var ori_assigned_to;
var previous;
//var not_assigned_to = new Option();
$(document).ready(function () {
  //assigned_to = $('#assigned-to').find('select#assigned-to option:selected');
  //assigned_list = $('#assigned-to').find('select#assigned-to');
  //assigned_to.text = $('#assigned-to').find('select#assigned-to option:selected').attr("text");
  //ori_assigned_to = $('#assigned-to').find('select#assigned-to option:selected');
  //ori_assigned_to.text = $('#assigned-to').find('select#assigned-to option:selected').attr("text");
  //not_assigned_to = $('SELECT#assigned-to, #assigned-to option:not(:selected)');
  //console.log("assigned_to.text = " + assigned_to[0].text);
  $('#assigned-to').find('select#assigned-to').focus(function () {
    // Store the current value on focus, before it changes
    previous = $(this).find('option:selected');
  }).change(function () {
    // Do soomething with the previous value after the change
    //document.getElementById("log").innerHTML = "<b>Previous: </b>"+previous;
    console.log('previous.text = ' + previous.text());
    previous = $(this).find('option:selected')

    var cc_list = $('#cc-list').find('SELECT#cc-list OPTION');
    // Remove the new one
    for (var i = 0; i < cc_list.length; i++) {
      //console.log("not_assigned_to["+i+"]" + not_assigned_to[i][1]);
      // If exist in the actual list
      if (cc_list[i].text == '------') {
        continue;
      }
      console.log('LOOP:cc_list[' + i + '] = ' + cc_list[i].text);
      if (cc_list[i].text == previous.text()) {
        // Remove the use as it is actually selected in assigned_to
        //$('#cc-list').find('SELECT#cc-list option[text="'+ assigned_to[0].text +'"]').remove();
        $('#cc-list').find('SELECT#cc-list option[text="' + cc_list[i].text + '"]').remove();
        console.log('remove(' + cc_list[i].text + ')');
        //console.log("cc-list[" + i + "] = " + assigned_to[0].text + " == " + cc_list[i].text );  
      }
    }
  });
});

