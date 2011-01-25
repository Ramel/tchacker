# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2009 Armel Fortun <armel@maar.fr>
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
from time import strftime
from tempfile import mkdtemp
#from subprocess import call
from zipfile import ZipFile

# Import from itools
from itools.core import guess_extension
from itools.gettext import MSG
from itools.fs import vfs
from itools.uri import encode_query #, get_uri_name
#from itools.fs import FileName
from itools.web import STLView
from itools.xml import XMLParser
#from itools.handlers import File as FileHandler

# Import from ikaaro
#from ikaaro.views import ContextMenu
from ikaaro.views import CompositeView
from ikaaro.tracker.tracker_views import Tracker_View, StoreSearchMenu
from ikaaro.tracker.tracker_views import TrackerViewMenu
from ikaaro.file import Image, Video



class Tchacker_ViewMenu(TrackerViewMenu):

    title = MSG(u'Advanced')

    def get_items(self, resource, context):
        # Keep the query parameters
        schema = context.view.get_query_schema()
        params = encode_query(context.query, schema)
        return [
            {'title': MSG(u'Download "Last Att." images as one Zip'),
             'href': ';zip?%s' % params}
              ] + TrackerViewMenu.get_items(self, resource, context)



class Tchacker_ViewTop(STLView):

    template = '/ui/tchacker/tchacker_view_top.xml.en'


class Tchacker_ViewBottom(Tracker_View):

    access = 'is_allowed_to_view'
    title = MSG(u'View')
    icon = 'view.png'

    # XXX
    #table_template = '/ui/tchacker/browse_table.xml'
    #context.styles.append('/ui/tchacker/tracker.css')


    def get_item_value(self, resource, context, item, column):
        # Last Attachement
        if column == 'issue_last_attachment':
            attach_name = item.issue_last_attachment
            issue = item.name
            if attach_name is None:
                return None
            attach = resource.get_resource('%s/%s' % (issue, attach_name))
            #print item.name, attach, isinstance(attach, Video)
            if isinstance(attach, Image) is True:
                img_template = '<img src="./%s/%s_LOW/;download"/>'
                return XMLParser(img_template % (issue, attach_name))
            elif isinstance(attach, Video) is True:
                #print("%s.thumbnail = %s" % (issue, attach.metadata.get_property('thumbnail')))
                if attach.metadata.get_property('thumbnail') == 'True':
                    img_template = '<img \
                        src="./%s/%s_thumb/;thumb?width=256&amp;height=256"/>'
                #TODO: Don't think it can append, as we encode every video input file
                else:
                    img_template = '<img \
                        src="./%s/thumb_%s/;thumb?width=256&amp;height=256"/>'
                return XMLParser(img_template % (issue, attach_name))
            else:
                return None
        # Last Author
        elif column == 'issue_last_author':
            user_id = item.issue_last_author
            user = resource.get_resource('/users/%s' % user_id, soft=True)
            if user is None:
                return None
            return user.get_title()

        return Tracker_View.get_item_value(self, resource, context, item,
                                           column)

    def get_table_columns(self, resource, context):
        table_columns = Tracker_View.get_table_columns(self, resource, context)
        # Insert the last attachement row's title in the table
        table_columns.insert(2, ('issue_last_attachment', 'Last Attach.'))
        table_columns.insert(11, ('issue_last_author', 'Last Auth.'))
        return table_columns



class Tchacker_View(CompositeView):

    access = 'is_allowed_to_view'
    subviews = [Tchacker_ViewTop(),
                Tchacker_ViewBottom()]

    context_menus = [StoreSearchMenu(),
                     Tchacker_ViewMenu()]
    scripts = ['/ui/tchacker/tracker.js']
    styles = ['/ui/tchacker/style.css', '/ui/tracker/style.css' ]

    """
    def GET(self, resource, context):
        context.scripts.append('/ui/tchacker/tracker.js')
        context.styles.append('/ui/tchacker/tracker.css')
        return CompositeView.GET(self, resource, context)
    """

class Tracker_Zip_Img(Tchacker_ViewBottom):

    access = 'is_allowed_to_view'
    title = MSG(u'Zip Last Images')

    def GET(self, resource, context):
        items = self.get_items(resource, context)
        issues = self.sort_and_batch(resource, context, items)
        # Get path of all attachment to add in zip
        dirname = '%s/zip' % mkdtemp('zip', 'ikaaro')
        zip = ZipFile(dirname, 'w')
        for issue in issues:
            attachment_name = issue.issue_last_attachment
            attachment = resource.get_resource('%s/%s' % (issue.name, attachment_name))
            attachment_uri = attachment.handler.key
            # Get extension
            mimetype = attachment.get_content_type()
            ext = guess_extension(mimetype)[1:]
            attachment_name = '%s_%s.%s' % (issue.name, issue.title, ext) 
            zip.write(attachment_uri, attachment_name)
        zip.close()
        # Create zip
        # Build zipname
        name = "LastAttachedImages"
        now = strftime("%y%d%m%H%M")
        #pprint("%s" % now)
        zipname = "%s_%s_%s.zip" % (resource.name, name, now)

        file = open(dirname)
        try:
            data = file.read()
        finally:
            file.close()

        vfs.remove(dirname)

        # Return the zip
        context.set_content_type('application/zip')
        context.set_content_disposition('attachment; filename=%s' % zipname)
        return data

