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
    console.log('focus.previous.text = ' + previous.text());
  }).change(function () {
    // Do soomething with the previous value after the change
    //document.getElementById("log").innerHTML = "<b>Previous: </b>"+previous;
    actual = $(this).find('option:selected').clone()
    console.log('NOW::previous.text = ' + previous.text());
    console.log('NOW::previous.text = ' + previous.text());
    var cc_list = $('#cc-list').find('SELECT#cc-list OPTION').clone();
    // Remove the new one
    for (var i = 0; i < cc_list.length; i++) {
      // If exist in the actual list
      if (cc_list[i].text == '------') {
        continue;
      }
      console.log('LOOP_1:cc_list[' + i + '] = ' + cc_list[i].text);
      if (cc_list[i].text == actual.text()) {
        // Remove the use as it is actually selected in assigned_to
        $('#cc-list').find('SELECT#cc-list option[text="' + cc_list[i].text + '"]').remove();
        console.log('remove(' + cc_list[i].text + ')');
      }
    }
    var is_here = false;
    cc_list = $('#cc-list').find('SELECT#cc-list OPTION').clone();
    console.log('NOW::previous.text = ' + previous.text());
    // Add the selected one if not exists
    for (var i = 0; i < cc_list.length; i++) {
      if (cc_list[i].text == '------') {
        continue;
      }
      console.log('LOOP_2:cc_list[' + i + '] = ' + cc_list[i].text);
      if (cc_list[i].text == previous.text()) {
        is_here = true;
        console.log('LOOP_2:cc_list[' + i + '] = assigned_to.text is already there: ' + cc_list[i].text);
      }
    }
    console.log('is_here = ' + is_here);
    if (is_here == false && previous.text() != '') {
      $('#cc-list').find('SELECT#cc-list').append(previous);
      console.log('append(' + previous.text() + ')');
    }
    previous = $(this).find('option:selected').clone();
    /*
    Array.prototype.sort.call($('#cc-list').find('SELECT#cc-list option'), function (a, b) {
      return $(a).text() > $(b).text() ? 1 : - 1;
    }).appendTo($('#cc-list').find('SELECT#cc-list'));
    */
    var selected = Array.prototype.sort.call($('#cc-list').find('SELECT#cc-list option:selected'), function (a, b) {
      return $(a).text() > $(b).text() ? 1 : - 1;
    });
    var not_selected = Array.prototype.sort.call($('#cc-list').find('SELECT#cc-list option:not(:selected,[value=""])'), function (a, b) {
      return $(a).text() > $(b).text() ? 1 : - 1;
    });
    console.log('selected(' + selected.length + ')');
    console.log('not_selected(' + not_selected.length + ')');
    //var sep = new Option();
    $('#cc-list').find('SELECT#cc-list option[value=""]').remove();
    $('#cc-list').find('SELECT#cc-list').append(selected);
    if (not_selected.length > 0) {
      $('#cc-list').find('SELECT#cc-list').append('<option value="">------</option>');
      $('#cc-list').find('SELECT#cc-list').append(not_selected);
    }
  });
});
