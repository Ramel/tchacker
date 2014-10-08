var previous,
actual;
$(document).ready(function () {
  // Reodering
  $('#cc-list').find('SELECT#cc-list option[value=""]').remove();
  $('#cc-list').find('SELECT#cc-list').append(selected);
  if (not_selected.length > 0) {
    $('#cc-list').find('SELECT#cc-list').append('<option value="">------</option>');
    $('#cc-list').find('SELECT#cc-list').append(not_selected);
  }
  // Keep updated
  $('#assigned-to').find('select#assigned-to').focus(function () {
    // Store the current value on focus, before it changes
    previous = $(this).find('option:selected').clone();
  }).change(function () {
    // Do soomething with the previous value after the change
    //document.getElementById("log").innerHTML = "<b>Previous: </b>"+previous;
    actual = $(this).find('option:selected').clone()
    var cc_list = $('#cc-list').find('SELECT#cc-list OPTION').clone();
    // Remove the new one
    for (var i = 0; i < cc_list.length; i++) {
      // If exist in the actual list
      if (cc_list[i].text == '------') {
        continue;
      }
      if (cc_list[i].text == actual.text()) {
        // Remove the use as it is actually selected in assigned_to
        $('#cc-list').find('SELECT#cc-list option[text="' + cc_list[i].text + '"]').remove();
      }
    }
    var is_here = false;
    cc_list = $('#cc-list').find('SELECT#cc-list OPTION').clone();
    // Add the selected one if not exists
    for (var i = 0; i < cc_list.length; i++) {
      if (cc_list[i].text == '------') {
        continue;
      }
      if (cc_list[i].text == previous.text()) {
        is_here = true;
      }
    }
    if (is_here == false && previous.text() != '') {
      $('#cc-list').find('SELECT#cc-list').append(previous);
    }
    previous = $(this).find('option:selected').clone();
    var selected = Array.prototype.sort.call($('#cc-list').find('SELECT#cc-list option:selected'), function (a, b) {
      return $(a).text() > $(b).text() ? 1 : - 1;
    });
    var not_selected = Array.prototype.sort.call($('#cc-list').find('SELECT#cc-list option:not(:selected,[value=""])'), function (a, b) {
      return $(a).text() > $(b).text() ? 1 : - 1;
    });
    //var sep = new Option();
    $('#cc-list').find('SELECT#cc-list option[value=""]').remove();
    $('#cc-list').find('SELECT#cc-list').append(selected);
    if (not_selected.length > 0) {
      $('#cc-list').find('SELECT#cc-list').append('<option value="">------</option>');
      $('#cc-list').find('SELECT#cc-list').append(not_selected);
    }
  });
});
