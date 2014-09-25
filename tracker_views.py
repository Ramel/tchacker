# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
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

# Import from standard library
from base64 import b64encode

# Import from itools
from itools.gettext import MSG
from itools.csv import CSVFile
from itools.uri import encode_query
from itools.xml import XMLParser
from itools.datatypes import Unicode
from itools.web import INFO
from itools.web import get_context
from itools.core import freeze
from itools.datatypes import String

# Import from ikaaro
from ikaaro.tracker.issue_views import ProductsSelectWidget
from ikaaro.autoform import TextWidget, SelectWidget
from ikaaro.autoform import ProgressBarWidget, FileWidget, MultilineWidget
from ikaaro.tracker.tracker_views import Tracker_View, StoreSearchMenu
from ikaaro.tracker.tracker_views import StoredSearch, StoredSearchesMenu
from ikaaro.tracker.tracker_views import TrackerViewMenu, Tracker_Search
from ikaaro.tracker.tracker_views import Tracker_AddIssue, Tracker_ExportToCSV
from ikaaro.tracker.tracker_views import columns
from ikaaro.tracker.tracker_views import Tracker_AddIssue
from ikaaro.tracker.datatypes import get_issue_fields

from issue import Tchack_Issue
from monkey import Image, Video


class Tchack_TrackerViewMenu(TrackerViewMenu):

    title = MSG(u'Advanced')

    def get_items(self, resource, context):
        # Keep the query parameters
        schema = self.context.view.get_query_schema()
        params = encode_query(self.context.query, schema)
        return [
            {'title': MSG(u'Download "Last Att." images as one Zip'),
             'href': ';zip?%s' % params}
              ] + TrackerViewMenu.get_items(resource, context)



