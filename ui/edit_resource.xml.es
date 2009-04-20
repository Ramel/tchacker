<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form action="${action}" method="post">
  <fieldset>
    <legend stl:if="not id">Asignar un recurso</legend>
    <legend stl:if="id">Edit the assignment #${id}</legend>
    <table>
      <tr>
        <td valign="top">
          <label for="resource">Resource:</label><br></br>
          <select id="resource" name="resource" class="tracker_select">
            <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item users">${item/title}</option>
          </select>
        </td>
        <td valign="top">
          <label for="dtstart">Start:</label><br></br>
          <input value="${d_start}" type="text" id="dtstart" size="10" name="dtstart"></input>
          <input id="trigger_dtstart" value="..." name="trigger_dtstart" type="button"></input>  <br></br>  <input value="${t_start}" type="text" id="tstart" size="5" name="tstart"></input> (HH:MM)
        </td>
        <td valign="top">
          <label for="dtend">End:</label><br></br>
          <input value="${d_end}" type="text" id="dtend" size="10" name="dtend"></input>
          <input id="trigger_dtend" value="..." name="trigger_dtend" type="button"></input>   
          <select id="time_select" onchange="update_time('time_select')" name="time_select">
            <option value=""></option>
            <option value="${option/name}" stl:repeat="option time_select">${option/start} - ${option/end}</option>
          </select>
          <br></br>
          <input value="${t_end}" type="text" id="tend" size="5" name="tend"></input> (HH:MM)
        </td>
      </tr>
      <tr>
        <td colspan="3" valign="top">
          <label for="comment">Comentario:</label><br></br>
          <textarea cols="80" rows="3" id="comment" name="comment">${comment}</textarea>
        </td>
      </tr>
    </table>
    <input name=";add" value="Assign" type="submit" class="button_ok" stl:if="not id"></input>
    <input name=";edit" value="Save Changes" type="submit" class="button_ok" stl:if="id"></input>
  </fieldset>
</form>
<br></br>

<script language="javascript">
Calendar.setup({inputField: "dtstart", ifFormat: "%Y-%m-%d",
  button: "trigger_dtstart"});
Calendar.setup({inputField: "dtend", ifFormat: "%Y-%m-%d",
  button: "trigger_dtend"});

function update_time(name){
  var elt = document.getElementById(name);
  var text = elt.options.item(elt.selectedIndex).text;
  var start = ""; var end = "";
  if (text != ""){
    var reg = new RegExp(" - +", "g");
    var value = text.split(reg);
    start = value[0];
    end = value[1];
    }
  document.getElementById("tstart").value = start;
  document.getElementById("tend").value = end;
}
</script>

</stl:block>
