# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2009 Armel Fortun <armel@tchack.com>
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
from itools.core import merge_dicts, proto_lazy_property
from itools.csv import CSVFile, Property
from itools.datatypes import Boolean, Integer, String, Unicode
from itools.gettext import MSG
from itools.handlers.utils import transmap
from itools.stl import stl
from itools.uri import encode_query, Reference
from itools.web import BaseView, STLView, FormError, INFO, ERROR
from itools.web.views import process_form
#from itools.uri import encode_query
from itools.xml import XMLParser

# Import from ikaaro
from ikaaro.autoform import TextWidget
from ikaaro.buttons import BrowseButton
from ikaaro import messages
from ikaaro.views import BrowseForm, ContextMenu
#from ikaaro.views_new import NewInstance
#from ikaaro.database import Database
from ikaaro.cc import Followers_Datatype

from issue import Issue
from datatypes import get_issue_fields, TchackerList, ProductInfoList
#from datatypes import Tchacker_UsersList
from stored import StoredSearch
from monkey import Image, Video


columns = [
    ('id', MSG(u'Id')),
    ('title', MSG(u'Title')),
    ('product', MSG(u'Product')),
    ('module', MSG(u'Module')),
    ('version', MSG(u'Version')),
    ('type', MSG(u'Type')),
    ('state', MSG(u'State')),
    ('priority', MSG(u'Priority')),
    ('assigned_to', MSG(u'Assigned To')),
    ('mtime', MSG(u'Modified'))]



###########################################################################
# Menus
###########################################################################
class GoToIssueMenu(ContextMenu):

    title = MSG(u'Go To Issue')
    template = '/ui/tchacker/menu_goto.xml'


    def path_to_tracker(self):
        return '..' if isinstance(self.resource, Issue) else '.'



class StoreSearchMenu(ContextMenu):
    """Form to store a search.
    """
    title = MSG(u'Remember this search')
    template = '/ui/tchacker/menu_remember.xml'

    def get_query_schema(self):
        resource = self.resource
        stored_search_class = resource.stored_search_class
        return merge_dicts(stored_search_class.class_handler.schema,
                           search_name=String,
                           search_title=Unicode)


    @proto_lazy_property
    def search_name(self):
        return self.context.get_query_value('search_name')


    @proto_lazy_property
    def search(self):
        search_name = self.search_name
        if search_name:
            return self.resource.get_resource(search_name, soft=True)
        return None


    def search_title(self):
        search = self.search
        return search.get_title() if search else None


    def search_fields(self):
        search = self.search
        if search:
            get = search.get_values
            stored_search_class = search
        else:
            # Warning, a menu is not the default view!
            query = process_form(self.context.get_query_value,
                                 self.get_query_schema())
            get = query.get

            resource = self.resource
            stored_search_class = resource.stored_search_class

        # Fill the fields
        fields = []
        for name, type in stored_search_class.class_handler.schema.iteritems():
            value = get(name)
            if isinstance(value, list):
                for x in value:
                    fields.append({'name': name, 'value': type.encode(x)})
            elif value is not None:
                fields.append({'name': name, 'value': type.encode(value)})

        # Ok
        return fields


    def forget_search(self):
        context = self.context
        search_name = context.get_query_value('search_name')
        if search_name is not None:
            resource = context.resource
            search = resource.get_resource(search_name, soft=True)
            ac = resource.get_access_control()
            if search and ac.is_allowed_to_edit(context.user, search):
                return True
        return False



class StoredSearchesMenu(ContextMenu):
    """Provides links to every stored search.
    """

    title = MSG(u'Stored Searches')

    def get_items(self):
        context = self.context
        resource = self.resource
        root = context.root

        # If called from a child
        if isinstance(resource, Issue):
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
            title = title.gettext(**kw)
            class_title = MSG(u'{search_title}')
            class_title = class_title.gettext(**kw).lower().replace(" ", "-").replace("_", "-")

            # Namespace
            items.append({'title': title,
                          'href': '%s?search_name=%s' % (base, item.name),
                          'class': 'nav-active' if (item.name == search_name)
                                                else class_title})
        items.sort(lambda x, y: cmp(x['title'], y['title']))

        return items



