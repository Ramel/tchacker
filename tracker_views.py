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

# Import from itools
from itools.gettext import MSG
from itools.uri import encode_query
from itools.xml import XMLParser
from itools.datatypes import Unicode

# Import from ikaaro
from ikaaro.tracker.tracker_views import Tracker_View, StoreSearchMenu
from ikaaro.tracker.tracker_views import TrackerViewMenu, Tracker_Search
from ikaaro.tracker.tracker_views import Tracker_AddIssue
from ikaaro.tracker.datatypes import get_issue_fields

from monkey import Image, Video


class Tchacker_ViewMenu(TrackerViewMenu):

    title = MSG(u'Advanced')

    def get_items(self, resource, context):
        # Keep the query parameters
        schema = self.context.view.get_query_schema()
        params = encode_query(self.context.query, schema)
        return [
            {'title': MSG(u'Download "Last Att." images as one Zip'),
             'href': ';zip?%s' % params}
              ] + TrackerViewMenu.get_items(resource, context)



class Tchacker_View(Tracker_View):

    access = 'is_allowed_to_view'
    title = MSG(u'View')
    icon = 'view.png'
    scripts = ['/ui/tchacker/tracker.js']
    styles = ['/ui/tchacker/style.css', '/ui/tracker/style.css' ]

    context_menus = [
                    TrackerViewMenu(),
                    StoreSearchMenu(),
                    #Tchacker_ViewMenu()]
                    ]
    # XXX
    table_template = '/ui/tchacker/browse_table.xml'
    #context.styles.append('/ui/tchacker/tracker.css')


    def get_item_value(self, resource, context, item, column):
        # Last Attachement
        if column == 'last_attachment':
            attach_name = item.last_attachment
            issue = item.name
            if attach_name is None:
                return None
            attach = resource.get_resource('%s/%s' % (issue, attach_name))
            attachments = resource.get_resource(issue).get_attachments()
            if isinstance(attach, Image):
                image = resource.get_resource('%s/%s_LOW' % (issue, attach_name))
                width, height = image.handler.get_size()
                rollover = ""
                rollimages = ""
                quantity = len(attachments)
                if quantity >= 2:
                    part = width / quantity
                    i = 0
                    for attachment in attachments:
                        i += 1
                        rollover += '<div class="roll" style="width:%spx;height:%spx;" />' % (part, height)
                        rollimages += '<div class="roll" style="height:%spx;line-height:%spx;clip:rect(0px,%spx,%spx,0px);"><img \
                            src="./%s/%s_LOW/;download" /></div>' % (
                            height, height, width, height, issue, attachment)
                img_template = '<div id="num-%s" class="issue-roll">\
                    <div class="rollover">%s</div>\
                    <div class="rollimages">%s</div><img class="low" src="./%s/%s_LOW/;download"/>\
                </div>'
                return XMLParser(img_template % (issue, rollover, rollimages, issue, attach_name))
            if isinstance(attach, Video):
                thumb = attach.metadata.get_property('has_thumb')
                if thumb:
                    image = resource.get_resource('%s/%s_thumb' % (issue, attach_name))
                    width, height = image.handler.get_size()
                    # The encoded file already as a name "fn_low.flv" 
                    img_template = '<div style="position:relative">\
                        <div style="position:absolute;bottom:10px;right:10px">\
                            <img src="/ui/tchacker/redhat-sound_video.png" />\
                        </div>\
                        <img src="./%s/%s_thumb/;download" width="256" height="{height}" />\
                        </div>'.format(height=(256 * height/ width))
                #TODO: Don't think it can append, as we encode every video input file
                else:
                    img_template = '<img \
                        src="./%s/%s/;thumb?width=256&amp;height=256"/>'
                return XMLParser(img_template % (issue, attach_name))
            else:
                return None
        # Last Author
        if column == 'last_author':
            user_id = item.last_author
            user = resource.get_resource('/users/%s' % user_id, soft=True)
            if user is None:
                return None
            return user.get_title()
        return Tracker_View.get_item_value(self, resource, context, item,
                                           column)


    def get_table_columns(self, resource, context):
        table_columns = Tracker_View.get_table_columns(self, resource, context)
        # Insert the last attachement row's title in the table
        table_columns.insert(2, ('last_attachment', u'Last Attach.'))
        table_columns.insert(11, ('last_author', u'Last Auth.'))
        return table_columns



class Tchacker_Search(Tracker_Search):
    search_template = '/ui/tchacker/search.xml'

    def get_namespace(self, resource, context):
        get_resource = resource.get_resource
        products = get_resource('product')
        title = products.get_property('title') 
        namespace = Tracker_Search.get_namespace(self, resource, context)
        namespace['title'] = title
        columns = self.get_table_columns(resource, context)
        for name, label in columns:
            if label is not None:
                try:
                    get_resource(name)
                    title = get_resource(name).get_property('title')
                except LookupError:
                    pass
        return namespace



class Tchacker_AddIssue(Tracker_AddIssue):

    access = 'is_allowed_to_edit'
    title = MSG(u'Add')
    icon = 'new.png'
    template = '/ui/tracker/add_issue.xml'
    styles = ['/ui/tracker/style.css']
    scripts = ['/ui/tracker/tracker.js']


    def get_schema(self, resource, context):
        schema = get_issue_fields(resource)
        schema['comment'] = Unicode()
        return schema

    def get_namespace(self, resource, context):
        namespace = Tracker_AddIssue.get_namespace(self, resource, context)
        return namespace

    def action(self, resource, context, form):
        # Add
        id = resource.get_new_id()
        issue_cls = resource.issue_class
        issue = resource.make_resource(id, issue_cls)
        issue.add_comment(context, form, new=True)

        # Ok
        message = INFO(u'New issue added.')
        goto = './%s/' % id
        return context.come_back(message, goto=goto)
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
"""
