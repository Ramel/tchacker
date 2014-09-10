# -*- coding: UTF-8 -*-
# Copyright (C) 2011 Henry Obein <henry@itaapy.com>
# Copyright (C) 2011 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2011 Armel FORTUN <armel@tchack.com>
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
from itools.datatypes import Integer, Boolean, Decimal, String
from itools.database import register_field

from ikaaro.file import Image, Video


Image.class_schema = freeze(merge_dicts(
        Image.class_schema,
        has_thumb=Boolean(source='metadata', indexed=True),
        need_thumb=Boolean(source='metadata', indexed=True),
        is_thumb=Boolean(source='metadata')))


Video.class_schema = freeze(merge_dicts(
        Video.class_schema,
        has_thumb=Boolean(source='metadata'),
        is_video=Boolean(source='metadata', indexed=True),
        encoded=Boolean(source='metadata', indexed=True),
        tmp_folder=String(source='metadata'),
        width=Integer(source='metadata'),
        height=Integer(source='metadata'),
        ratio=Decimal(source='metadata')))


# Remove "is_thumb" from indexation
def is_image_content(self):
    try:
        if self.metadata.get_property("is_thumb"):
            return False
    except AttributeError:
        pass
    return super(Image, self).is_content


Image.is_content = property(is_image_content)
register_field('has_thumb', Boolean(indexed=True))
register_field('need_thumb', Boolean(indexed=True))
