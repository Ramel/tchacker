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
#from itools.datatypes import Unicode
from itools.core import merge_dicts
from itools.database import register_field
from itools.csv import Property
from itools.datatypes import Integer, String, Unicode, Tokens
from itools.datatypes import Boolean

# Import from ikaaro
from ikaaro.registry import register_resource_class
from ikaaro.tracker.issue import Issue
from ikaaro.tracker.obsolete import History
from ikaaro.file import Video, Image
from ikaaro.utils import generate_name
from ikaaro.registry import get_resource_class
from ikaaro.folder import Folder

# Import from Tchacker
from issue_views import TchackIssue_Edit

# Import from videoencoding
from videoencoding import VideoEncodingToFLV

from PIL import Image as PILImage

from comments import tchacker_comment_datatype



class TchackerImage(Image):

    class_schema = merge_dicts(
        Image.class_schema,
        # Metadata
        thumbnail=Boolean(source='metadata', stored=True))
    """
        width=Integer(source='metadata', stored=True),
        height=Integer(source='metadata', stored=True),
        ratio=Integer(source='metadata', indexed=True, stored=True),
    """


class Tchack_Issue(Issue):

    class_id = 'tchack_issue'
    class_version = '20071216'
    class_title = MSG(u'Tchack Issue')
    class_description = MSG(u'Tchack Issue')

    # Views
    edit = TchackIssue_Edit()

    class_schema = Issue.class_schema
    class_schema['comment'] = tchacker_comment_datatype
    """
    class_schema = merge_dicts(
        Issue.class_schema,
        # Metadata
        comment=tchacker_comment_datatype)
    """
    """
    class_schema = merge_dicts(
        Folder.class_schema,
        # Metadata
        product=Integer(source='metadata', indexed=True, stored=True),
        module=Integer(source='metadata', indexed=True, stored=True),
        version=Integer(source='metadata', indexed=True, stored=True),
        type=Integer(source='metadata', indexed=True, stored=True),
        state=Integer(source='metadata', indexed=True, stored=True),
        priority=Integer(source='metadata', indexed=True, stored=True),
        assigned_to=String(source='metadata', indexed=True, stored=True),
        cc_list=Tokens(source='metadata'),
        comment=tchacker_comment_datatype,
        # Other
        id=Integer(indexed=True, stored=True),
        attachment=String(source='metadata', multiple=True))
    """

    """
    #XXX: Need to update that
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
    """

    def add_comment(self, context, form, new=False):
        # Keep a copy of the current metadata
        old_metadata = self.metadata.clone()
        # Title
        title = form['title'].strip()
        language = self.get_edit_languages(context)[0]
        self.set_property('title', title, language=language)
        # Version, Priority, etc.
        for name in ['product', 'module', 'version', 'type', 'state',
                     'priority', 'assigned_to']:
            value = form[name]
            self.set_property(name, value)
        # CCs
        cc_list = form['cc_list']
        self.set_property('cc_list', tuple(cc_list))

        # Attachment
        attachment = form['attachment']
        
        att_name = "" 
        att_is_img = False
        att_is_vid = False
        
        if attachment is not None:
            # Upload
            filename, mimetype, body = attachment
            # Find a non used name
            name = checkid(filename)
            name, extension, language = FileName.decode(name)
            name = generate_name(name, self.get_names())

            mtype = mimetype.split("/")[0]
            
            att_name = name 
 
            # Image
            if (mtype == "image"):
                att_is_img = True 
                # Add attachment
                cls = get_resource_class(mimetype)
                #self.make_resource(name, cls, body=body, filename=filename,
                self.make_resource(name, TchackerImage, body=body, filename=filename,
                                extension=extension, format=mimetype)
                file = self.get_resource(name)

                # For speed, we need to add _LOW, _MED, _HIG resources, in the DB
                # used instead of a ;thumb
                if extension == "psd":
                    pass
                else:
                    name = file.name
                    mimetype = file.handler.get_mimetype()
                    body = file.handler.to_str()

                    dirname = mkdtemp('makethumbs', 'ikaaro')
                    tempdir = vfs.open(dirname)
                    # Paste the file in the tempdir
                    tmpfolder = "%s" % (dirname)
                    tmp_uri = ("%s%s%s" % (tmpfolder, os.sep, name))
                    tmpfile = open("%s" % tmp_uri, "w+")
                    tmpfile.write(body)
                    tmpfile.close()

                    low = 256, 256
                    med = 800, 800
                    hig = 1024, 1024

                    # Create the thumbnail PNG resources
                    cls = get_resource_class('image/jpeg')
                    thumbext = (["_HIG", hig], ["_MED", med], ["_LOW", low])
                    uri = tmpfolder + os.sep
                    ext = "jpeg"
                    for te in thumbext:
                        try:
                            im = PILImage.open(tmp_uri)
                        except IOError:
                            print("IOError = %s" % tmp_uri)
                        im.thumbnail(te[1], PILImage.ANTIALIAS)
                        ima = name + te[0]
                        # Some images are in CMYB, force RVB if needed
                        if im.mode != "RGB":
                            im = im.convert("RGB")
                        im.save(uri + ima + "." + ext, ext, quality=85)
                        # Copy the thumb content
                        thumb_file = tempdir.open(ima + "." + ext)
                        try:
                            thumb_data = thumb_file.read()
                        finally:
                            thumb_file.close()
                        self.make_resource(ima, Image,
                            body=thumb_data, filename=ima,
                            extension=ext, format='image/%s' % ext)
                    thumbnail = Property(True)
                    file.metadata.set_property('thumbnail', thumbnail)
                    # Clean the temporary folder
                    vfs.remove(dirname)
            """
            # Video
            elif (mtype == "video"):
                # Make Thumbnail for it, and encode it
                # in a Low version (319px width)
                # First, upload it, then encode it, and make a thumb for the
                # encoded file.
                # video.mp4, video_low.mp4, video_low_thumb.jpg
                # If the video is h264 and wider than 319px,
                # so create a Low copy.
                att_is_vid = True
                dirname = mkdtemp('videoencoding', 'ikaaro')
                tempdir = vfs.open(dirname)
                # Paste the file in the tempdir
                tmpfolder = "%s" % (dirname)
                #root_path = file.handler.database.path
                tmp_uri = ("%s%s%s" % (tmpfolder, os.sep, name))
                tmpfile = open("%s" % tmp_uri, "w+")
                tmpfile.write(body)
                tmpfile.close()
                # Get size
                dim = VideoEncodingToFLV(tmpfile).get_size_and_ratio(tmp_uri)
                width, height, ratio = dim
                # Codec
                #venc = VideoEncodingToFLV(file).get_video_codec(tmp_uri)
                width_low = 640
                # In case of a video in h264 and widder than 319px
                # We encode it in Flv at 640px width  and make a thumbnail
                #if int(width) > 319 and venc == "h264":
                if int(width) > 319:
                    #video_low = ("%s_low" % name)
                    # video is already in temp dir, so encode it
                    encoded = VideoEncodingToFLV(tmpfile).encode_video_to_flv(
                        tmpfolder, name, name, width_low)

                    if encoded is not None:
                        vidfilename, vidmimetype, \
                                vidbody, vidextension = encoded['flvfile']
                        thumbfilename, thumbmimetype, \
                                thumbbody, thumbextension = encoded['flvthumb']
                        # Create the video resources
                        cls = get_resource_class(vidmimetype)
                        self.make_resource(cls, self, vidfilename,
                            body=vidbody, filename=vidfilename,
                            extension=vidextension, format=vidmimetype)
                        height_low = int(round(float(width_low) / ratio))
                        vid = self.get_resource(vidfilename)
                        vid.metadata.set_property('width', str(width_low))
                        vid.metadata.set_property('height', str(height_low))
                        vid.metadata.set_property('ratio', str(ratio))
                        vid.metadata.set_property('thumbnail', "True")
                        # Create the thumbnail PNG resources
                        cls = get_resource_class(thumbmimetype)
                        self.make_resource(cls, self, thumbfilename,
                            body=thumbbody, filename=thumbfilename,
                            extension=thumbextension, format=thumbmimetype)
            """
            """
                # Create a thumbnail for a big file, instead of encoding it
                else:
                    mkthumb = VideoEncodingToFLV(file).make_thumbnail(
                        tmpfolder, name, width_low)
                    if mkthumb is not None:
                        thumbfilename, thumbmimetype, \
                                thumbbody, thumbextension = mkthumb
                        # Create the thumbnail PNG resources
                        cls = get_resource_class(thumbmimetype)
                        self.make_resource(cls, self, thumbfilename,
                            body=thumbbody, filename=thumbfilename,
                            extension=thumbextension, format=thumbmimetype)
                    file.metadata.set_property('width', width)
                    file.metadata.set_property('height', height)
                    file.metadata.set_property('ratio', str(ratio))
                    file.metadata.set_property('thumbnail', "False")
            """
            """
                # Clean the temporary folder
                vfs.remove(dirname)
            """

            # Link
            attachment = att_name
            self.set_property('attachment', attachment)

        # Comment
        date = context.timestamp
        user = context.user
        author = user.name if user else None
        comment = form['comment']
        if not comment:
            if att_is_img:
                comment = "%s" % att_is_img
            if att_is_vid:
                comment = "%s" % att_is_vid
            else:
                comment = "att_is_file"
        print("comment = %s" % comment)
        #attachment = attname
        comment = Property(comment, date=date, author=author,
            attachment=att_name, att_is_img=att_is_img,
            att_is_vid=att_is_vid)
        self.set_property('comment', comment)

        # Send a Notification Email
        # Notify / From
        if user is None:
            user_title = MSG(u'ANONYMOUS')
        else:
            user_title = user.get_title()
        # Notify / To
        to_addrs = set(cc_list)
        assigned_to = self.get_property('assigned_to')
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
        body += '#%s %s\n\n' % (self.name, self.get_property('title'))
        message = MSG(u'The user {title} did some changes.')
        body +=  message.gettext(title=user_title)
        body += '\n\n'
        if attachment:
            filename = unicode(filename, 'utf-8')
            message = MSG(u'New Attachment: {filename}')
            message = message.gettext(filename=filename)
            body += message + '\n'
        comment = context.get_form_value('comment', type=Unicode)
        modifications = self.get_diff_with(old_metadata, context, new=new)
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
        root = context.root
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
register_resource_class(TchackerImage)
register_field('issue_last_attachment', String(is_stored=True))
register_field('issue_last_author', String(is_stored=True))
