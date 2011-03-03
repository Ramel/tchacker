# -*- coding: UTF-8 -*-
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2008 Nicolas Deram <nicolas@itaapy.com>
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
from itools.core import get_abspath
from itools.core import get_version
from itools.fs import lfs
from itools.web import get_context

# Import from ikaaro
from ikaaro.registry import register_document_type
from ikaaro.skins import register_skin

#from issue import TchackerImage
#from issue import TchackerVideo
#from issue import Tchack_Issue
from tracker import Tchack_Tracker
from utils import which

# The version
__version__ = get_version()

# Register skin
path = get_abspath('ui')
register_skin('tchacker', path)

# Register document type
register_document_type(Tchack_Tracker)

###########################################################################
# Check required software
###########################################################################
for name, cli in [("zip", "zip")]:
    if(which(cli)) is None:
        print 'You need to install "%s".' % name