class TchackerViewMenu(ContextMenu):

    title = MSG(u'Advanced')

    def get_items(self, resource, context):
        # Keep the query parameters
        schema = self.context.view.get_query_schema()
        params = encode_query(self.context.query, schema)
        return [
            {'title': MSG(u'Edit this search'),
             'href': ';search?%s' % params},
            {'title': MSG(u'Change Several Issues'),
             'href': ';change_several_bugs?%s' % params},
            {'title': MSG(u'Export to Text'),
             'href': ';export_to_text?%s' % params},
            {'title': MSG(u'Export to CSV'),
             'href': ';export_to_csv_form?%s' % params},
            {'title': MSG(u'Download "Last Att." images as one Zip'),
             'href': ';zip?%s' % params}]



###########################################################################
# Views
###########################################################################
#class Tchacker_NewInstance(NewInstance):
#
#    schema = merge_dicts(NewInstance.schema, product=Unicode(mandatory=True))
#    widgets = NewInstance.widgets + [
#        TextWidget('product', title=MSG(u'Give the title of one Product'))]
#
#
#    def action(self, resource, context, form):
#        # Get the container
#        container = form['container']
#        # Make the resource
#        name = form['name']
#        class_id = context.query['type']
#        cls = Database.get_resource_class(class_id)
#        child = container.make_resource(name, cls)
#        # The metadata
#        language = container.get_edit_languages(context)[0]
#        title = Property(form['title'], lang=language)
#        child.metadata.set_property('title', title)
#        # Add the initial product
#        product = form['product']
#        table = container.get_resource('%s/product' % name).get_handler()
#        product = Property(product, language='en')
#        table.add_record({'title': product})
#        # Ok
#        goto = str(resource.get_pathto(child))
#        return context.come_back(messages.MSG_NEW_RESOURCE, goto=goto)
#


class Tchacker_AddIssue(STLView):

    access = 'is_allowed_to_edit'
    title = MSG(u'Add')
    icon = 'new.png'
    template = '/ui/tchacker/add_issue.xml'
    styles = ['/ui/tchacker/style.css']
    scripts = ['/ui/tchacker/tchacker.js']


    def get_schema(self, resource, context):
        schema = get_issue_fields(resource)
        comment = context.get_form_value('comment')
        attachment = context.get_form_value('attachment')
        if comment is None and attachment is True:
            schema['comment'] = Unicode(mandatory=False)
        if (comment is None or comment == '') and attachment is None:
            schema['comment'] = Unicode(mandatory=True)
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
        namespace = STLView.get_namespace(self, resource, context)
        namespace['list_products'] = resource.get_list_products_namespace()
        if(namespace['comment']['error'] is not None):
            namespace['comment']['error'] = MSG(
                u'This field is required (or can be emtpy if an attachment is joined)')
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



