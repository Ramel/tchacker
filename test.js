var assigned_to;
var ori_assigned_to;
//var not_assigned_to = new Option();
$(document).ready(function () {
    assigned_to = $('#assigned-to').find('select#assigned-to option:selected');
    //assigned_to.text = $('#assigned-to').find('select#assigned-to option:selected').attr("text");
    ori_assigned_to = $('#assigned-to').find('select#assigned-to option:selected');
    //ori_assigned_to.text = $('#assigned-to').find('select#assigned-to option:selected').attr("text");
    
    //not_assigned_to = $('SELECT#assigned-to, #assigned-to option:not(:selected)');
    console.log("assigned_to.text = " + assigned_to[0].text);
});

$('#assigned-to').find('select#assigned-to').change(function () {
  //$('#other').html(''); //Clear
  //var not_assigned_to = $('#other option:not(:selected)').length;
  //alert(assto[0].value + ", " + assto.length);
  //ori_assigned_to.value = $('#assigned-to').find('select#assigned-to option:selected').attr("value")
  //ori_assigned_to.value = $('#assigned-to').find('select#assigned-to option:selected').attr("text")
  assigned_to = $('#assigned-to').find('select#assigned-to option:selected');
  //assigned_to.text = $('#assigned-to').find('select#assigned-to option:selected').attr("text");
  
  console.log("BEG::ori_assigned_to.text = " + ori_assigned_to[0].text);
  console.log("BEG::assigned_to.text = " + assigned_to[0].text);
  var cc_list = $('#cc-list').find('SELECT#cc-list OPTION');
  // Remove the new one
  for (var i = 0; i < cc_list.length; i++) {
    //console.log("not_assigned_to["+i+"]" + not_assigned_to[i][1]);
    // If exist in the actual list
    if (cc_list[i].text == '------') {
      continue;
    }
    console.log("LOOP:cc_list["+i+"] = " + cc_list[i].text);
    if (cc_list[i].text == assigned_to[0].text) {
      // Remove the use as it is actually selected in assigned_to
      //$('#cc-list').find('SELECT#cc-list option[text="'+ assigned_to[0].text +'"]').remove();
      $('#cc-list').find('SELECT#cc-list option[text="'+ cc_list[i].text +'"]').remove();
      console.log('remove(' + cc_list[i].text + ')');
      //console.log("cc-list[" + i + "] = " + assigned_to[0].text + " == " + cc_list[i].text );  
    }
  }
  //ori_assigned_to.value = assigned_to.value;
  //ori_assigned_to.text = assigned_to.text;
  //console.log("assigned_to.text = " + assigned_to.text);
  //console.log("ori_assigned_to.text = " + ori_assigned_to.text);
  //$(this).html();
  var is_here = false;
  cc_list = $('#cc-list').find('SELECT#cc-list OPTION');
  // Add yhe old one
  for (var i = 0; i < cc_list.length; i++) {
    
    //console.log("not_assigned_to["+i+"]" + not_assigned_to[i][1]);
    // If exist in the actual list
    if (cc_list[i].text == '------') {
      continue;
    }
    console.log("LOOP_2:cc_list["+i+"] = " + cc_list[i].text);
    if (ori_assigned_to[0] == cc_list[i].text) {
      // Remove the use as it is actually selected in assigned_to
      //$('#cc-list').find('SELECT#cc-list option:[text="'+ assigned_to.text +'"]').remove();
      is_here = true;
      console.log("LOOP_2:cc_list["+i+"] = assigned_to.text is already there: " + assigned_to[0].text);
    }
  }
  if (is_here == false) {
    $('#cc-list').find('SELECT#cc-list').append(ori_assigned_to);
    console.log('append(' + ori_assigned_to[0].text + ')');
  }
  ori_assigned_to = assigned_to;
  ori_assigned_to = assigned_to;
  console.log("END::assigned_to.text = " + assigned_to[0].text);
  console.log("END::ori_assigned_to.text = " + ori_assigned_to[0].text);
  console.log("---");
});
