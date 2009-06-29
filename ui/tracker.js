function reply(id){
  var comment = document.getElementById('comment'+id).innerHTML;

  /* Replace html by text */
  var reg = new RegExp("(&gt;)", "g");
  comment = comment.replace(reg, '>');
  reg = new RegExp("(&lt;)", "g");
  comment = comment.replace(reg, '<');
  reg = new RegExp("(&amp;)", "g");
  comment = comment.replace(reg, '&');
  reg = new RegExp("(&nbsp;)", "g");
  comment = comment.replace(reg, ' ');
  reg1 = new RegExp('(<a href=")', "g");
  reg2 = new RegExp('(">.*</a>)', "g");
  if (comment.match(reg1) && comment.match(reg2)) {
      comment = comment.replace(reg1, '');
      comment = comment.replace(reg2, '');
  }

  comment = comment.split(/\r|\n/);
  replytext = ''
  for (var i=0; i < comment.length; i++){
    replytext += "> " + comment[i] + "\n";
  }
  replytext = "(In reply to comment #" + id + ")\n" + replytext + "\n";
  var textarea = document.getElementById('comment')
  textarea.value = replytext
  textarea.focus();
}


function update_tracker_list(list_name)
{
  /* Search the selected elements */
  var selected_id = {};
  $('#' + list_name + ' option:selected').each(function() {
    selected_id[$(this).val()] = true;
  });

  /* Remove only the good options */
  $('#'+list_name).find("option[value!='-1'][value!='']").remove();

  /* Get the others */
  var options = $('#' + list_name).html();

  /* Update the list */
  $('#product option:selected').each(function() {
    var id_product = $(this).val();
    for (var i=0; i < list_products[id_product][list_name].length; i++) {
      id = list_products[id_product][list_name][i]['id'];
      options += '<option value="';
      options += id + '"';
      if (id in selected_id)
        options += ' selected="selected">';
      else
        options += '>';
      options += list_products[id_product][list_name][i]['value'];
      options += '</option>';
    }
  });
  $("#" + list_name).html(options);
}

$(document).ready(function () {
	// Test if we need to throw the update_tracker() method only if we are in a
	// ";add_issue", ";change_several_bugs", ";edit", ";search" page,
	// seems to bug with hide(), show(), toggle(), investigations needed.
	var href = location.href;
	var pos = href.lastIndexOf("/");
	href  = href.substr(pos + 1);
	pos = href.lastIndexOf("?");
	href = href.substr(0, pos);
	// If we are in one of them, apply the method
	if(href == ";add_issue" || href == ";edit"
		|| href == ";search" || href == ";change_several_bugs") {
		update_tracker();
		$("#product").bind("change", update_tracker);
	}
	/* show.hide some TDs */
	$("A.showall").click(function() {
		$("TD.light").toggle();
		return false;
	});
	/* show.hide.toggle some table columns */
	$('A.hide').click(function() {
		$('TABLE.issues TH.version, TABLE.issues TD.version, TABLE.issues TH.product, TABLE.issues TD.product, TABLE.issues TH.assigned_to, TABLE.issues TD.assigned_to').hide();
		return false;
	});
	$('A.show').click(function() {
		$('TABLE.issues TH.version, TABLE.issues TD.version, TABLE.issues TH.product, TABLE.issues TD.product, TABLE.issues TH.assigned_to, TABLE.issues TD.assigned_to').show();
		return false;
	});
	$('A.toggle').click(function() {
		$('TABLE.issues TH.version, TABLE.issues TD.version, TABLE.issues TH.product, TABLE.issues TD.product, TABLE.issues TH.assigned_to, TABLE.issues TD.assigned_to').toggle();
		return false;
	});
});
