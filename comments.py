# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Juan David IBÁÑEZ PALOMAR <jdavid@itaapy.com>
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
from itools.datatypes import Unicode, String, DateTime
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.fields import Owner_Field
from ikaaro.comments import Comment, CommentState_Field
from ikaaro.comments import Comment_View, indent

from monkey import Image, Video



tchacker_comment_datatype = Unicode(source='metadata', multiple=True,
                            parameters_schema={'date': DateTime,
                            'author': String,
                            'attachment': String})



def has_comment(att):
    """Hack, if comment is empty, but has an attachment
    we force the value of comment to False, so it doesn't be shown
    by STL.
    """
    if (att == "comment_is_empty_but_has_attachment"):
        value = False
    else:
        value = indent(att)
    return value



class Tchacker_Comment_View(Comment_View):

    template = '/ui/tchacker/comments.xml'

    def get_namespace(self, resource, context):
        root = context.root

        comments = resource.metadata.get_property('comment') or []
        attachments = resource.metadata.get_property('attachment') or []

        attached = [{ 'link': False,
                    'is_image': False,
                    'is_video': False,
                    'format': False,
                    }] * len(comments)

        for attachment in attachments:
            j = attachment.get_parameter('comment')
            file = resource.get_resource(str(attachment.value))

            has_thumb = False
            image = isinstance(file, Image) or False
            video = isinstance(file, Video) or False
            fileformat = file.metadata.format or False

            if image or video:
                has_thumb = file.get_property('has_thumb') or False

            if video and has_thumb:
                video = {
                    'width': file.get_property('width'),
                    'height': file.get_property('height'),
                    'ratio': file.get_property('ratio')
                    }

            attached[j] = {
                    'link': file.name,
                    'is_image': image or False,
                    'is_video': video or False,
                    'format': fileformat
                    }

        # Get resource metadata values: is_video, is_image
        # TODO: Perhaps we need to run this if comments is not empty
        comments = [
            {'number': i + 1,
             'user': root.get_user_title(x.get_parameter('author')),
             'datetime': context.format_datetime(x.get_parameter('date')),
             'comment': has_comment(x.value),
             'attachment': attached[i]
             }
            for i, x in enumerate(comments) ]

        comments.reverse()
        return {'comments': comments}



class Tchacker_Comment(Comment):

    class_id = 'comment'
    class_title = MSG(u'Comment')

    # Fields
    title = None
    subject = None
    owner = Owner_Field
    comment_state = CommentState_Field
    attachment = None

    # Sharing is acquired from container
    share = None
    def get_share(self):
        return self.parent.get_share()

    # Views
    view = Tchacker_Comment_View
