$(document).ready(function () {
  // Keep on One line :
  $('TABLE#browse-list THEAD TR TH:nth-child(1), TABLE#browse-list TBODY TR TD:nth-child(1), TABLE#browse-list THEAD TR TH:nth-child(4), TABLE#browse-list TBODY TR TD:nth-child(4), TABLE#browse-list THEAD TR TH:nth-child(6), TABLE#browse-list TBODY TR TD:nth-child(6), TABLE#browse-list THEAD TR TH:nth-child(10), TABLE#browse-list TBODY TR TD:nth-child(10)').hide();
  /* show.hide some TDs */
  $("A.showall").click(function() {
    $("FORM#autoform .light").toggle();
    return false;
  });
  /* show.hide.toggle some table columns in tracker_views.py */
  $('A.hide').click(function() {
    // Id
    $('TABLE#browse-list THEAD TR TH:nth-child(1)').hide();
    $('TABLE#browse-list TBODY TR TD:nth-child(1)').hide();
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
    // Id
    $('TABLE#browse-list THEAD TR TH:nth-child(1)').show();
    $('TABLE#browse-list TBODY TR TD:nth-child(1)').show();
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

	/*
	 * For last_images in "tracker_views"'s table
	 */
 	var issue;
	var index;
	$(".rollover .roll").hover(
		function (issue, index) {
			issue = $(this).parent().parent().attr("id");
			index = $("#" + issue + " .roll").index(this);
			$("#" + issue + " .thumbnail").css("visibility", "hidden");
			$("#" + issue + " .rollimages DIV.roll:nth-child(" + (index+1) +")")
				.stop().css("display", "block").parent().css("background-color", "#E0E0F0");
		},
		function (issue, index) {
			issue = $(this).parent().parent().attr("id");
			index = $("#" + issue + " .roll").index(this);
			$("#" + issue + " .thumbnail").css("visibility", "visible");
			$("#" + issue + " .rollimages DIV.roll:nth-child(" + (index+1) +")")
				.stop().css("display", "none").parent().css("background-color", "transparent");
	});
});i

/* Sketch canvas drawing */ 
function updateDrawing() {
  var selected = $tabs.tabs('option', 'selected'); // => 0
  switch(selected) {
    case 0:
      // reset canvas
      $('#canvasDrawing').val("");
      break;
    case 1:
      // reset upload
      var att= $('#attachment');
      att.replaceWith(att.val('').clone(true));
      // send canvas
      $('#canvasDrawing')[0].value = $('canvas')[0].toDataURL();
      break;
  }
}
