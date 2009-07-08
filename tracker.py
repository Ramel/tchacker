# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
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
from datetime import datetime, timedelta
from operator import itemgetter
from string import Template

# Import from itools
from itools.csv import Property
from itools.datatypes import Integer, String, Unicode
from itools.gettext import MSG
from itools.uri import Reference
from itools.web import ERROR
from itools.xapian import RangeQuery, AndQuery, OrQuery, PhraseQuery
from itools.xapian import StartQuery

# Import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class
from resources import Tchack_Resources
from stored import Tchack_StoredSearch, StoredSearchFile
from tables import Tracker_TableResource, Tracker_TableHandler
from tables import ModulesResource, ModulesHandler
from tables import VersionsResource, VersionsHandler
from tracker_views import GoToIssueMenu, StoredSearchesMenu
from tracker_views import Tracker_NewInstance, Tracker_Search, Tracker_View
from tracker_views import Tracker_Zip_Img
from tracker_views import Tracker_AddIssue, Tracker_GoToIssue
from tracker_views import Tracker_RememberSearch, Tracker_ForgetSearch
from tracker_views import Tracker_ExportToText, Tracker_ChangeSeveralBugs
from tracker_views import Tracker_ExportToCSVForm, Tracker_ExportToCSV


resolution = timedelta.resolution



default_types = [u'Color Set', u'B&W Set', u'Props']

default_tables = [
    ('product', []),
    ('type', default_types),
    ('state', [u'Awaiting validation', u'Validated', u'In Progress']),
    ('priority', [u'High', u'Medium', u'Low']),
    ]


