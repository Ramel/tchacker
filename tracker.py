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

# Import from itools
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.tracker import Tracker
from ikaaro.registry import register_resource_class

#from resources import Tchack_Resources
from issue import Tchack_Issue
from tracker_views import Tchacker_View, Tracker_Zip_Img


class Tchack_Tracker(Tracker):

    class_id = 'tchack_tracker'
    class_version = '20090706'
    class_title = MSG(u'Tchack Issue Tracker')
    class_description = MSG(u'To manage images, bugs and tasks')
    class_views = Tracker.class_views + ['zip']

    # Configuration
    issue_class = Tchack_Issue

    # Views
    view = Tchacker_View()
    zip = Tracker_Zip_Img()


###########################################################################
# Register
###########################################################################

register_resource_class(Tchack_Tracker)
