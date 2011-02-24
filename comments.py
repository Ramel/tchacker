# -*- coding: UTF-8 -*-
# Copyright (C) 2010 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
from itools.datatypes import Unicode, String, DateTime, Boolean

# Import from ikaaro
from ikaaro.comments import CommentsView, indent


tchacker_comment_datatype = Unicode(source='metadata', multiple=True,
                            parameters_schema={'date': DateTime,
                            'author': String,
                            'attachment': String,
                            'att_is_img': Boolean,
                            'att_is_vid': Boolean})


def attachment(att):
    if (att == "att_is_file") | (att == "att_is_img") | (att == "att_is_vid"):
        value = None
    else:
        value = indent(att)
    return value



class TchackerCommentsView(CommentsView):

    template = '/ui/tchacker/comments.xml'

    def get_namespace(self, resource, context):
        root = context.root

        comments = resource.metadata.get_property('comment') or []
        #print("comments 1 = %s" % comments)
        comments = [
            {'number': i,
             'user': root.get_user_title(x.get_parameter('author')),
             'datetime': context.format_datetime(x.get_parameter('date')),
             'comment': attachment(x.value),
             #'comment': indent(x.value),
             'attachment': x.get_parameter('attachment'),
             'att_is_img': x.get_parameter('att_is_img'),
             'att_is_vid': x.get_parameter('att_is_vid')}
            for i, x in enumerate(comments) ]
        comments.reverse()
        #print("comments 2 = %s" % comments)
        return {'comments': comments} 