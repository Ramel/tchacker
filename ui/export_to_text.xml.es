<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<form id="form_table" action=";export_to_text" method="GET">
  <stl:block stl:repeat="param search_parameters">${param}</stl:block>

  ${batch} ${table}
  <br></br>
  <fieldset>
    <legend>Exportar a texto: selecciona las columnas a exportar</legend>
    <stl:block stl:repeat="column columns">
      <input id="${column/name}" value="${column/name}" type="checkbox" name="column_selection" checked="${column/checked}"></input>
        <label for="${column/name}">${column/title}</label>  
    </stl:block>
    <input value="Update text export" class="button_ok" type="submit"></input>
  </fieldset>
  <br></br>
  <div style="height: 200px; border: 1px solid #9FB7D4; overflow: auto">
    <pre>${text}</pre>
  </div>
</form>

</stl:block>
