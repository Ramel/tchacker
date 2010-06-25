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

# Import from itools
from itools.datatypes import String
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.registry import register_field
from ikaaro.tracker.issue import Issue

# Import from Tchacker
from issue_views import TchackIssue_Edit

# Import from videoencoding
#from videoencoding import VideoEncodingToFLV

from pprint import pprint

class Tchack_Issue(Issue):

    class_id = 'tchack_issue'
    class_version = '20071216'
    class_title = MSG(u'Tchack Issue')
    class_description = MSG(u'Tchack Issue')

    # Views
    edit = TchackIssue_Edit()

    def _get_catalog_values(self):
        values = Issue._get_catalog_values(self)
        history = self.get_history()
        # Get the last record
        record = history.get_record(-1)
        if record:
            values['issue_last_author'] = history.get_record_value(record, 'username')
        # Get last attachment
        values['issue_last_attachment'] = None
        for record in self.get_history_records():
            if record.file:
                values['issue_last_attachment'] = record.file
        return values
    
    """
    def _add_records(self, context, form):
        # Files XXX
        values = Issue._add_records(self, context, form)
        file = values.get_form_value('file')
        pprint("_add_records : file = %s" % file)
    """

    #def get_context_menus(self):
    #    return self.parent.get_context_menus() + [IssueTrackerMenu()]


###########################################################################
# Register
###########################################################################
# The class
register_resource_class(Tchack_Issue)
register_field('issue_last_attachment', String(is_stored=True))
register_field('issue_last_author', String(is_stored=True))

