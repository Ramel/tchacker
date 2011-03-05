# -*- coding: UTF-8 -*-
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

# Import from itools
from itools.core import merge_dicts
from itools.datatypes import Integer, String, Unicode
from itools.datatypes import Boolean, Decimal, Tokens
from itools.handlers import Image as ImageHandler
#from itools.handlers import register_handler_class


# Import from ikaaro
from ikaaro.file import Video, Image
from ikaaro.registry import register_resource_class

"""
class Image(Image):

    class_mimetypes = ['image', 'tchacker_image']
"""

class TchackerImage(Image):
    
    #class_id = 'image'
    class_id = 'tchacker_image'
    #class_handler = ImageHandler
    class_schema = merge_dicts(
        Image.class_schema,
        # Metadata
        has_thumb=Boolean(source='metadata'))



class TchackerVideo(Video):
    
    #class_id = 'image'
    class_id = 'tchacker_video'
    #class_handler = ImageHandler
    class_schema = merge_dicts(
        Video.class_schema,
        # Metadata
        has_thumb=Boolean(source='metadata'),
        width=Integer(source='metadata'),
        height=Integer(source='metadata'),
        ratio=Decimal(source='metadata'))


class TchackerImageThumb(Image):
    
    #class_id = 'image'
    class_id = 'tchacker_image_thumb'
    #class_handler = ImageHandler
    class_schema = merge_dicts(
        Image.class_schema,
        # Metadata
        is_thumb=Boolean(source='metadata'))


###########################################################################
# Register
###########################################################################
# The class
#register_handler_class(Image)
register_resource_class(TchackerImageThumb)
register_resource_class(TchackerImage)
register_resource_class(TchackerVideo)
