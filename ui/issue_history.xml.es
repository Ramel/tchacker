<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

  <h2>Issue #${number}</h2>

  <stl:block stl:repeat="row rows">
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
      <tr class="tracker_issue_comment_title">
        <td><a href="#${row/number}">${row/datetime}</a> <a name="${row/number}"></a></td>
        <td>${row/user}</td>
      </tr>
      <tr>
        <td colspan="2">
          <stl:block stl:if="row/title">
            <strong>Title:</strong> ${row/title}<br></br>
          </stl:block>
          <stl:block stl:if="row/version">
            <strong>Version:</strong> ${row/version}<br></br>
          </stl:block>
          <stl:block stl:if="row/type">
            <strong>Tipo:</strong> ${row/type}<br></br>
          </stl:block>
          <stl:block stl:if="row/state">
            <strong>State:</strong> ${row/state}<br></br>
          </stl:block>
          <stl:block stl:if="row/module">
            <strong>Módulo:</strong> ${row/module}<br></br>
          </stl:block>
          <stl:block stl:if="row/priority">
            <strong>Prioridad:</strong> ${row/priority}<br></br>
          </stl:block>
          <stl:block stl:if="row/assigned_to">
            <strong>Asignar a:</strong> ${row/assigned_to}<br></br>
          </stl:block>
          <stl:block stl:if="row/cc_list">
            <strong>CC:</strong> ${row/cc_list}<br></br>
          </stl:block>
          <stl:block stl:if="row/file">
            <strong>Attachement:</strong> <a href="${row/file}">${row/file}</a>
            <br></br>
          </stl:block>
          <stl:block stl:if="row/comment">
            <strong>Comentario:</strong> ${row/comment}<br></br>
          </stl:block>
        </td>
      </tr>
    </table>
    <br></br>
  </stl:block>

</stl:block>
