# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Armel FORTUN <armel@tchack.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ikaaro.autoform import Widget
from ikaaro.utils import make_stl_template


class FileAndSketchTabbedWidget(Widget):

    name = "onglets"
    type = "file"

    template = make_stl_template("""
    <ul>
        <li><a href="#tabs-1"><span>Upload a file</span></a></li>
        <li stl:if="last_attachment"><a href="#tabs-2"><span>Draw on last attachment</span></a></li>
    </ul>
    <div id="tabs-1">
        <div class="one bord">
            <fieldset class="attachement">
                <legend>Attachments</legend>
                <div class="bord">
                    <label class="label" for="attachement">New attachment:</label>
                    <input type="${type}" name="attachement" id="attachement" size="36" />
                </div>
            </fieldset>
        </div>
    </div>
    <div id="tabs-2" stl:if="last_attachment">
        <div class="one bord">
            <fieldset class="drawing">
                <legend>Online retake</legend>
                <div id="drawing-tools" class="bord">
                    <div class="tools">
                        <a href="#tools-sketch" data-tool="marker">Marker</a>
                        <a href="#tools-sketch" data-tool="eraser">Eraser</a>
                    </div>
                    <input type="text" id="canvasDrawing" name="canvasDrawing" type="hidden"/>
                        <canvas id="tools-sketch" width="{last_attachment/width_MED}" height="{last_attachment/height_MED}" style="background: url(${last_attachment/drawing_MED}) no-repeat center;"></canvas>
                    <script type="text/javascript">
                    $(function() {
                        $.each(['#f00', '#ff0', '#0f0', '#0ff', '#00f', '#f0f', '#000', '#fff'], function() {
                            $('#drawing-tools .tools').append('<a href="#tools-sketch" data-color="' + this + '" style="width: 20px; background: ' + this + ';"></a>');
                        });
                        $('#tools-sketch').sketch({defaultColor: "#f00"});
                    });
                    </script>
                </div>
            </fieldset>
        </div>
        <script type="text/javascript">
            var $tabs = $("#${name}").tabs();
        </script>
    </div>""")
