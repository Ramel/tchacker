# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
from itools.datatypes import Boolean, Integer

# Import from ikaaro
from ikaaro.comments import CommentsView, indent


tchacker_comment_datatype = Unicode(source='metadata', multiple=True,
                            parameters_schema={'date': DateTime,
                            'author': String,
                            'attachment': String,
                            'amount': Integer})


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



class TchackerCommentsView(CommentsView):

    template = '/ui/tchacker/comments.xml'

    def get_namespace(self, resource, context):
        root = context.root

        comments = resource.metadata.get_property('comment') or []
        attachments = resource.metadata.get_property('attachment') or []
        #amount = resource.metadata.get_property('amount').value
        #print("comments = %s" % len(comments))
        #print("amount = %s" % amount)
        joined = [False]*len(comments)
        for att in attachments:
            pos = att.get_parameter('related')-1
            joined[pos] = att.value
        print("joined = %s" % joined)
        links = [
            {'link': x.value,
             'thumbnail': 
                resource.get_resource(x.value, soft=True).get_property('thumbnail')
             #  x.get_parameter('thumbnail') 
             #'width': width or False,
             #'height' height or False
            }
            for i, x in enumerate(attachments) ]
        print("links = %s" % links)
        # Get resource metadata values: is_video, is_image
        comments = [
            {'number': i,
             'user': root.get_user_title(x.get_parameter('author')),
             'datetime': context.format_datetime(x.get_parameter('date')),
             'comment': has_comment(x.value),
             #'attachment': x.get_parameter('attachment')
             'attachment': {
                 'link': joined[i] or False,
                 'is_video': False
                 }
             }
            for i, x in enumerate(comments) ]
        comments.reverse()
        return {'comments': comments}

    def get_comments_amount(self, resource):
        amount = resource.metadata.get_property('amount') or 0
        return amount