class Tchacker_View(BrowseForm):

    access = 'is_allowed_to_view'
    title = MSG(u'View')
    icon = 'view.png'
    scripts = ['/ui/tchacker/tchacker.js']
    styles = ['/ui/tchacker/style.css']

    schema = {
        'ids': String(multiple=True, mandatory=True)}

    tchacker_schema = {
        # Do not batch
        'batch_size': Integer(default=0),
        # search_fields
        'search_name': String(),
        'mtime': Integer(default=0),
        'product': Integer(multiple=True),
        'module': Integer(multiple=True),
        'version': Integer(multiple=True),
        'type': Integer(multiple=True),
        'state': Integer(multiple=True),
        'priority': Integer(multiple=True),
        'assigned_to': String(multiple=True),
        # Specific fields
        'search_field': String,
        'search_term': Unicode,
        # BrowseForm fields
        'sort_by': String,
        'reverse': Boolean(default=None),
    }

    context_menus = [TchackerViewMenu(), StoreSearchMenu()]
    
    # XXX
    table_template = '/ui/tchacker/browse_table.xml'

    
    def get_query_schema(self):
        return merge_dicts(BrowseForm.get_query_schema(self),
                           self.tchacker_schema)


    def on_query_error(self, resource, context):
        query = encode_query(context.uri.query)
        return context.come_back(None, goto=';search?%s' % query)


    def get_page_title(self, resource, context):
        query = getattr(context, 'query', {})
        search_name = query.get('search_name')
        if search_name:
            search = context.resource.get_resource(search_name, soft=True)
            if search:
                search = search.get_title()
                template = MSG(u'{title} - {search}')
                title = self.title.gettext()
                return template.gettext(title=title, search=search)

        return self.title


    def GET(self, resource, context):
        # Check stored search
        search_name = context.query['search_name']
        if search_name:
            search = resource.get_resource(search_name, soft=True)
            if search is None:
                msg = MSG(u'Unknown stored search "{sname}".')
                goto = ';search'
                return context.come_back(msg, goto=goto, sname=search_name)
        # Ok
        return BrowseForm.GET(self, resource, context)


    def get_namespace(self, resource, context):
        # Default table namespace
        namespace = BrowseForm.get_namespace(self, resource, context)

        # Keep the search_parameters, clean different actions
        schema = self.get_query_schema()
        namespace['search_parameters'] = encode_query(context.query, schema)

        return namespace


    def get_items(self, resource, context):
        return resource.get_search_results(context)


    def sort_and_batch(self, resource, context, results):
        query = context.query
        # Stored search, or default
        search_name = query['search_name']
        if search_name:
            search = resource.get_resource(search_name).handler
            sort_by = search.get_value('sort_by')
            reverse = search.get_value('reverse')
        else:
            sort_by = 'title'
            reverse = False
        # Query takes precedence
        if query['sort_by'] is not None:
            sort_by = query['sort_by']
        if query['reverse'] is not None:
            reverse = query['reverse']

        # Case 1: title
        if sort_by == 'title':
            items = results.get_documents()
            key = lambda x: x.title.lower().translate(transmap)
            items.sort(key=key, reverse=reverse)
            return items

        # Case 2: ordered table
        if sort_by in ('product', 'module', 'version', 'type', 'state',
                       'priority'):
            # Make the key function
            table_handler = resource.get_resource(sort_by).handler
            sorted_ids = list(table_handler.get_record_ids_in_order())

            def key(x):
                x_value = getattr(x, sort_by)
                try:
                    return sorted_ids.index(x_value)
                except ValueError:
                    return None

            # Sort
            items = results.get_documents()
            items.sort(key=key, reverse=reverse)

            # Return the result
            return items

        # Case 3: something else
        return results.get_documents(sort_by=sort_by, reverse=reverse)


    def get_item_value(self, resource, context, item, column):
        if column == 'checkbox':
            datatype = String(multiple=True)
            selected_issues = context.get_form_value('ids', type=datatype)
            return item.name, item.name in selected_issues
        if column == 'id':
            id = item.name
            return id, '%s/;edit' % id

        value = getattr(item, column)
        if value is None:
            return None
        if column == 'title':
            return value, '%s/;edit' % item.name
        # Assigned to
        if column == 'assigned_to':
            users = resource.get_resource('/users')
            user = users.get_resource(value, soft=True)
            if user is None:
                return None
            return user.get_title()
        # Mtime
        if column == 'mtime':
            return context.format_datetime(value)
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
            for filename in attachments:
                attachment = resource.get_resource('%s/%s' % (issue, filename))
                has_thumb = attachment.metadata.get_property('has_thumb') or False
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
            #thumbnails.reverse()
            quantity = len(thumbnails)
            if (quantity >= 1):
                rollover = ""
                rollimages = ""
                part = max_width / quantity
                if (quantity >= 2):
                    for thumb in thumbnails[:-1]:
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
                        #thumb_name = thumb['name']
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

        # Tables
        table = resource.get_resource(column).handler
        table_record = table.get_record(value)
        if table_record is None:
            return None
        return table.get_record_value(table_record, 'title')



    table_actions = []
    
    
    def get_table_columns(self, resource, context):
        table_columns = columns[:]
        table_columns.insert(0, ('checkbox', None))
        # Insert the last attachement row's title in the table
        table_columns.insert(2, ('last_attachment', MSG(u'Last Attach.')))
        table_columns.insert(11, ('last_author', MSG(u'Last Auth.')))
        return table_columns



