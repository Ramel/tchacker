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
#from datetime import date, datetime, time
#from re import compile
#from textwrap import TextWrapper
#from tempfile import mkdtemp

# Import from itools
from itools.gettext import MSG
from itools.fs import FileName #, vfs

# Import from ikaaro
from ikaaro.file import Image, Video
from ikaaro.tracker.issue_views import Issue_Edit
#from ikaaro.tracker.datatypes import get_issue_fields

from datatypes import get_issue_fields
from comments import TchackerCommentsView


class TchackIssue_Edit(Issue_Edit):

    access = 'is_allowed_to_edit'
    title = MSG(u'Edit Issue')
    icon = 'edit.png'
    template = '/ui/tchacker/edit_issue.xml'
    styles = ['ui/tracker/style.css',
              '/ui/tchacker/style.css', '/ui/thickbox/style.css']
    scripts = ['/ui/tchacker/tracker.js', '/ui/thickbox/thickbox.js',
               '/ui/flowplayer/flowplayer-3.2.2.min.js']

    def get_schema(self, resource, context):
        tracker = resource.parent
        return get_issue_fields(tracker)

    def get_value(self, resource, context, name, datatype):
        if name in ('comment'):
            return datatype.get_default()
        return resource.get_property(name)

    def get_namespace(self, resource, context):
        namespace = Issue_Edit.get_namespace(self, resource, context)

        # Local variables
        root = context.root
        
        # Comments
        namespace['comments'] = TchackerCommentsView().GET(resource, context)
        #namespace['amount'] = TchackerCommentsView().get_comments_amount(resource)
        #print("in issue_views:get_namespace:%s" % namespace['comments_amount'])
        """
        for comment in namespace['comments']:
            print comment
            if comment['att_is_vid']:
                attachment = resource.get_resource(comment['attachment'])
                metadata = attachment.metadata
                width = metadata.get_property('width')
                #print width
        """
        """ 
        # Attachments
        links = []
        get_user = root.get_user_title
        for attachment_name in resource.get_property('attachment'):
            attachment = resource.get_resource(attachment_name, soft=True)
            missing = (attachment is None)
            author = mtime = None
            if missing is False:
                mtime = attachment.get_property('mtime')
                mtime = context.format_datetime(mtime)
                author = get_user(attachment.get_property('last_author'))

            links.append({
                'author': author,
                'missing': missing,
                'mtime': mtime,
                'name': attachment_name,
                'is_image': isinstance(attachment_name, Image)})

        namespace['attachments'] = links
        """
        #print("namespace = %s" % namespace) 
        """ 
        # Build the namespace for comments
        for comment in namespace['comments']:
            if comment['file']:
                attachment = resource.get_resource(comment['file'])
                comment['is_image'] = isinstance(attachment, Image)
                comment['is_video'] = isinstance(attachment, Video)
                comment['width'] = 200
                comment['height'] = 200
                #print("is_video = %s" % comment['is_video'])
                if comment['is_video']:
                    name = attachment.name
                    filename, ext, lang = FileName.decode(name)
                    thumb = attachment.metadata.get_property('thumbnail')
                    video = resource.get_resource("%s" % name)
                    comment['video'] = ("%s" % filename)
                    comment['width'] = video.metadata.get_property('width')
                    comment['height'] = video.metadata.get_property('height')
                    if thumb == "True":
                        comment['old'] = ""
                    elif thumb == "False":
                        comment['old'] = "_low"
                    else:
                        comment['width'] = False
                        comment['height'] = False
                        comment['is_image'] = False
                        comment['is_video'] = False
                        comment['old'] = False
            else:
                comment['file'] = False
                comment['is_image'] = False
                comment['is_video'] = False
        """
        return namespace
