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

# Import from the Standard Library
from datetime import date, datetime, time
from re import compile
from textwrap import TextWrapper
from tempfile import mkdtemp

# Import from itools
from itools.datatypes import Boolean, Date, Integer, String, Unicode
from itools.datatypes import XMLContent
from itools.gettext import MSG
from itools.ical import Time
from itools.html import xhtml_uri
from itools.i18n import format_datetime
from itools.web import STLForm, STLView
from itools.xml import XMLParser, START_ELEMENT, END_ELEMENT, TEXT
from itools.fs import FileName, vfs
from itools.core import guess_extension, guess_type
from itools.uri import resolve_uri

# Import from ikaaro
from ikaaro.messages import MSG_CHANGES_SAVED
from ikaaro.table_views import Table_View
from ikaaro.views import CompositeForm
from ikaaro.views import ContextMenu
from ikaaro.file import Image, Video
from ikaaro.tracker.issue_views import Issue_Edit
from ikaaro.tracker.datatypes import get_issue_fields, UsersList
from ikaaro.registry import get_resource_class


class TchackIssue_Edit(Issue_Edit):

    access = 'is_allowed_to_edit'
    title = MSG(u'Edit Issue')
    icon = 'edit.png'
    template = '/ui/tchacker/edit_issue.xml'
    styles = ['ui/tracker/style.css',
              '/ui/tchacker/style.css', '/ui/thickbox/style.css']
    scripts = ['/ui/tchacker/tracker.js', '/ui/thickbox/thickbox.js',
               '/ui/flowplayer/flowplayer-3.2.2.min.js',
               '/ui/flowplayer/flowplayer-3.2.2.swf']

    def get_schema(self, resource, context):
        return get_issue_fields(resource.parent)

    def get_value(self, resource, context, name, datatype):
        history = resource.get_history()
        record = history.get_record(-1)
        return  record.get_value(name)

    def get_namespace(self, resource, context):
        namespace = Issue_Edit.get_namespace(self, resource, context)
        # Local variables
        users = resource.get_resource('/users')
        history = resource.get_history()
        record = history.get_record(-1)
        # Build the namespace
        for comment in namespace['comments']:
            if comment['file']:
                attachment = resource.get_resource(comment['file'])
                comment['is_image'] = isinstance(attachment, Image)
                comment['is_video'] = isinstance(attachment, Video)
                comment['width'] = 200
                comment['height'] = 200

                if comment['is_video']:
                    name = attachment.name
                    filename, ext, lang = FileName.decode(name)
                    thumb = attachment.metadata.get_property('thumbnail')
                    if thumb == "True":
                        video = resource.get_resource("%s_low" % name)
                        comment['video'] = ("%s_low" % filename)
                        comment['width'] = video.metadata.get_property('width')
                        comment['height'] = video.metadata.get_property('height')
                    else:
                        comment['video'] = ("%s" % filename)
                        comment['width'] = False
                        comment['height'] = False
                        comment['is_image'] = False
                        comment['is_video'] = False
            else:
                comment['file'] = False
                comment['is_image'] = False
                comment['is_video'] = False

        return namespace