class Tchacker_Search(Tchacker_View):
    
    access = 'is_allowed_to_view'
    title = MSG(u'Search')
    icon = 'search.png'
    styles = ['/ui/tchacker/style.css']
    scripts = ['/ui/tchacker/tchacker.js']


    # Search Form
    search_template = '/ui/tchacker/search.xml'
    search_schema = {
        'search_name': String(),
        'search_title': Unicode(),
        'text': Unicode(),
        'mtime': Integer(),
        'product': Integer(multiple=True),
        'module': Integer(multiple=True),
        'version': Integer(multiple=True),
        'type': Integer(multiple=True),
        'state': Integer(multiple=True),
        'priority': Integer(multiple=True),
        'assigned_to': String(multiple=True)
        }

    context_menus = []


    def get_query(self, context):
        try:
            return BrowseForm.get_query(self, context)
        except FormError:
            schema = self.get_query_schema()
            query = {}
            for name in schema:
                default = schema[name].get_default()
                query[name] = context.uri.query.get(name, default)
            return query


    on_query_error = BrowseForm.on_query_error

    
    def get_search_namespace(self, resource, context):
        # Search Form
        get_resource = resource.get_resource
        query = context.query
        search_name = query['search_name']
        if search_name:
            search = get_resource(search_name)
            get_value = search.handler.get_value
            get_values = search.get_values
            search_title = search.get_property('title')
        else:
            get_value = query.get
            get_values = query.get
            search_name = None
            search_title = query['search_title']

        # Build the namespace
        product = get_values('product')
        module = get_values('module')
        version = get_values('version')
        type = get_values('type')
        state = get_values('state')
        priority = get_values('priority')
        assigned_to = get_values('assigned_to')

        # is_admin
        ac = resource.get_access_control()
        pathto_website = resource.get_pathto(resource.get_site_root())

        return  {
           'search_name': search_name,
           'search_title': search_title,
           'text': get_value('text'),
           'mtime': get_value('mtime'),
           'is_admin': ac.is_admin(context.user, resource),
           'manage_assigned': '%s/;browse_users' % pathto_website,
           'products': TchackerList(element='product',
                                   tchacker=resource).get_namespace(product),
           'modules': ProductInfoList(element='module',
                                      tchacker=resource).get_namespace(module),
           'versions': ProductInfoList(element='version',
                                     tchacker=resource).get_namespace(version),
           'types': TchackerList(element='type',
                                tchacker=resource).get_namespace(type),
           'states': TchackerList(element='state',
                                 tchacker=resource).get_namespace(state),
           'priorities': TchackerList(element='priority',
                                 tchacker=resource).get_namespace(priority),
           'assigned_to': Followers_Datatype(
                              resource=resource).get_namespace(assigned_to),
           'list_products': resource.get_list_products_namespace()}

    
    """
    # XXX tchacker 0.62
    def get_namespace(self, resource, context):
        search_template = resource.get_resource(self.search_template)
        search_namespace = self.get_search_namespace(resource, context)
        return {
            'batch': None,
            'table': None,
            'search': stl(search_template, search_namespace)}
    """
    # XXX
    def get_namespace(self, resource, context):
        search_template = resource.get_resource(self.search_template)
        search_namespace = self.get_search_namespace(resource, context)
        get_resource = resource.get_resource
        products = get_resource('product')
        title = products.get_property('title')
        #namespace = .get_namespace(resource, context)
        namespace = self.get_search_namespace(resource, context)
        namespace['batch'] = None
        namespace['table'] = None
        namespace['search'] = stl(search_template, search_namespace)
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
    


class Tchacker_RememberSearch(BaseView):

    access = 'is_allowed_to_edit'

    def get_schema(self, resource, context):
        return merge_dicts(resource.stored_search_class.class_handler.schema,
                           search_name=String,
                           search_title=Unicode(mandatory=True))

    def GET(self, resource, context):
        # Required for when the form fails the automatic checks
        return context.come_back(message=context.message)


    def action(self, resource, context, form):
        search_name = form.get('search_name')
        title = form['search_title']

        # Already a (valid) search name ?

        # Check the search was not deleted before
        if search_name is not None:
            search = resource.get_resource(search_name, soft=True)
        # No
        if search_name is None or search is None:
            # Search for a search with the same title
            if isinstance(resource, Issue):
                resource = resource.parent
            searches = resource.search_resources(cls=StoredSearch)
            for search in searches:
                # Found !
                if title == search.get_property('title'):
                    search_name = search.name
                    message = MSG(u'The search has been modified.')
                    break
            else:
                # Not found => so we make a new search resource
                search_name = resource.get_new_id('s')
                search = resource.make_resource(search_name, StoredSearch)
                message = MSG(u'The search has been stored.')
        # Yes
        else:
            message = MSG(u'The search title has been changed.')

        # Reset the search
        search.handler.load_state_from_string('')

        # Set title
        language = resource.get_edit_languages(context)[0]
        search.set_property('title', title, language=language)

        # Save the value
        for name, type in search.class_handler.schema.iteritems():
            value = form.get(name, None)
            if value:
                search.set_values(name, value, type)

        # Go
        return context.come_back(message, goto=';view?search_name=%s' %
                                          search_name)



