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
  <!-- Advanced Search -->
  <fieldset>
    <legend>Buscar<stl:block stl:if="search_name">: ${search_title}</stl:block>
    </legend>
    <form action=";view" method="get">
      <table>
        <tr>
          <td colspan="2">
            <label for="text">Text (search within the title and all comments) </label>  <br></br>
            <input id="text" type="text" name="text" value="${text}" class="tracker_select" size="30"></input>
          </td>
          <td colspan="1">
            <label for="mtime">Modified since:</label><br></br>
            <input value="${mtime}" type="text" id="mtime" size="2" name="mtime"></input> days ago
          </td>
        </tr>
        <tr>
          <td valign="top">
            <label for="product">Product:<stl:inline stl:if="is_admin"> (<a href="./product/;view">Edit</a>)</stl:inline></label>
            <br></br>
            <select id="product" name="product" size="4" class="tracker_select" multiple="multiple">
              <option value="${item/name}" selected="${item/selected}" stl:repeat="item products">${item/value}</option>
            </select>
          </td>
          <td valign="top">
            <label for="module">Module:<stl:inline stl:if="is_admin"> (<a href="./module/;view">Edit</a>)</stl:inline></label>
            <br></br>
            <select id="module" name="module" size="4" class="tracker_select" multiple="multiple">
              <option value="${item/name}" selected="${item/selected}" stl:repeat="item modules">${item/value}</option>
            </select>
          </td>
          <td valign="top">
            <label for="version">Version:<stl:inline stl:if="is_admin"> (<a href="./version/;view">Edit</a>)</stl:inline></label>
            <br></br>
            <select id="version" name="version" size="4" class="tracker_select" multiple="multiple">
              <option value="${item/name}" selected="${item/selected}" stl:repeat="item versions">${item/value}</option>
            </select>
          </td>
        </tr>
        <tr>
          <td valign="top">
            <label for="type">Type:<stl:inline stl:if="is_admin"> (<a href="./type/;view">Edit</a>)</stl:inline></label>
            <br></br>
            <select id="type" name="type" size="4" class="tracker_select" multiple="multiple">
              <option value="${item/name}" selected="${item/selected}" stl:repeat="item types">${item/value}</option>
            </select>
          </td>
          <td valign="top">
            <label for="state">Status:<stl:inline stl:if="is_admin"> (<a href="./state/;view">Edit</a>)</stl:inline></label>
            <br></br>
            <select id="state" name="state" size="4" class="tracker_select" multiple="multiple">
              <option value="${item/name}" selected="${item/selected}" stl:repeat="item states">${item/value}</option>
            </select>
          </td>
          <td valign="top">
            <label for="priority">Priority:<stl:inline stl:if="is_admin"> (<a href="./priority/;view">Edit</a>)</stl:inline></label>
            <br></br>
            <select id="priority" name="priority" size="4" class="tracker_select" multiple="multiple">
              <option value="${item/name}" selected="${item/selected}" stl:repeat="item priorities">${item/value}</option>
            </select>
          </td>
        </tr>
        <tr>
          <td colspan="3" valign="top">
            <label for="assigned_to">Assigned To:<stl:inline stl:if="is_admin"> (<a href="${manage_assigned}">Edit</a>)</stl:inline></label>
            <br></br>
            <select id="assigned_to" name="assigned_to" size="4" class="tracker_select" multiple="multiple">
              <option value="${item/name}" selected="${item/selected}" stl:repeat="item assigned_to">${item/value}</option>
            </select>
          </td>
        </tr>
      </table>
      <br></br>
      <input value="Search" type="submit" class="button_search" name=";view"></input>
    </form>
  </fieldset>

</stl:block>