class Tchack_Tracker_View(Tracker_View):

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
            width = 0
            height = 0
            max_width = 0
            max_height = 0
            image = False
            video = False
            #print("%s: attachments = %s" % (issue, attachments))
            for filename in attachments:
                attachment = resource.get_resource('%s/%s' % (issue, filename))
                image = isinstance(attachment, Image)
                video = isinstance(attachment, Video)
                #print("attachment = %s" % attachment)
                has_thumb = attachment.metadata.get_property(
                                    'has_thumb') or None
                #print("1) has_thumb = %s" % has_thumb)
                if has_thumb is None:
                    continue
                else:
                    has_thumb = attachment.metadata.get_property(
                                    'has_thumb').value

                #print("2) has_thumb = %s" % has_thumb)
                if has_thumb:
                    if image:
                        endfile = "_LOW"
                        link = ';download'
                        image = True
                        thumbnail = resource.get_resource(
                                        '%s/%s%s' % (issue, filename, endfile))
                        width, height = thumbnail.handler.get_size()
                    if video:
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
                    #print('%s/%s%s' % (issue, filename, endfile))

                # Or use the default ikaaro's thumbnails
                else:
                    if image is False and video is False:
                        continue
                    if image:
                        endfile = ""
                        link= ";thumb?width=256&amp;height=256"
                        thumbnail = resource.get_resource(
                                        "%s/%s" % (issue, filename))
                        height = 256
                        width = 256
                        # Run Cron?
                        need_thumb = attachment.metadata.get_property(
                                    'need_thumb') or None
                        if need_thumb is not None:
                            need_thumb = attachment.metadata.get_property(
                                    'need_thumb').value or False
                            #print("## %s -> need_thumb = %s" % (filename, need_thumb))
                            if need_thumb:
                                from cron import run_cron
                                server = context.server
                                server.run_cron()
                    if video:
                        endfile = "_thumb"
                        link = ';thumb?width=256&amp;height=256'
                        video = True
                        thumbnail = resource.get_resource(
                                        '%s/%s%s' % (issue, filename, endfile))
                        width, height = thumbnail.handler.get_size()
                        # Thumbnail is certainly widder than 256 px
                        height = 256 * height / width
                        width = 256
                    if (max_width < width):
                        max_width = width
                    if (max_height < height):
                        max_height = height
                # Add an image to the Thumbnails
                thumbnails.append({
                                'name': filename + endfile,
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

        if column == "state":
            state_template = '<span class="state-{state}">{value}</span>'
            # Tables
            table = resource.get_resource(column).handler
            table_record = table.get_record(item.state)

            value = table.get_record_value(table_record, 'title')

            return XMLParser(state_template.format(
                                    state=item.state,
                                    value=value.encode('utf8')))

        return Tracker_View.get_item_value(self, resource, context, item, column)


    def get_table_columns(self, resource, context):
        table_columns = Tracker_View.get_table_columns(self, resource, context)
        # Insert the last attachement row's title in the table
        table_columns.insert(2, ('last_attachment', MSG(u'Last Attach.')))
        table_columns.insert(11, ('last_author', MSG(u'Last Auth.')))
        return table_columns


class Tchack_LastComments_View(Tracker_View):

    access = 'is_allowed_to_view'
    title = MSG(u'View')
    icon = 'view.png'
    scripts = ['/ui/tchacker/tracker.js']
    styles = ['/ui/tchacker/style.css', '/ui/tracker/style.css' ]

    context_menus = [
                    TrackerViewMenu(),
                    StoreSearchMenu(),
                    ]
    # XXX
    table_template = '/ui/tchacker/browse_table.xml'


    def get_item_value(self, resource, context, item, column):

        issue = item.name
        # Last Attachment
        if column == 'last_attachment':
            attach_name = item.last_attachment
            if attach_name is None:
                return None
            attach = resource.get_resource('%s/%s' % (issue, attach_name))
            if isinstance(attach, Image):
                img_template = '<img src="./%s/%s_LOW/;download"/>'
                return XMLParser(img_template % (issue, attach_name))
            if isinstance(attach, Video):
                thumb = attach.metadata.get_property('has_thumb')
                if thumb:
                    # The encoded file already as a name "fn_low.flv"
                    img_template = '<img \
                        src="./%s/%s_thumb/;thumb?width=256&amp;height=256"/>'
                #TODO: Don't think it can append, as we encode every video input file
                else:
                    img_template = '<img \
                        src="./%s/%s/;thumb?width=256&amp;height=256"/>'
                return XMLParser(img_template % (issue, attach_name))
            else:
                return None

        """
        # Last Author
        if column == 'last_author':
            user_id = item.last_author
            user = resource.get_resource('/users/%s' % user_id, soft=True)
            if user is None:
                return None
            return user.get_title()
        """

        # Last comments
        if column == 'last_comments':
            #comments =  resource.get_resource(issue).get_comments_ordered()
            #print("%s" % comments)
            #la =  resource.get_resource(issue).get_last_attachment()
            #print("%s" % la)
            last_comments_id =  resource.get_resource(issue).get_last_attachment_id()
            #print("%s" % glaid)
            last_comments = resource.get_resource(
                                    issue).get_last_comments_from_id(last_comments_id)
            last_comments = ''.join(['<p>%s</p>' % k for k in last_comments])
            return XMLParser(last_comments.encode("utf-8"))


    def get_table_columns(self, resource, context):
        table_columns = Tracker_View.get_table_columns(self, resource, context)
        del table_columns[2:11]
        #table_columns.pop(3)
        # Insert the last attachement row's title in the table
        table_columns.insert(2, ('last_attachment', MSG(u'Last Attach.')))
        table_columns.insert(3, ('last_comments', MSG(u'Last Comments')))
        #table_columns.insert(11, ('last_author', MSG(u'Last Auth.')))
        return table_columns



"""
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
"""



class Tchack_Tracker_AddIssue(Tracker_AddIssue):

    styles = ['/ui/tracker/style.css',
              '/ui/tchacker/style.css', '/ui/thickbox/style.css']
    scripts = ['/ui/tchacker/tracker.js', '/ui/thickbox/thickbox.js',
               '/ui/flowplayer/flowplayer-3.2.2.min.js']
    access = 'is_allowed_to_edit'

    widgets = freeze([
        TextWidget('title', title=MSG(u'Title:'),
                                classes=['left-center', 'light']),
        SelectWidget('assigned_to', title=MSG(u'Assigned To:'),
                                classes=['right', 'light']),
        ProductsSelectWidget('product', title=MSG(u'Product:'),
                                classes=['left', 'light']),
        SelectWidget('type', title=MSG(u'Type:'), classes=['center', 'light']),
        SelectWidget('cc_list', title=MSG(u'CC:'), classes=['right', 'light']),
        SelectWidget('module', title=MSG(u'Module:'), classes=['left', 'light']),
        SelectWidget('state', title=MSG(u'State:'), classes=['center']),
        SelectWidget('version', title=MSG(u'Version:'),
                                classes=['left', 'light']),
        SelectWidget('priority', title=MSG(u'Priority:'),
                                classes=['center', 'light']),
        MultilineWidget('comment', title=MSG(u'New Comment:'), classes=['all']),
        FileWidget('attachment', title=MSG(u'Attachment (<512Mo):'), classes=['all']),
        ProgressBarWidget()
        ])

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
        #namespace = Tracker_AddIssue.get_namespace(self, resource, context)
        proxy = super(Tracker_AddIssue, self)
        namespace = proxy.get_namespace(resource, context)
        widgets = namespace['widgets']
        for name in widgets:
            if name['name'] == 'comment':
                if name['error'] is not None:
                    name['error'] = MSG(u"""This field is required (or can be left
                        emtpy if an attachment is joined)""")
        return namespace

    def action(self, resource, context, form):
        comment = form['comment']
        attachment = form['attachment']
        if comment == '' and attachment is not None:
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


class Tchack_StoredSearchesMenu(StoredSearchesMenu):
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
                          'href': '%s?search_name=%s' % (base, item.name),
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



class Tchack_Tracker_ExportToCSVForm(Tchack_Tracker_View):

    template = '/ui/tchacker/export_to_csv.xml'
    external_form = True

    def get_query_schema(self):
        schema = Tchack_Tracker_View.get_query_schema(self)
        schema['ids'] = String(multiple=True, default=[])
        return schema


    def get_namespace(self, resource, context):
        namespace = Tchack_Tracker_View.get_namespace(self, resource, context)
        query = context.query

        # Insert query parameters as hidden input fields
        parameters = []
        schema = Tchack_Tracker_View.get_query_schema(self)
        for name in schema:
            if name in namespace:
                continue
            value = query[name]
            datatype = schema[name]
            if datatype.multiple is True:
                for value in value:
                    value = datatype.encode(value)
                    parameters.append({'name': name, 'value': value})
            else:
                default = datatype.get_default()
                if value != default:
                    value = datatype.encode(value)
                    parameters.append({'name': name, 'value': value})
        namespace['hidden_fields'] = parameters

        return namespace



class Tchack_Tracker_ExportToCSV(Tracker_ExportToCSV):

    access = 'is_allowed_to_view'
    title = MSG(u'Export to CSV')
    query_schema = {
        'editor': String(default='excel'),
        'ids': String(multiple=True),
    }


    def GET(self, resource, context):
        # Get search results
        results = resource.get_search_results(context)
        if isinstance(results, Reference):
            return results

        # Selected issues
        issues = results.get_documents()
        selected_issues = context.query['ids']
        if selected_issues:
            issues = [ x for x in issues if x.name in selected_issues ]

        if len(issues) == 0:
            context.message = ERROR(u"No data to export.")
            return

        # Get CSV encoding and separator (OpenOffice or Excel)
        editor = context.query['editor']
        if editor == 'oo':
            separator = ','
            encoding = 'utf-8'
        else:
            separator = ';'
            encoding = 'cp1252'

        # Create the CSV
        csv = CSVFile()
        for issue in issues:
            issue = get_issue_informations(resource, issue, context)
            row = []
            # Insert the last attachement row's title in the table
            columns.insert(2, ('last_attachment', MSG(u'Last Attach.')))
            columns.insert(11, ('last_author', MSG(u'Last Auth.')))
            for name, label in columns:
                value = issue[name]
                if isinstance(value, unicode):
                    value = value.encode(encoding)
                else:
                    value = str(value)
                row.append(value)
            csv.add_row(row)

        # Ok
        context.set_content_type('text/comma-separated-values')
        context.set_content_disposition('attachment', 'export.csv')
        return csv.to_str(separator=separator)



def get_issue_informations(resource, item, context):
    """Construct a dict with issue informations.  This dict is used to
    construct a line for a table.
    """
    # Build the namespace
    infos = {
        'name': item.name,
        'id': item.id,
        'title': item.title}

    # Select Tables
    get_resource = resource.get_resource
    print("get_resource = %s" % get_resource)
    tables = ['product', 'module', 'version', 'type', 'state', 'priority']
    for name in tables:
        infos[name] = None
        value = getattr(item, name)
        if value is None:
            continue
        table = get_resource(name).handler
        table_record = table.get_record(value)
        if table_record is None:
            continue
        infos[name] = table.get_record_value(table_record, 'title')

    # Assigned-To
    assigned_to = getattr(item, 'assigned_to')
    infos['assigned_to'] = ''
    if assigned_to:
        users = resource.get_resource('/users')
        user = users.get_resource(assigned_to, soft=True)
        if user is not None:
            infos['assigned_to'] = user.get_title()
    # Last-Attachement
    last_attachment = getattr(item, 'last_attachment')
    infos['last_attachment'] = last_attachment
    # Last-Author
    last_author = getattr(item, 'last_author')
    infos['last_author'] = ''
    if last_author:
        users = resource.get_resource('/users')
        user = users.get_resource(last_author, soft=True)
        if user is not None:
            infos['last_author'] = user.get_title()
    #infos['last_attachment'] = last_attachment

    # Modification Time
    infos['mtime'] = context.format_datetime(item.mtime)

    return infos
