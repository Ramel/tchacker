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
<form action=";add_issue" method="post" enctype="multipart/form-data">
  <fieldset>
    <legend>Add Issue</legend>
    <table>
      <tr>
        <td colspan="3">
          <label for="title" class="${title/class}">Title (mandatory):</label><br></br>
          <input value="${title/value}" type="text" id="title" size="48" name="title"></input>
        </td>
      </tr>
      <tr>
        <td valign="top">
          <label for="product" class="${product/class}">Producto (obligatorio)</label><br></br>
          <select id="product" name="product" class="tracker_select">
            <option value="-1"></option>
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item product/value">${item/value}</option>
          </select>
        </td>
        <td valign="top">
          <label for="module" class="${module/class}">Módulo:</label><br></br>
          <select id="module" name="module" class="tracker_select">
            <option value=""></option>
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item module/value">${item/value}</option>
          </select>
        </td>
        <td valign="top">
          <label for="version" class="${version/class}">Version:</label><br></br>
          <select id="version" name="version" class="tracker_select">
            <option value=""></option>
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item version/value">${item/value}</option>
          </select>
        </td>
      </tr>
      <tr>
        <td valign="top">
          <label for="type" class="${type/class}">Tipo (obligatorio)</label><br></br>
          <select id="type" name="type" class="tracker_select">
            <option value="-1"></option>
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item type/value">${item/value}</option>
          </select>
        </td>
        <td valign="top">
          <label for="state" class="${state/class}">Estado (obligatorio):</label><br></br>
          <select id="state" name="state" class="tracker_select">
            <option value="-1"></option>
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item state/value">${item/value}</option>
          </select>
        </td>
        <td valign="top">
          <label for="priority" class="${priority/class}">Prioridad:</label><br></br>
          <select id="priority" name="priority" class="tracker_select">
            <option value=""></option>
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item priority/value">${item/value}</option>
          </select>
        </td>
      </tr>
      <tr>
        <td valign="top">
          <label for="assigned_to" class="${assigned_to/class}">Asignar a:</label><br></br>
          <select id="assigned_to" name="assigned_to" class="tracker_select">
            <option value=""></option>
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item assigned_to/value">${item/value}</option>
          </select>
        </td>
        <td colspan="2" valign="top">
          <label for="cc_add" class="${cc_list/class}">CC:</label><br></br>
          <select id="cc_add" name="cc_add" size="5" class="tracker_select" multiple="multiple">
            <option value="${item/name}" selected="${item/selected}" stl:repeat="item cc_list/value">${item/value}</option>
          </select>
        </td>
      </tr>
      <tr>
        <td colspan="3" valign="top">
          <label for="description" class="${comment/class}">Descripción:</label><br></br>
          <textarea cols="80" rows="10" id="description" name="comment">${comment/value}</textarea>
        </td>
      </tr>
      <tr>
        <td colspan="3" valign="top">
          <label for="attachement">Attachement:</label><br></br>
          <input name="file" id="attachement" size="36" type="file"></input>
        </td>
      </tr>
      <tr>
        <td colspan="3">
          <input value="Agregar" class="button_ok" type="submit"></input>
        </td>
      </tr>
    </table>
  </fieldset>
</form>

</stl:block>
