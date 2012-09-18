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

from ikaaro.comments import Comment
from ikaaro.fields import Boolean_Field
from ikaaro.fields import Integer_Field, Decimal_Field
from ikaaro.fields import URI_Field
from ikaaro.file import Image, Video


class Tchacker_Image(Image):
    class_id = Image.class_id
    has_thumb = Boolean_Field
    is_thumb = Boolean_Field


class Tchacker_Video(Video):
    class_id = Video.class_id
    has_thumb = Boolean_Field
    width = Integer_Field
    height = Integer_Field
    ratio = Decimal_Field


class Tchacker_Comment(Comment):
    class_id = Comment.class_id
    attachement = URI_Field


# Remove "is_thumb" from indexation
def is_image_content(self):
    try:
        if self.metadata.get_property("is_thumb"):
            return False
    except AttributeError:
        pass
    return super(Image, self).is_content


Image.is_content = property(is_image_content)
