# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2007-2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
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

# Import from the Standard Library
from datetime import datetime
from tempfile import mkdtemp
import os

# Import from itools
from itools.datatypes import String
from itools.gettext import MSG
from itools.handlers import checkid
from itools.fs import FileName, vfs
from itools.datatypes import Unicode

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.registry import register_field
from ikaaro.tracker.issue import Issue, History
from ikaaro.file import Image, Video
from ikaaro.utils import generate_name
from ikaaro.registry import get_resource_class

# Import from Tchacker
from issue_views import TchackIssue_Edit

# Import from videoencoding
from videoencoding import VideoEncodingToFLV

from pprint import pprint

class Tchack_Issue(Issue):

    class_id = 'tchack_issue'
    class_version = '20071216'
    class_title = MSG(u'Tchack Issue')
    class_description = MSG(u'Tchack Issue')

    # Views
    edit = TchackIssue_Edit()

    def _get_catalog_values(self):
        values = Issue._get_catalog_values(self)
        history = self.get_history()
        # Get the last record
        record = history.get_record(-1)
        if record:
            values['issue_last_author'] = history.get_record_value(record, 'username')
        # Get last attachment
        values['issue_last_attachment'] = None
        for record in self.get_history_records():
            if record.file:
                values['issue_last_attachment'] = record.file
        return values
    
    def _add_record(self, context, form):
        user = context.user
        root = context.root
        parent = self.parent
        users = root.get_resource('users')

        record = {}
        # Datetime
        record['datetime'] = datetime.now()
        # User XXX
        if user is None:
            record['username'] = ''
        else:
            record['username'] = user.name
        # Title
        title = context.get_form_value('title', type=Unicode).strip()
        record['title'] = title
        # Version, Priority, etc.
        for name in ['product', 'module', 'version', 'type', 'state',
                     'priority', 'assigned_to', 'comment']:
            type = History.record_properties[name]
            value = context.get_form_value(name, type=type)
            if type == Unicode:
                value = value.strip()
            record[name] = value
        # CCs
        cc_list = set(self.get_value('cc_list') or ())
        cc_remove = context.get_form_value('cc_remove')
        datatype = String(multiple=True)
        if cc_remove:
            cc_remove = context.get_form_value('cc_list', type=datatype)
            cc_list = cc_list.difference(cc_remove)
        cc_add = context.get_form_value('cc_add', type=datatype)
        if cc_add:
            cc_list = cc_list.union(cc_add)
        record['cc_list'] = list(cc_list)

        # Files XXX
        file = context.get_form_value('file')
        if file is None:
            record['file'] = ''
        else:
            # Upload
            filename, mimetype, body = form['file']
            # Find a non used name
            name = checkid(filename)
            name, extension, language = FileName.decode(name)
            name = generate_name(name, self.get_names())
            # Add attachement
            cls = get_resource_class(mimetype)
            cls.make_resource(cls, self, name, body=body, filename=filename,
                            extension=extension, format=mimetype)
            pprint("name = %s" % name)
            # Video
            file = self.get_resource(name)
            #cls.save_changes()
            #self.init_resource(**kw)
            pprint("file = %s" % file)
            if isinstance(file, Video):
                pprint("That's a Video file")
                if extension is None:
                    mimetype = file.get_content_type()
                    extension = guess_extension(mimetype)[1:]
                if (extension == "mp4"):
                    pprint("I got an \"%s\" file" % extension)
                    thumbnail = ("thumb_%s" % name)
                    if vfs.exists(thumbnail):
                        pprint("thumbnail.handler.key = %s"
                            % thumbnail.handler.key)
                    else:
                        pprint("No thumbnail, We need to create a thumb, let's go...")
                        dirname = mkdtemp('videoencoding', 'ikaaro')
                        tempdir = vfs.open(dirname)
                        # Paste the file in the tempdir
                        tmp_uri= "/%s" % (dirname)
                        
                        base = file.handler.key
                        pprint("base = %s" % base)
                        root_path = file.handler.database.path
                        pprint("root_path = %s" % root_path)
                        #vfs.copy(file.handler.database.path+base, tmp_uri+os.sep+filename)
                        #vfs.copy(root_path+base, tmp_uri)
                        tmpfile = open("/%s/%s" % (tmp_uri, name), "w+")
                        tmpfile.write(body)
                        tmpfile.close()
                        # Thumbnail
                        thumbnailed = VideoEncodingToFLV(file).make_thumbnail_only(
                            tmp_uri, name, name, 512)
                        #pprint("thumbnail = %s" % thumbnail)
                        
                        if thumbnailed is not None:
                            thumbfilename, thumbmimetype, thumbbody, thumbextension = thumbnailed['flvthumb']
                            
                            # Create the thumbnail PNG resources
                            thumb = Image #get_resource_class(thumbmimetype)
                            #pprint("get_resource_class(thumbmimetype) = %s" % thumb)
                            issue = context.resource
                            #pprint("issue.handler.key = %s" % issue.handler.key)
                            #pprint("thumbfilename= %s" % thumbfilename)
                            #pprint("thumbmimetype= %s" % thumbmimetype)
                            #pprint("thumbextension= %s" % thumbextension)
                            #pprint(thumb.make_resource.__class__.__name__)
                            thumb.make_resource(thumb, issue, thumbfilename,
                                body=thumbbody, filename=thumbfilename,
                                extension=thumbextension, format=thumbmimetype)
                        else:
                            pprint("Thumbnailed is None")

                        # Clean the temporary folder
                        #vfs.remove(dirname)
            # Link
            record['file'] = name
        # Update
        modifications = self.get_diff_with(record, context)
        history = self.get_history()
        history.add_record(record)
        # Send a Notification Email
        # Notify / From
        if user is None:
            user_title = MSG(u'ANONYMOUS')
        else:
            user_title = user.get_title()
        # Notify / To
        to_addrs = set()
        reported_by = self.get_reported_by()
        if reported_by:
            to_addrs.add(reported_by)
        for cc in cc_list:
            to_addrs.add(cc)
        assigned_to = self.get_value('assigned_to')
        if assigned_to:
            to_addrs.add(assigned_to)
        if user.name in to_addrs:
            to_addrs.remove(user.name)
        # Notify / Subject
        tracker_title = self.parent.get_property('title') or 'Tracker Issue'
        subject = '[%s #%s] %s' % (tracker_title, self.name, title)
        # Notify / Body
        if isinstance(context.resource, self.__class__):
            uri = context.uri.resolve(';edit')
        else:
            uri = context.uri.resolve('%s/;edit' % self.name)

        message = MSG(u'DO NOT REPLY TO THIS EMAIL. To comment on this '
                u'issue, please visit:\n{issue_uri}')
        body = message.gettext(issue_uri=uri)
        body += '\n\n'
        body += '#%s %s\n\n' % (self.name, self.get_value('title'))
        message = MSG(u'The user {title} did some changes.')
        body +=  message.gettext(title=user_title)
        body += '\n\n'
        if file:
            filename = unicode(filename, 'utf-8')
            message = MSG(u'New Attachment: {filename}')
            message = message.gettext(filename=filename)
            body += message + '\n'
        comment = context.get_form_value('comment', type=Unicode)
        if modifications:
            body += modifications
            body += '\n\n'
        if comment:
            title = MSG(u'Comment').gettext()
            separator = len(title) * u'-'
            template = u'{title}\n{separator}\n\n{comment}\n'
            body += template.format(title=title, separator=separator,
                                    comment=comment)
        # Notify / Send
        for to_addr in to_addrs:
            user = root.get_user(to_addr)
            if not user:
                continue
            to_addr = user.get_property('email')
            root.send_email(to_addr, subject, text=body)


###########################################################################
# Register
###########################################################################
# The class
register_resource_class(Tchack_Issue)
register_field('issue_last_attachment', String(is_stored=True))
register_field('issue_last_author', String(is_stored=True))

