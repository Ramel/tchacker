<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<div class="context_menu">
  <label>${title}</label>
  <form action="${path_to_tracker}/;go_to_issue" method="get" style="margin: 4px 0px 0px 5px;">
    <input name="issue_name" size="6" type="text"></input>
    <input value="Go" class="button_ok" type="submit"></input>
  </form>
</div>

</stl:block>
