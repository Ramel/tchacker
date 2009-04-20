<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<div class="context_menu">
  <label>${title}</label>
  <form action=";remember_search" method="post" style="margin: 4px 0px 0px 5px;">
    <input value="${search_name}" type="hidden" name="search_name" stl:if="search_name"></input>
    <input value="${item/value}" stl:repeat="item search_fields" name="${item/name}" type="hidden"></input>  <input value="${search_title}" name="search_title" style="width: 73%" size="18" type="text"></input>
    <input value="Aceptar" class="button_ok" type="submit"></input>
  </form>

  <form action=";forget_search" method="post" stl:if="search_name">
    <input value="${search_name}" name="search_name" type="hidden"></input>
    <input onclick="return confirm('Are you sure you want to forget this search?');" type="submit" class="button_delete" value="Olvidar esta Búsqueda"></input>
  </form>
</div>

</stl:block>
