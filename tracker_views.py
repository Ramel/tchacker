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
from itools.web import INFO

# Import from ikaaro
from ikaaro.tracker.tracker_views import Tracker_View, StoreSearchMenu
from ikaaro.tracker.tracker_views import StoredSearch
from ikaaro.tracker.tracker_views import StoredSearchesMenu
from ikaaro.tracker.tracker_views import TrackerViewMenu, Tracker_Search
from ikaaro.tracker.tracker_views import Tracker_AddIssue
from ikaaro.tracker.datatypes import get_issue_fields


from monkey import Image, Video
from issue import Tchack_Issue


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
    styles = ['/ui/tchacker/style.css']

    context_menus = [
                    TrackerViewMenu(),
                    StoreSearchMenu(),
                    #Tchacker_ViewMenu()]
                    ]
    # XXX
    table_template = '/ui/tchacker/browse_table.xml'
    #context.styles.append('/ui/tchacker/tracker.css')


    def get_item_value(self, resource, context, item, column):
        # Last Attachment
        if column == 'last_attachment':
            attach_name = item.last_attachment
            issue = item.name
            if attach_name is None:
                return None
            #last_attachment = resource.get_resource('%s/%s' % (issue, attach_name))
            attachments = resource.get_resource(issue).get_attachments_ordered()
            thumbnails = []
            max_width = 0
            max_height = 0
            #print("%s: attachments = %s" % (issue, attachments))
            for filename in attachments:
                attachment = resource.get_resource('%s/%s' % (issue, filename))
                #print("attachment = %s" % attachment)
                has_thumb = attachment.metadata.get_property(
                                    'has_thumb') or False
                #print("%s -> has_thumb = %s" % (filename, has_thumb))
                if has_thumb:
                    image = False
                    video = False
                    if isinstance(attachment, Image):
                        endfile = "_LOW"
                        link = ';download'
                        image = True
                        thumbnail = resource.get_resource(
                                        '%s/%s%s' % (issue, filename, endfile))
                        width, height = thumbnail.handler.get_size()
                    if isinstance(attachment, Video):
                        endfile = "_thumb"
                        link = ';thumb?width=256&amp;height=256'
                        video = True
                        thumbnail = resource.get_resource(
                                        '%s/%s%s' % (issue, filename, endfile))
                        width, height = thumbnail.handler.get_size()
                        # video thumbnail is certainly widder than 256 px
                        height = 256 * height / width
                        width = 256
                    if (max_width < width):
                        max_width = width
                    if (max_height < height):
                        max_height = height
                    thumbnails.append({ 'name' : filename + endfile,
                                    'link': link,
                                    'width': width,
                                    'height': height,
                                    'image': image,
                                    'video': video})
                else:
                    image = False
                    video = False
                    if isinstance(attachment, Image):
                        endfile = ";thumb?width=256&amp;height=256"
                        link = ';download'
                        image = True
                        thumbnail = resource.get_resource(
                                        '%s/%s%s' % (issue, filename, endfile))
                        width, height = thumbnail.handler.get_size()
                        # Thumbnail is certainly widder than 256 px
                        height = 256 * height / width
                        width = 256
                    if isinstance(attachment, Video):
                        endfile = "_thumb"
                        link = ';thumb?width=256&amp;height=256'
                        video = True
                        thumbnail = resource.get_resource(
                                        '%s/%s%s' % (issue, filename, endfile))
                        width, height = thumbnail.handler.get_size()
                        # video thumbnail is certainly widder than 256 px
                        height = 256 * height / width
                        width = 256
                    if (max_width < width):
                        max_width = width
                    if (max_height < height):
                        max_height = height
                    thumbnails.append({ 'name' : filename + endfile,
                                    'link': link,
                                    'width': width,
                                    'height': height,
                                    'image': image,
                                    'video': video})
            #thumbnails.reverse()
            #print("%s: thumbnails = %s" % (issue, thumbnails))
            quantity = len(thumbnails)
            if (quantity >= 1):
                rollover = ""
                rollimages = ""
                part = max_width / quantity
                #print thumbnails[-1]
                if (quantity >= 2):
                    for thumb in thumbnails[:-1]:
                        #print("%s: %s" % (issue, thumb))
                        rollover += '<div class="roll" \
                                style="width:%spx;height:%spx;" />' % (
                                part, max_height)
                        if thumb['image']:
                            rollimages += '<div class="roll" \
                                style="height:{height}px;line-height:{height}px;"><img \
                                src="./{issue}/{name}/{link}" /></div>'.format(
                                    height=max_height,
                                    issue=issue,
                                    name=thumb['name'],
                                    link=thumb['link'])
                        if thumb['video']:
                            rollimages += '<div class="roll" \
                                style="height:{height}px;line-height:{height}px;">\
                                <div style="position:relative"><div \
                                style="position:absolute;right:10px;line-height:{height}px">\
                                    <img style="vertical-align:-{vertical}px" src="/ui/tchacker/redhat-sound_video.png" />\
                                </div>\
                                <img style="vertical-align:middle" src="./{issue}/{name}/{link}" />\
                                </div>\
                                </div>'.format(
                                    height=max_height,
                                    vertical=thumb['height'] / 2 - 12,
                                    issue=issue,
                                    name=thumb['name'],
                                    link=thumb['link'])
                        thumb_name = thumb['name']
                        link = thumb['link']
                if thumbnails[-1]['image']:
                    last_img_template = '<img class="thumbnail" style="vertical-align:middle" \
                        src="./{issue}/{thumb_name}/{link}"/>'.format(
                                        issue=issue,
                                        thumb_name=thumbnails[-1]['name'],
                                        link=thumbnails[-1]['link'])
                if thumbnails[-1]['video']:
                    last_img_template = '<div style="position:relative" \
                        class="thumbnail"><div \
                            style="position:absolute;right:10px;line-height:{height}px">\
                            <img style="vertical-align:-{vertical}px" src="/ui/tchacker/redhat-sound_video.png" />\
                        </div>\
                        <img style="vertical-align:middle" src="./{issue}/{thumb_name}/{link}" />\
                        </div>'.format(
                                issue=issue,
                                thumb_name=thumbnails[-1]['name'],
                                link=thumbnails[-1]['link'],
                                height=max_height,
                                vertical=thumbnails[-1]['height'] / 2 - 12)
                img_template = '<div id="num-{issue}" class="issue-roll" \
                            style="line-height:{max_height}px">\
                        <div class="rollover">{rollover}</div><div \
                        class="rollimages">{rollimages}</div>{last_img_template}\
                    </div>'
                return XMLParser(img_template.format(
                                        issue=issue,
                                        max_height=max_height,
                                        rollover=rollover,
                                        rollimages=rollimages,
                                        last_img_template=last_img_template))
            else:
                return None

        # Last Author
        if column == 'last_author':
            user_id = item.last_author
            user = resource.get_resource('/users/%s' % user_id, soft=True)
            if user is None:
                return None
            return user.get_title()

        return Tracker_View.get_item_value(self, resource, context, item, column)


    def get_table_columns(self, resource, context):
        table_columns = Tracker_View.get_table_columns(self, resource, context)
        # Insert the last attachement row's title in the table
        table_columns.insert(2, ('last_attachment', MSG(u'Last Attach.')))
        table_columns.insert(11, ('last_author', MSG(u'Last Auth.')))
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
    scripts = ['/ui/tchacker/tracker.js']


    def get_schema(self, resource, context):
        schema = get_issue_fields(resource)
        comment = context.get_form_value('comment')
        attachment = context.get_form_value('attachment')
        #print("get_schema:comment = %s" % comment)
        if comment is None and attachment is True:
            schema['comment'] = Unicode(mandatory=False)
            #print("comment=None; attachment=True")
        if (comment is None or comment == '') and attachment is None:
            schema['comment'] = Unicode(mandatory=True)
            #print("comment=None; attachment=None")
        #schema['comment'] = Unicode(mandatory=True)
        return schema

    def get_value(self, resource, context, name, datatype):
        if getattr(datatype, 'mandatory', False):
            datatype = datatype(mandatory=False)
        value = context.get_query_value(name, type=datatype)
        # By default, set cc_list to the current user
        if name == 'cc_list' and not value:
            return [context.user.name]
        return value

    def get_namespace(self, resource, context):
        namespace = Tracker_AddIssue.get_namespace(self, resource, context)
        if(namespace['comment']['error'] is not None):
            namespace['comment']['error'] = MSG(
                u'This field is required (or can be emtpy if an attachment is joined)')
        return namespace

    def action(self, resource, context, form):
        comment = form['comment']
        attachment = form['attachment']
        #print("Action:comment = %s" % (comment))
        if comment == '' and attachment is not None:
            #print("Action: comment == '' and attachment is not None")
            form['comment'] = "comment_is_empty_but_has_attachment"

        # Add
        id = resource.get_new_id()
        issue_cls = resource.issue_class
        issue = resource.make_resource(id, issue_cls)
        issue.add_comment(context, form, new=True)

        # Ok
        message = INFO(u'New issue added.')
        goto = './%s/' % id
        return context.come_back(message, goto=goto)



