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

from itools.web import get_context

# Import from tchacker
from ikaaro.autoform import Widget
from ikaaro.utils import make_stl_template

from monkey import Image


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
            <fieldset class="attachment">
                <legend>Attachments</legend>
                <div class="bord">
                    <label class="label" for="attachment">New attachment:</label>
                    <input type="${type}" name="attachment" id="attachment" size="36" />
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
                        <canvas id="tools-sketch" width="${last_attachment/width_MED}" height="${last_attachment/height_MED}" style="background: url(${last_attachment/drawing_MED}) no-repeat center;"></canvas>
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

    def get_medium_image_size(self, image_width, image_height):
        if image_width >= image_height:
            medium_image_height = 800 * image_height / image_width
            medium_image_width = 800
        else:
            medium_image_width = 800 * image_width / image_height
            medium_image_height = 800
        return medium_image_width, medium_image_height

    def last_attachment(self):
        context = get_context()
        resource = context.resource
        # Last attachment
        last_attachment = resource.get_property('last_attachment') or None
        print("last_attachment = %s" % last_attachment)
        attachment = None
        if last_attachment is not None:
            image_file = resource.get_resource(str(last_attachment))
            is_image = isinstance(image_file, Image) or False

            try:
                drawing_MED = resource.get_resource(
                                str(last_attachment + "_MED"))
            except LookupError:
                    drawing_MED = False

            if is_image:
                # If last_attachment is an Image
                # Add the sketch-tool
                # Get the _MED image, if exist
                if drawing_MED:
                    # Get the _MED size if there is a MED image
                    handler = drawing_MED.handler
                    image_width, image_height = handler.get_size()
                    width_MED = image_width
                    height_MED = image_height
                    #print(last_attachment + '_MED/;download')
                    drawing_MED = last_attachment + '_MED/;download'
                else:
                    handler = image_file.handler
                    image_width, image_height = handler.get_size()
                    width_MED, height_MED = self.get_medium_image_size(
                                            image_width, image_height)
                    drawing_MED = last_attachment + '/;thumb?width=800&height=800'

                attachment = {
                        'name': last_attachment,
                        'width': image_width, 'height': image_height,
                        'width_MED': width_MED, 'height_MED': height_MED,
                        'drawing_MED': drawing_MED}
        print("attachment = %s" % attachment)
        return attachment
