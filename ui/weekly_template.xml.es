<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<stl:block xmlns="http://www.w3.org/1999/xhtml" xmlns:stl="http://www.hforge.org/xml-namespaces/stl">

<td colspan="${cell/colspan}" rowspan="${cell/rowspan}" class="color0" valign="top">
  <a href="${cell/content/issue/url}" title="${cell/content/issue/comment}">[#${cell/content/issue/number}]</a>  <span class="tracker_product" stl:if="cell/content/issue/product">${cell/content/issue/product}</span> ${cell/content/issue/title} <span class="tracker_resource">(${cell/content/resource/title})</span>
</td>

</stl:block>