class Tchacker_ForgetSearch(BaseView):

    access = 'is_allowed_to_edit'
    schema = {
        'search_name': String(mandatory=True)}


    def action(self, resource, context, form):
        name = form['search_name']
        resource.del_resource(name)
        # Ok
        message = MSG(u'The search has been removed.')
        return context.come_back(message, goto=';search')



class Tchacker_GoToIssue(BaseView):

    access = 'is_allowed_to_view'

    def GET(self, resource, context):
        issue_name = context.get_form_value('issue_name')
        if not issue_name:
            return context.come_back(messages.MSG_NAME_MISSING)

        issue = resource.get_resource(issue_name, soft=True)
        if issue is None or not isinstance(issue, Issue):
            return context.come_back(ERROR(u'Issue not found.'))

        return context.uri.resolve2('../%s' % issue_name)



class Tchacker_ExportToCSVForm(Tchacker_View):

    template = '/ui/tchacker/export_to_csv.xml'
    external_form = True

    def get_query_schema(self):
        schema = Tchacker_View.get_query_schema(self)
        schema['ids'] = String(multiple=True, default=[])
        return schema


    def get_namespace(self, resource, context):
        namespace = Tchacker_View.get_namespace(self, resource, context)
        query = context.query

        # Insert query parameters as hidden input fields
        parameters = []
        schema = Tchacker_View.get_query_schema(self)
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



class Tchacker_ExportToCSV(BaseView):

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



class Tchacker_ExportToText(Tchacker_ExportToCSVForm):

    template = '/ui/tchacker/export_to_text.xml'

    def get_query_schema(self):
        schema = Tchacker_ExportToCSVForm.get_query_schema(self)
        schema['column_selection'] = String(multiple=True, default=['title'])
        return schema


    def get_namespace(self, resource, context):
        namespace = Tchacker_ExportToCSVForm.get_namespace(self, resource,
                                                          context)
        query = context.query

        # Column Selector
        selection = query['column_selection']
        export_columns = columns[2:] + [columns[1]]
        namespace['columns'] = [
            {'name': name, 'title': title, 'checked': name in selection}
            for name, title in export_columns ]

        # Text
        items = self.get_items(resource, context)
        items = self.sort_and_batch(resource, context, items)
        selected_items = query['ids']
        if selected_items:
            items = [ x for x in items if x.name in selected_items ]
        items = [ get_issue_informations(resource, x, context) for x in items ]
        # Create the text
        lines = []
        for item in items:
            name = item['name']
            line = [u'#%s' % name]
            for x in selection:
                value = item[x]
                if type(value) is unicode:
                    pass
                elif type(value) is str:
                    value = unicode(value, 'utf-8')
                else:
                    value = unicode(value)
                line.append(value)
            line = u'\t'.join(line)
            lines.append(line)
        namespace['text'] = u'\n'.join(lines)

        # Ok
        return namespace