class Tchacker_StoredSearchesMenu(StoredSearchesMenu):
    """Provides links to every stored search.
    """

    title = MSG(u'Stored Searches')

    def get_items(self):
        context = self.context
        resource = self.resource
        root = context.root

        # If called from a child
        if isinstance(resource, Tchack_Issue):
            resource = resource.parent

        # Namespace
        search_name = context.get_query_value('search_name')
        base = '%s/;view' % context.get_link(resource)
        items = []
        ac = resource.get_access_control()
        for item in resource.search_resources(cls=StoredSearch):
            if not ac.is_allowed_to_view(context.user, item):
                continue
            # Make the title
            get_value = item.handler.get_value
            query = resource.get_search_query(get_value)
            issues_nb = len(root.search(query))
            kw = {'search_title': item.get_property('title'),
                  'issues_nb': issues_nb}
            title = MSG(u'{search_title} ({issues_nb})')
            class_title = MSG(u'{search_title}')
            title = title.gettext(**kw)
            class_title = class_title.gettext(**kw).lower().replace(" ", "-").replace("_", "-")

            # Namespace
            items.append({'title': title,
                          'href': '%s?search_name=%s&sort_by=title' % (base, item.name),
                          'class': 'nav-active' if (item.name == search_name)
                                                else class_title})
        items.sort(lambda x, y: cmp(x['title'], y['title']))

        return items



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
