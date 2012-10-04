# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2012 Armel FORTUN <armel@tchack.com>
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
from itools.core import merge_dicts
from itools.datatypes import Boolean, String
from itools.datatypes import Enumerate
from itools.gettext import MSG
from itools.database import PhraseQuery, AndQuery
from itools.uri import normalize_path

# Import from ikaaro
from ikaaro.autoform import title_widget, CheckboxWidget, SelectWidget
from ikaaro.autoform import ReadOnlyWidget
from ikaaro.config_common import NewResource_Local
from ikaaro.resource_ import DBResource
from ikaaro.fields import Field #Multilingual
from ikaaro.order import OrderedFolder, OrderedFolder_BrowseContent
from ikaaro.autoedit import AutoEdit
from ikaaro.autoadd import AutoAdd
from ikaaro.enumerates import DynamicEnumerate_Field



###########################################################################
# Views
###########################################################################
class SelectTable_View(OrderedFolder_BrowseContent):

    access = 'is_allowed_to_view'

    def get_table_columns(self, resource, context):
        proxy = super(SelectTable_View, self)
        columns = proxy.get_table_columns(resource, context)
        columns = columns[:]
        columns.append(('issues', MSG(u'Issues')))
        if resource.name == 'product':
            # Add specific columns for the product table
            columns.append(('modules', MSG(u'Modules')))
            columns.append(('versions', MSG(u'Versions')))
        return columns


    def get_item_value(self, resource, context, item, column):
        # Append a column with the number of issues
        if column == 'issues':
            filter = str(resource.name)

            # Build the search query
            query_terms = resource.parent.get_issues_query_terms()
            query_terms.append(PhraseQuery(filter, item.name))
            query = AndQuery(*query_terms)

            # Search
            results = context.search(query)
            count = len(results)
            if count == 0:
                return 0, None
            return count, '../;view?%s=%s' % (filter, item.name)
        # Don't show the "edit" link when i am not an admin.
        elif column == 'id':
            ac = resource.get_access_control()
            is_admin =  ac.is_admin(context.user, resource)

            id = item.id
            if is_admin:
                link = context.get_link(resource)
                return id, '%s/;edit_record?id=%s' % (link, id)
            else:
                return id

        # Default
        proxy = super(SelectTable_View, self)
        value = proxy.get_item_value(resource, context, item, column)

        # FIXME The field 'product' is reserved to make a reference to the
        # 'products' table.  Currently it is used by the 'versions' and
        # 'modules' tables.
        # The fields 'modules' and 'versions' is reserved to make reference to
        # the 'modules' and 'versions' tables. Currently it is used by the
        # 'product' table
        if column == 'product':
            return resource.get_resource('../product/%s' % value).get_title()
        elif column in ('modules', 'versions'):
            # Strip 's' modules -> module
            associated_table = resource.get_resource('../%s' % column[:-1])
            # Search
            results = [ x for x in associated_table.get_resources()
                        if x.get_value('product') == item.name ]
            count = len(results)
            if count == 0:
                return 0, None
            return count, '%s/;view' % context.get_link(associated_table)

        return value


    def sort_and_batch(self, resource, context, items):
        # Sort
        sort_by = context.query['sort_by']
        if sort_by != 'issues':
            proxy = super(SelectTable_View, self)
            return proxy.sort_and_batch(resource, context, items)

        reverse = context.query['reverse']
        f = lambda x: self.get_item_value(resource, context, x, 'issues')[0]
        items.sort(cmp=lambda x,y: cmp(f(x), f(y)), reverse=reverse)

        # Batch
        start = context.query['batch_start']
        size = context.query['batch_size']
        return items[start:start+size]


    def action_remove(self, resource, context, form):
        ids = form['ids']
        parent = resource.parent
        # Search all issues
        query_terms = parent.get_issues_query_terms()
        query = AndQuery(*query_terms)
        results = context.root.search(query)

        # Associated modules and versions
        check_associated = (resource.name == 'product')
        module = parent.get_resource('module')
        version = parent.get_resource('version')
        module_handler = module.handler
        version_handler = version.handler

        # Remove values only if no issues have them
        handler = resource.handler
        filter = str(resource.name)
        removed = []
        for id in ids:
            query = PhraseQuery(filter, id)
            count = len(results.search(query))
            if check_associated:
                module_count = len(module_handler.search('product', str(id)))
                version_count = len(version_handler.search('product', str(id)))
                count = count + module_count + version_count
            if count == 0:
                handler.del_record(id)
                removed.append(str(id))

        # Ok
        message = MSG(u'Resources removed: {resources}.')
        message = message.gettext(resources=', '.join(removed)).encode('utf-8')
        context.message = message


###########################################################################
# Resources
###########################################################################
class Tchacker_Item(DBResource):
    class_id = 'tchacker_item'
    class_title = MSG(u"Tchacker Item")
    title = DBResource.title(required=True)

    new_instance = AutoAdd(fields=['title'])


class Tchacker_TableResource(OrderedFolder):

    class_id = 'tchacker_select_table'
    class_title = MSG(u'Select Table')
    class_views = OrderedFolder.class_views + ['add_item']

    # Hide in browse_content
    is_content = False

    form = [title_widget]


    def get_document_types(self):
        return [Tchacker_Item]

    def get_options(self, value=None, sort=None):
        # Find out the options
        handler = self.handler
        options = []
        for id in handler.get_record_ids_in_order():
            record = handler.get_record(id)
            title = handler.get_record_value(record, 'title')
            options.append({'id': id, 'title': title})

        # Sort
        if sort is not None:
            options.sort(key=lambda x: x.get(sort))

        # Set 'is_selected'
        if value is None:
            for option in options:
                option['is_selected'] = False
        elif isinstance(value, list):
            for option in options:
                option['is_selected'] = (option['id'] in value)
        else:
            for option in options:
                option['is_selected'] = (option['id'] == value)

        return options


    view = SelectTable_View
    add_item = NewResource_Local(title=MSG(u'Add item'),
                                 include_subclasses=False)



class Modules_Item_New(AutoAdd):
    fields = ['title', 'product']
    def get_field(self, name):
        field = super(Modules_Item_New, self).get_field(name)
        if name == 'product':
            path = normalize_path('%s/../product' % self.resource.abspath)
            return field(resource_path=path)
        return field


class Modules_Item_Edit(AutoEdit):

    fields = ['title', 'product']
    def get_field(self, resource, name):
        field = super(Modules_Item_Edit, self).get_field(resource, name)
        if name == 'product':
            path = normalize_path('%s/../../product' % self.resource.abspath)
            return field(resource_path=path, widget=ReadOnlyWidget)
        return field



class Modules_Item(Tchacker_Item):

    class_id = "modules-item"
    class_views = ['edit']

    product = DynamicEnumerate_Field(required=True, title=MSG(u'Product'),
                                     widget=SelectWidget)

    new_instance = Modules_Item_New
    edit = Modules_Item_Edit



class ModulesResource(Tchacker_TableResource):

    class_id = 'tchacker_modules'

    def get_document_types(self):
        return [Modules_Item]



class VersionsResource(ModulesResource):

    class_id = 'tchacker_versions'
