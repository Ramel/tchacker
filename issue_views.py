# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2007-2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
# Copyright (C) 2009 Armel FORTUN <armel@maar.fr>
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

# Import from itools
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.messages import MSG_CHANGES_SAVED
from ikaaro.tracker.issue_views import Issue_Edit

# Import from tchacker
from datatypes import get_issue_fields
from comments import TchackerCommentsView

from monkey import Image

class TchackIssue_Edit(Issue_Edit):

    access = 'is_allowed_to_edit'
    title = MSG(u'Edit Issue')
    icon = 'edit.png'
    template = '/ui/tchacker/edit_issue.xml'
    styles = ['/ui/tchacker/style.css', '/ui/thickbox/style.css']
    scripts = ['/ui/tchacker/tracker.js', '/ui/thickbox/thickbox.js',
               '/ui/flowplayer/flowplayer-3.2.2.min.js', '/ui/tchacker/sketch.min.js']

    def get_schema(self, resource, context):
        tracker = resource.parent
        return get_issue_fields(tracker)

    def get_value(self, resource, context, name, datatype):
        if name in ('comment'):
            return datatype.get_default()
        if name in ('canvasDrawing'):
            return datatype.get_default()
        return resource.get_property(name)

    def get_namespace(self, resource, context):
        proxy = super(TchackIssue_Edit, self)
        namespace = proxy.get_namespace(resource, context)

        last_attachment = resource.get_property('last_attachment')
        # If last_attachment is an Image
        # Add the sketch-tool
        image_file = resource.get_resource(str(last_attachment + "_MED"))
        is_image = isinstance(image_file, Image) or False
        #print("is_image = %s" % is_image)
        handler = image_file.handler
        image_width, image_height = handler.get_size()
        #print("image_width = %s" % image_width)

        namespace['last_attachment'] = {'name': last_attachment,
            'width': image_width, 'height': image_height}
        #print("namespace['last_attachment'] = %s" % namespace['last_attachment'])

        # Comments
        namespace['comments'] = TchackerCommentsView().GET(resource, context)

        namespace['which_module'] = None
        for module in namespace['module']['value']:
            if module['selected'] == True in module.values():
                namespace['which_module'] = module['value']

        #print("namespace = %s" % namespace)
        return namespace

    def action(self, resource, context, form):
        #filename, mimetype, body = form['attachment']
        #print("action.form['attachment'].filename = %s" % filename)
        # Edit
        resource.add_comment(context, form)
        # Change
        context.database.change_resource(resource)
        context.message = MSG_CHANGES_SAVED
