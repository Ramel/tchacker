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

# Import from the Standard Library
from datetime import datetime, timedelta

# Import from itools
from itools.csv import Property
from itools.datatypes import Integer, String, Unicode #, Tokens
from itools.gettext import MSG
from itools.database import RangeQuery, AndQuery, OrQuery, PhraseQuery

# Import from ikaaro
from ikaaro.folder import Folder
from ikaaro.utils import get_base_path_query
#from ikaaro.database import Database

from issue import Issue
from tchacker_views import Tchacker_View #, Tchacker_Zip_Img
from tchacker_views import GoToIssueMenu, StoredSearchesMenu
from tchacker_views import Tchacker_AddIssue, Tchacker_GoToIssue
from tchacker_views import Tchacker_ExportToCSVForm, Tchacker_ExportToCSV
from tchacker_views import Tchacker_ExportToText, Tchacker_ChangeSeveralBugs
#from tchacker_views import Tchacker_NewInstance
from tchacker_views import Tchacker_Search
from tchacker_views import Tchacker_RememberSearch, Tchacker_ForgetSearch
from tables import Tchacker_TableResource, Tchacker_TableHandler
from stored import StoredSearch, StoredSearchFile
from tables import ModulesResource, ModulesHandler
from tables import VersionsResource, VersionsHandler


resolution = timedelta.resolution


default_types = [
    u'Bug', u'New Feature', u'Security Issue', u'Stability Issue',
    u'Data Corruption Issue', u'Performance Improvement',
    u'Technology Upgrade']

default_tables = [
    ('product', []),
    ('type', default_types),
    ('state', [u'Open', u'Fixed', u'Verified', u'Closed']),
    ('priority', [u'High', u'Medium', u'Low']),
    ]


class Tchacker(Folder):

    class_id = 'tchacker'
    class_version = '20120202'
    class_title = MSG(u'Tchack Tracker')
    class_description = MSG(u'To manage images, videos, bugs and tasks')
    class_icon16 = 'tchacker/tchacker16.png'
    class_icon48 = 'tchacker/tchacker48.png'
    class_views = ['search', 'add_issue', 'browse_content', 'edit']  #+ ['zip']

    __fixed_handlers__ = ['product', 'module', 'version', 'type', 'priority',
        'state']

    # Configuration
    issue_class = Issue
    stored_search_class = StoredSearch

    def init_resource(self, **kw):
        Folder.init_resource(self, **kw)
        # Products / Types / Priorities / States
        folder = self.handler
        for table_name, values in default_tables:
            self.make_resource(table_name, Tchacker_TableResource)
            table = Tchacker_TableHandler()
            for title in values:
                title = Property(title, language='en')
                table.add_record({'title': title})
            folder.set_handler(table_name, table)
        # Modules
        self.make_resource('module', ModulesResource)
        table = ModulesHandler()
        folder.set_handler('module', table)
        # Versions
        self.make_resource('version', VersionsResource)
        table = VersionsHandler()
        folder.set_handler('version', table)
        # Pre-defined stored searches
        open = StoredSearchFile(state='0')
        not_assigned = StoredSearchFile(assigned_to='nobody')
        high_priority = StoredSearchFile(state='0', priority='0')
        i = 0
        for search, title in [(open, u'Open Issues'),
                              (not_assigned, u'Not Assigned'),
                              (high_priority, u'High Priority')]:
            self.make_resource('s%s' % i, StoredSearch, title={'en': title})
            folder.set_handler('s%s' % i, search)
            i += 1


    def get_document_types(self):
        return []


    #######################################################################
    # API
    #######################################################################
    def get_new_id(self, prefix=''):
        ids = []
        for name in self.get_names():
            if prefix:
                if not name.startswith(prefix):
                    continue
                name = name[len(prefix):]
            try:
                id = int(name)
            except ValueError:
                continue
            ids.append(id)

        if ids:
            ids.sort()
            return prefix + str(ids[-1] + 1)

        return prefix + '0'


    def get_issues_query_terms(self):
        return [get_base_path_query(self.get_canonical_path()),
                PhraseQuery('format', self.issue_class.class_id)]


    def get_list_products_namespace(self):
        # Build javascript list of products/modules/versions
        products = self.get_resource('product').handler

        list_products = [{'id': '-1', 'modules': [], 'versions': []}]
        for product_record in products.get_records_in_order():
            product = {'id': product_record.id}
            for element in ['module', 'version']:
                elements = self.get_resource(element).handler

                content = []
                for record in elements.get_records_in_order():
                    product_id = elements.get_record_value(record, 'product')
                    if product_id is None:
                        continue
                    product_id = int(product_id)
                    if product_id == product_record.id:
                        content.append( {
                         'id': record.id,
                         'value': elements.get_record_value(record, 'title')})
                product[element + 's'] = content
            list_products.append(product)

        return list_products


    def get_search_query(self, get_value):
        """This method is like get_search_results, but works with
           get_value and returns a query
        """
        # Get search criteria
        text = get_value('text', type=Unicode)
        if text is not None:
            text = text.strip().lower()
        mtime = get_value('mtime', type=Integer)

        # Build the query
        query = self.get_issues_query_terms()
        # Text search
        if text:
            # XXX The language of text should be given
            #     => {'en': text}
            query2 = [PhraseQuery('title', text), PhraseQuery('text', text)]
            query2 = OrQuery(*query2)
            query.append(query2)
        # Metadata
        integers_type = Integer(multiple=True)
        names = 'product', 'module', 'version', 'type', 'priority', 'state'
        for name in names:
            data = get_value(name, type=integers_type)
            if len(data) > 0:
                query2 = [ PhraseQuery(name, value) for value in data ]
                query2 = OrQuery(*query2)
                query.append(query2)
        # Modification time
        if mtime:
            date = datetime.now() - timedelta(mtime)
            query2 = RangeQuery('mtime', date, None)
            query.append(query2)
        # Assign To
        assigns = get_value('assigned_to', type=String(multiple=True))
        if len(assigns) > 0:
            query2 = []
            for value in assigns:
                value = value or 'nobody'
                query2.append(PhraseQuery('assigned_to', value))
            query2 = OrQuery(*query2)
            query.append(query2)

        # Return the query
        return AndQuery(*query)


    def get_search_results(self, context):
        """Method that return a list of issues that correspond to the search.
        """
        # Choose stored Search or personalized search
        search_name = context.query.get('search_name')
        if search_name:
            search = self.get_resource(search_name)
            get_value = search.handler.get_value
        else:
            get_value = context.get_query_value

        # Compute the query and return the result
        query = self.get_search_query(get_value)
        return context.root.search(query)


    #######################################################################
    # User Interface
    #######################################################################
    context_menus = [GoToIssueMenu(), StoredSearchesMenu()]

    # Views
    new_instance = Tchacker_NewInstance()
    search = Tchacker_Search()
    view = Tchacker_View()
    add_issue = Tchacker_AddIssue()
    remember_search = Tchacker_RememberSearch()
    forget_search = Tchacker_ForgetSearch()
    go_to_issue = Tchacker_GoToIssue()
    export_to_text = Tchacker_ExportToText()
    export_to_csv_form = Tchacker_ExportToCSVForm()
    export_to_csv = Tchacker_ExportToCSV()
    change_several_bugs = Tchacker_ChangeSeveralBugs()

