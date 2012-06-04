$(document).ready(function () {
  // Keep on One line :
  $('TABLE#browse-list THEAD TR TH:nth-child(1), TABLE#browse-list TBODY TR TD:nth-child(1), TABLE#browse-list THEAD TR TH:nth-child(4), TABLE#browse-list TBODY TR TD:nth-child(4), TABLE#browse-list THEAD TR TH:nth-child(6), TABLE#browse-list TBODY TR TD:nth-child(6), TABLE#browse-list THEAD TR TH:nth-child(10), TABLE#browse-list TBODY TR TD:nth-child(10)').hide();
  /* show.hide some TDs */
  $("A.showall").click(function() {
    $("FORM#tracker .light").toggle();
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

  /*
   * For LuluVroumette
   */
  $("SELECT#state").change(function() {
    if (document.URL.match(";edit") != null && document.URL.match("luluvroumette") != null) {
      var state = $("SELECT#state option:selected").attr("value");  // selected state
      var str = $("TEXTAREA#comment").val();                        // actual comment
      var pattn = /ftp(.*).7z/gim;                                  // Is there an ftp pasted text?
      var is7z = str.match(pattn);
      var isFtp = str.match("ftp://tchack@tchack.com@192.175.0.1/lulu-vroumette-s2/From-Tchack/");
      if (state == 4 && is7z != null && isFtp != null) {
        var ftp = str.replace("ftp://tchack@tchack.com@192.175.0.1/lulu-vroumette-s2/", "");
        $("TEXTAREA#comment").val("Modélisation et texture livrées, disponible sur le Ftp :\n\nftp://ftp2.tchack.com/" + ftp);
      }
    }
  }).change();
  $("SELECT#type").change(function() {
    if (document.URL.match(";add_issue") != null && document.URL.match("luluvroumette") != null) {
      var type = $("SELECT#type option:selected").attr("value");    // selected type
      var str = $("INPUT#title").val();
      var pattn = /^LV([_\- ]*)P([_\- ]*)/gi;                        //
      var good = str.match(pattn);
      if (type == 2 || type == 12 || type == 13 || type == 15) {
        if (good != null) {
          var str = str.replace(good, "LV-P-");
          $("INPUT#title").val(str);
        }
        if (good == null) {
          $("INPUT#title").val("LV-P-" + str);
        }
      }
    }
  }).change();
  //$("LI.nav-active A").change(function() {
  //alert(document.URL.match(";view\\?search_name"));
  if (document.URL.match(";view\\?[a-zA-Z0-9%+!&=]*search_name") != null && document.URL.match("luluvroumette") != null) {
    var search = $("DIV.context-menu UL LI.nav-active A").text();
    var pattn = new RegExp("^EP[0-9]{3}");
    var isEpisode = pattn.exec(search); // EP000
    //alert(search);
    var quantityProps = 0;
    var validated = 0;
    if (isEpisode != null) {
      var rowCount = ($("TABLE#browse-list TR").length) - 1;
      quantityProps = rowCount;
      //alert("rowCount = " + rowCount);
      for(i = 1; i <= rowCount; i++) {
        var td = $("TABLE#browse-list TR:eq(" + i + ") TD:eq(7)").text();
        //alert("TD:eq(7) = '" + td + "'");
        if (td.match("À supprimer") != null) {
          quantityProps = quantityProps - 1;
        }
        if (td.match("Livré à TTK") != null) {
          validated = validated + 1;
        }
      }
      //alert("isEpisode = " + isEpisode + ", TR = " + rowCount + ",\n quantityProps = " + quantityProps + ", validated = " + validated);
      $("DIV.context-menu UL LI.nav-active A").append(" Livrés : " + validated + "/" + quantityProps);
    }
  }
});
