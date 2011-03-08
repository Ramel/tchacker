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
from itools.datatypes import Integer, String, Unicode
from itools.datatypes import Boolean, Decimal, Tokens
from itools.handlers import Image as ImageHandler
#from itools.handlers import Image
from itools.handlers import register_handler_class

from ikaaro.file import Image, Video
from ikaaro.registry import register_resource_class


#ImageHandler.class_mimetypes = ImageHandler.class_mimetypes + ['tchacker_image',
#'tchacker_image_thumb']


#print("ImageHandler.class_mimetypes = %s" % ImageHandler.class_mimetypes)


Image.class_schema = freeze(merge_dicts(
        Image.class_schema,
        has_thumb=Boolean(source='metadata'),
        is_thumb=Boolean(source='metadata')))


#Image.class_handler = ImageHandler


Video.class_schema = freeze(merge_dicts(
        Video.class_schema,
        has_thumb=Boolean(source='metadata'),
        width=Integer(source='metadata'),
        height=Integer(source='metadata'),
        ratio=Decimal(source='metadata')))


#register_handler_class(ImageHandler)
## TODO restore ikaaro class_id
register_resource_class(Image, format='tchacker_image')
register_resource_class(Image, format='tchacker_image_thumb')
register_resource_class(Video, format='tchacker_video')
