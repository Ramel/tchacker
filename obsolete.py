# -*- coding: UTF-8 -*-
# Copyright (C) 2006-2009 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
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

from itools.core import freeze, merge_dicts
from itools.datatypes import String, Integer, Boolean, Decimal

from ikaaro.file import Image, Video



Image.class_schema = freeze(merge_dicts(
        Image.class_schema,
        thumbnail=String(source='metadata'),
        ))

register_resource_class(Image)