class Tchacker_ChangeSeveralBugs(Tchacker_View):

    access = 'is_allowed_to_view'
    title = MSG(u'Change Several Issues')
    template = '/ui/tchacker/change_bugs.xml'
    scripts = ['/ui/tchacker/tchacker.js']
    schema = {
        'comment': Unicode,
        'ids': String(multiple=True),
        'change_product': Integer,
        'change_module': Integer,
        'change_version': Integer,
        'change_type': Integer,
        'change_priority': Integer,
        'change_assigned_to': String,
        'change_state': Integer,
    }

    external_form = True

    table_actions = [
        BrowseButton(name='change_several_bugs', title=MSG(u'Edit issues'))]


    def get_namespace(self, resource, context):
        namespace = Tchacker_View.get_namespace(self, resource, context)
        # Edit several bugs at once
        get_resource = resource.get_resource
        namespace['products'] = get_resource('product').get_options()
        namespace['modules'] = get_resource('module').get_options()
        namespace['versions'] = get_resource('version').get_options()
        namespace['priorities'] = get_resource('priority').get_options()
        namespace['types'] = get_resource('type').get_options()
        namespace['states'] = get_resource('state').get_options()
        namespace['assigned_to'] = Followers_Datatype(
                                      resource=resource).get_namespace('')
        namespace['list_products'] = resource.get_list_products_namespace()

        # Ok
        return namespace


    def action(self, resource, context, form):
        # Get search results
        results = resource.get_search_results(context)
        if isinstance(results, Reference):
            return results

        # Selected issues
        issues = results.get_documents()
        selected_issues = form['ids']
        issues = [ x for x in issues if x.name in selected_issues ]

        if len(issues) == 0:
            context.message = ERROR(u"No issue selected.")
            return

        # Modify all issues selected
        names = ['product', 'module', 'version', 'type', 'priority', 'state']
        comment = form['comment']
        user = context.user
        username = user and user.name or ''
        users_issues = {}
        for issue in issues:
            issue = resource.get_resource(issue.name)
            old_metadata = issue.metadata.clone()
            # Assign-To
            assigned_to = issue.get_property('assigned_to')
            new_assigned_to = form['change_assigned_to']
            if new_assigned_to == 'do-not-change':
                issue.set_property('assigned_to', assigned_to)
            else:
                issue.set_property('assigned_to', new_assigned_to)
            # Integer Fields
            for name in names:
                new_value = form['change_%s' % name]
                if new_value == -1:
                    issue.set_property(name, issue.get_property(name))
                else:
                    issue.set_property(name, new_value)
            # Comment
            p_comment = Property(comment, author=username,
                                 date=context.timestamp)
            modifications = issue.get_diff_with(old_metadata, context)
            if modifications:
                title = MSG(u'Modifications:').gettext()
                p_comment.value += u'\n\n%s\n\n%s' % (title, modifications)
            issue.metadata.set_property('comment', p_comment)

            # Mail (create a dict with a list of issues for each user)
            info = {'href': context.uri.resolve(issue.name),
                    'name': issue.name,
                    'title': issue.get_title()}
            if new_assigned_to and new_assigned_to != 'do-not-change':
                users_issues.setdefault(new_assigned_to, []).append(info)
            if assigned_to and assigned_to != new_assigned_to:
                users_issues.setdefault(assigned_to, []).append(info)
            # Change
            context.database.change_resource(issue)

        # Send mails
        root = context.root
        site_root = resource.get_site_root()
        website_languages = site_root.get_property('website_languages')
        default_language = site_root.get_default_language()
        if user is None:
            user_title = MSG(u'ANONYMOUS').gettext()
        else:
            user_title = user.get_title()
        template = MSG(
            u'--- Comment from: {user} ---\n\n{comment}\n\n{issues}')
        tchacker_title = resource.get_property('title') or 'Tchacker Issue'
        subject = u'[%s]' % tchacker_title
        for user_id in users_issues:
            user = root.get_user(user_id)
            if not user:
                continue
            # Find a good language
            language = user.get_property('user_language')
            if language not in website_languages:
                language = default_language
            # Construct the body
            user_issues = [
                u'#%s - %s - %s' % (x['href'], x['name'], x['title'])
                for x in users_issues[user_id]
            ]
            user_issues = '\n'.join(user_issues)
            body = template.gettext(user=user_title, comment=comment,
                                    issues=user_issues, language=language)
            # And send !
            to_addr = user.get_property('email')
            root.send_email(to_addr, subject, text=body)

        context.message = messages.MSG_CHANGES_SAVED



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

    # Modification Time
    infos['mtime'] = context.format_datetime(item.mtime)

    return infos



"""
class Tchacker_Zip_Img(Tchacker_ViewBottom):

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