class Tchack_Tracker(Folder):

    class_id = 'tchack_tracker'
    class_version = '20090706'
    class_title = MSG(u'Tchack Issue Tracker')
    class_description = MSG(u'To manage images, bugs and tasks')
    class_icon16 = 'tracker/tracker16.png'
    class_icon48 = 'tracker/tracker48.png'
    class_views = ['view', 'add_issue', 'search', 'browse_content', 'edit']

    __fixed_handlers__ = ['product', 'module', 'version', 'type', 'priority',
        'state', 'calendar']

    @staticmethod
    def _make_resource(cls, folder, name):
        Folder._make_resource(cls, folder, name)
        # Products / Types / Priorities / States
        for table_name, values in default_tables:
            table_path = '%s/%s' % (name, table_name)
            table = Tracker_TableHandler()
            for title in values:
                title = Property(title, language='en')
                table.add_record({'title': title})
            folder.set_handler(table_path, table)
            metadata = Tracker_TableResource.build_metadata()
            folder.set_handler('%s.metadata' % table_path, metadata)
        # Modules
        table = ModulesHandler()
        folder.set_handler('%s/module' % name, table)
        metadata = ModulesResource.build_metadata()
        folder.set_handler('%s/module.metadata' % name, metadata)
        # Versions
        table = VersionsHandler()
        folder.set_handler('%s/version' % name, table)
        metadata = VersionsResource.build_metadata()
        folder.set_handler('%s/version.metadata' % name, metadata)
        # Pre-defined stored searches
        to_validate = StoredSearchFile(state='0')
        validate = StoredSearchFile(state='1')
        work_in_progress = StoredSearchFile(state='2')
        not_assigned = StoredSearchFile(assigned_to='nobody')
        high_priority = StoredSearchFile(state='0', priority='0')
        i = 0
        for search, title in [(to_validate, u'Awaiting validation'),
                              (validate, u'Validated'),
                              (not_assigned, u'Non assigned'),
                              (high_priority, u'High Priority')]:
            folder.set_handler('%s/s%s' % (name, i), search)
            metadata = Tchack_StoredSearch.build_metadata(title={'en': title})
            folder.set_handler('%s/s%s.metadata' % (name, i), metadata)
            i += 1
        metadata = Tchack_Resources.build_metadata()
        folder.set_handler('%s/calendar.metadata' % name, metadata)


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
        # If the issue is not of Issue's class_type type for xapian
        class_id_issue = 'tchack_issue'
        abspath = self.get_canonical_path()
        abspath = '%s/' % abspath
        return [StartQuery('abspath', abspath),
                PhraseQuery('format', class_id_issue)]


    def get_members_namespace(self, value, not_assigned=False):
        """Returns a namespace (list of dictionaries) to be used for the
        selection box of users (the 'assigned to' and 'cc' fields).
        """
        # Members
        users = self.get_resource('/users')
        members = [
            {'id': x, 'title': users.get_resource(x).get_title()}
            for x in self.get_site_root().get_members() ]
        sort_cmp = lambda x, y: cmp(x['title'].lower(), y['title'].lower())
        members.sort(cmp=sort_cmp)

        # Not assigend
        if not_assigned is True:
            members.insert(0, {'id': 'nobody', 'title': 'NOT ASSIGNED'})

        # Add 'is_selected'
        if value is None:
            condition = lambda x: False
        elif type(value) is str:
            condition = lambda x: (x == value)
        else:
            condition = lambda x: (x in value)
        for member in members:
            member['is_selected'] = condition(member['id'])

        # Ok
        return members


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
            date = date.strftime('%Y%m%d%H%M%S')
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
        users = self.get_resource('/users')
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
    new_instance = Tracker_NewInstance()
    search = Tracker_Search()
    view = Tracker_View()
    zip = Tracker_Zip_Img()
    add_issue = Tracker_AddIssue()
    remember_search = Tracker_RememberSearch()
    forget_search = Tracker_ForgetSearch()
    go_to_issue = Tracker_GoToIssue()
    export_to_text = Tracker_ExportToText()
    export_to_csv_form = Tracker_ExportToCSVForm()
    export_to_csv = Tracker_ExportToCSV()
    change_several_bugs = Tracker_ChangeSeveralBugs()

    #######################################################################
    # Update
    #######################################################################
    def update_20090705(self):
        """
        Encode the unencoded MOV or AVI file, and add the thumb, erase the
        original file.
        """
        from pprint import pprint
        from datetime import datetime
        from tempfile import mkdtemp
        
        from issue import Tchack_Issue
        from ikaaro.file import Video
        from ikaaro.exceptions import ConsistencyError
        from itools import vfs
        from itools.vfs import FileName
        from itools.core import guess_extension
        from itools.uri import get_uri_path
        from videoencoding import VideoEncodingToFLV
        from ikaaro.registry import get_resource_class
        #TODO
        for issue in self.search_resources(cls=Tchack_Issue):
            base = issue.get_abspath()
            history = issue.get_history()

            for record in history.get_records():
                file = history.get_record_value(record, 'file')
                if not file:
                    continue
                if file:
                    video = issue.get_resource(file)
                    is_video = isinstance(video, Video)
                    pprint("video.handler.uri = %s" % issue.handler.uri)
                    pprint("====================")
                    if is_video:
                        #video = resource.get_resource(file)
                        pprint("video name = %s" % file)
                        base = video.metadata.uri
                        mimetype = video.metadata.format
                        #body = video.get_handler()
                        name = video.name
                        filename, ext, lang = FileName.decode(name)
                        if ext is None:
                            mimetype = video.get_content_type()
                            ext = guess_extension(mimetype)[1:]
                        #if ext != "flv":
                        if(mimetype == 'video/x-msvideo' or mimetype == 'video/quicktime'):
                            handler_path = get_uri_path(issue.handler.uri)
                            pprint("MimeType = %s, Handler_path = %s" % (mimetype, handler_path))
                            pprint("FileName = %s, Base = %s, Ext = %s" % (filename, base, ext))
                            dirname = mkdtemp('videoencoding', 'ikaaro')
                            tempdir = vfs.open(dirname)
                            # Paste the file in the tempdir
                            file = tempdir.make_file(filename) #"%s.%s" % (filename, ext))
                            try:
                                pprint("dirname = %s" % dirname)
                                file.write(video.handler.to_str())
                            finally:
                                file.close()
                            # Encode to 540 of width
                            encoded = VideoEncodingToFLV(video).encode_avi_to_flv(
                                 dirname, filename, name, 540)

                            if encoded is not None:
                                flvfilename, flvmimetype, flvbody, flvextension = encoded['flvfile']
                                thumbfilename, thumbmimetype, thumbbody, thumbextension = encoded['flvthumb']
        
                            file.close()
                            # Clean the temporary folder
                            vfs.remove(dirname)
                            """
                            # Create the video FLV and thumbnail PNG resources
                            video = get_resource_class(flvmimetype)
                            thumbnail = get_resource_class(thumbmimetype)
                            video.make_resource(video, self, name, body=flvbody, filename=flvfilename,
                                extension=flvextension, format=flvmimetype)
                            thumbnail.make_resource(thumbnail, self, thumbfilename, body=thumbbody, filename=thumbfilename,
                                extension=thumbextension, format=thumbmimetype)
                            """

###########################################################################
# Register
###########################################################################
register_resource_class(Tchack_Tracker)
