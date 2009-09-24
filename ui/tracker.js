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
	$('TABLE#browse-list THEAD TR TH:nth-child(4), TABLE#browse-list TBODY TR TD:nth-child(4), TABLE#browse-list THEAD TR TH:nth-child(6), TABLE#browse-list TBODY TR TD:nth-child(6), TABLE#browse-list THEAD TR TH:nth-child(10), TABLE#browse-list TBODY TR TD:nth-child(10)').hide(); //css("display","none");
	/* show.hide some TDs */
	$("A.showall").click(function() {
		$("TD.light").toggle();
		return false;
	});
	/* show.hide.toggle some table columns in tracker_views.py */
	$('A.hide').click(function() {
		// Product
		$('TABLE#browse-list THEAD TR TH:nth-child(4)').hide();
		$('TABLE#browse-list TBODY TR TD:nth-child(4)').hide();
		// Version
		$('TABLE#browse-list THEAD TR TH:nth-child(6)').hide();
		$('TABLE#browse-list TBODY TR TD:nth-child(6)').hide();
		// Assigned_to
		$('TABLE#browse-list THEAD TR TH:nth-child(10)').hide();
		$('TABLE#browse-list TBODY TR TD:nth-child(10)').hide();
		$(this).css("text-decoration","none");
		$('A.show').css("text-decoration","underline");
		return false;
	});
	$('A.show').click(function() {
		// Product
		$('TABLE#browse-list THEAD TR TH:nth-child(4)').show();
		$('TABLE#browse-list TBODY TR TD:nth-child(4)').show();
		// Version
		$('TABLE#browse-list THEAD TR TH:nth-child(6)').show();
		$('TABLE#browse-list TBODY TR TD:nth-child(6)').show();
		// Assigned_to
		$('TABLE#browse-list THEAD TR TH:nth-child(10)').show();
		$('TABLE#browse-list TBODY TR TD:nth-child(10)').show();
		$(this).css("text-decoration","none");
		$('A.hide').css("text-decoration","underline");
		return false;
	});
});
