<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">
  <!-- Javascript -->
  <script language="javascript">
  var list_products = {<stl:inline stl:repeat="product list_products">
                       "${product/id}":
                          {'module':
                           [<stl:inline stl:repeat="module product/modules">
                             {"id": "${module/id}",
                              "value": "${module/value}"},
                              </stl:inline>],
                           'version':
                           [<stl:inline stl:repeat="version product/versions">
                             {"id": "${version/id}",
                              "value": "${version/value}"},
                              </stl:inline>]}
                       ,</stl:inline>
                      }
  function update_tracker(){
      update_tracker_list('version');
      update_tracker_list('module');
  }
  </script>
<form id="form_table" action=";change_several_bugs?${search_parameters}" method="POST">
  ${batch} ${table}

  <br></br>
  <fieldset>
    <legend>Change Several Issues</legend>
<table>
  <tr>
    <td valign="top">
      <label for="product">Producto:</label><br></br>
      <select id="product" name="change_product" class="tracker_select">
        <option value="-1">Do not change</option>
        <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item products">${item/title}</option>
      </select>
    </td>
    <td valign="top">
      <label for="module">Módulo:</label><br></br>
      <select id="module" name="change_module" class="tracker_select">
        <option value="-1">Do not change</option>
        <option value=""></option>
        <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item modules">${item/title}</option>
      </select>
    </td>
    <td valign="top">
      <label for="version">Version:</label><br></br>
      <select id="version" name="change_version" class="tracker_select">
        <option value="-1">Do not change</option>
        <option value=""></option>
        <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item versions">${item/title}</option>
      </select>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <label for="type">Tipo:</label><br></br>
      <select id="type" name="change_type" class="tracker_select">
        <option value="-1">Do not change</option>
        <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item types">${item/title}</option>
      </select>
    </td>
    <td valign="top">
      <label for="state">Estado:</label><br></br>
      <select id="state" name="change_state" class="tracker_select">
        <option value="-1">Do not change</option>
        <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item states">${item/title}</option>
      </select>
    </td>
    <td valign="top">
      <label for="priority">Prioridad:</label><br></br>
      <select id="priority" name="change_priority" class="tracker_select">
        <option value="-1">Do not change</option>
        <option value=""></option>
        <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item priorities">${item/title}</option>
      </select>
    </td>
  </tr>
  <tr>
    <td colspan="3" valign="top">
      <label for="assigned_to">Asignar a:</label><br></br>
      <select id="assigned_to" name="change_assigned_to" class="tracker_select">
        <option value="do-not-change">Do not change</option>
        <option value=""></option>
        <option value="${item/id}" selected="${item/is_selected}" stl:repeat="item users">${item/title}</option>
      </select>
    </td>
  </tr>
  <tr>
    <td colspan="6">
      <label for="comment">Comentario:</label>
      <br></br>
      <textarea cols="68" rows="10" id="comment" name="comment"></textarea>
    </td>
  </tr>
  <tr>
    <td colspan="6">
      <input value="Edit Issues" class="button_ok" type="submit"></input>
    </td>
  </tr>
</table>
  </fieldset>
</form>

</stl:block>
