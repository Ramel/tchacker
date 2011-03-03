# -*- coding: UTF-8 -*-
# Copyright (C) 2008 David Versmisse <david.versmisse@itaapy.com>
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
from itools.datatypes import Unicode, Integer

# Import from ikaaro
from ikaaro.cc import UsersList
from ikaaro.datatypes import FileDataType
from ikaaro.tracker.datatypes import TrackerList, Tracker_UsersList
from ikaaro.tracker.datatypes import ProductInfoList


def get_issue_fields(tracker):
    return {
            'title': Unicode(mandatory=True),
            'product': TrackerList(element='product', tracker=tracker,
                                    mandatory=True),
            'module': ProductInfoList(element='module', tracker=tracker),
            'version': ProductInfoList(element='version', tracker=tracker),
            'type': TrackerList(element='type', tracker=tracker, mandatory=True),
            'state': TrackerList(element='state', tracker=tracker, mandatory=True),
            'priority': TrackerList(element='priority', tracker=tracker),
            'assigned_to': Tracker_UsersList(resource=tracker),
            'cc_list': Tracker_UsersList(resource=tracker, multiple=True),
            'comment': Unicode,
            'attachment': FileDataType,
            'amount': Integer}
