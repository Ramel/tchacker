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
from tempfile import mkdtemp
from os import sep

# Import from itools
from itools.gettext import MSG
from itools.handlers import checkid
from itools.fs import FileName, vfs
from itools.core import merge_dicts
from itools.csv import Property
from itools.datatypes import Integer, String, Unicode

# Import from ikaaro
from ikaaro.tracker.issue import Issue
from ikaaro.utils import generate_name
from ikaaro.registry import get_resource_class
from ikaaro.tracker.issue_views import IssueTrackerMenu

# Import from Tchacker
from issue_views import TchackIssue_Edit

# Import from videoencoding
from videoencoding import VideoEncodingToFLV

# Import from PIL
from PIL import Image as PILImage

import re
from StringIO import StringIO

from comments import tchacker_comment_datatype
from monkey import Image, Video



class Tchack_Issue(Issue):

    class_id = 'tchack_issue'
    class_version = '20130427'
    class_title = MSG(u'Tchacker Issue')
    class_description = MSG(u'Tchacker Issue')

    # Views
    edit = TchackIssue_Edit()

    class_schema = merge_dicts(
        Issue.class_schema,
        last_attachment=String(source='metadata', indexed=False, stored=True))

    #XXX: Replace the original datatypes
    class_schema['comment'] = tchacker_comment_datatype
    # Add a relation to comment in the attachment schema
    class_schema['attachment'] = Unicode(
                        source='metadata',
                        multiple=True,
                        parameters_schema={
                            'attachment': String,
                            'comment': Integer})

    def get_catalog_values(self):
        document = Issue.get_catalog_values(self)
        return document


    def get_comments(self):
        comments = self.metadata.get_property('comment')
        if not comments:
            return None
        return [ ("%s" % x.value) for x in comments ]


    def get_len_comments(self):
        comments = self.metadata.get_property('comment')
        if not comments:
            return None
        return len(comments)


    def get_attachments(self):
        attachments = self.metadata.get_property('attachment')
        if not attachments:
            return None
        return set([ str(x.value) for x in attachments ])


    def get_attachments_ordered(self):
        attachments = self.metadata.get_property('attachment')
        if not attachments:
            return []
        #return dict([ (x.get_parameter('comment'), str(x.value)) for x in attachments])
        return [ str(x.value) for x in attachments]


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

        comment = form['comment']
        # Attachment
        attachment = form['attachment']
        if new:
            drawing = ""
            #last_attachment = None
        else:
            drawing = form['canvasDrawing']

        emptyDrawing = False
        #print("attachment = '%s', drawing = '%s'" % (attachment, drawing))
        # Test if drawing is an empty String
        if not drawing:
            emptyDrawing = True

        if new:
            ids = 0
        else:
            ids = self.get_len_comments()

        att_name = ""

        canvasSketch = False

        if not emptyDrawing:
            body = re.search(r'base64,(.*)', drawing).group(1)
            body = body.decode('base64')
            # body is only the canvas sketch,
            # we need to add the original image to it
            # So, create a tmp image that contains body
            alphaImage = PILImage.open(StringIO(body))
            # transform the tmp image black color to alpha
            alphaImage = alphaImage.convert("RGBA")
            # create a tmp2 image that contains the last attachment
            last_attachment = self.get_property('last_attachment')
            #print("last_attachment = %s" % last_attachment)

            fs = self.metadata.database.fs
            originalImage = self.get_resource(last_attachment + "_MED")
            fileabspath = fs.get_absolute_path(originalImage.handler.key)
            #print("fileabspath = %s" % fileabspath)

            originalImage = PILImage.open(str(fileabspath))
            # paste the tmp onto tmp2
            originalImage.paste(alphaImage, (0, 0), alphaImage)
            # retrieve the result body
            # Save it in memory
            f = StringIO()
            originalImage.save(f, "PNG")
            body = f.getvalue()
            mimetype = "image/png"
            filename = "online-drawing.png"
            canvasSketch = True

        if attachment is not None or emptyDrawing is False:
            if canvasSketch is False:
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
                # Create the image in the database
                tchackerImage = self.make_resource(
                                name, Image,
                                body=body,
                                filename=filename,
                                extension=extension,
                                format=mimetype
                                )
                # For speed, we need to add _LOW, _MED, _HIG resources, in the DB
                # used instead of a ;thumb
                has_thumb = Property(False)
                tchackerImage.set_property('has_thumb', has_thumb)
                need_thumb = Property(True)
                tchackerImage.set_property('need_thumb', need_thumb)

                if extension == "psd":
                    pass
            # Video
            elif (mtype == "video"):
                # Copy the uploaded video in the TMP folder for later encoding
                # Then copy a Fake/Waiting video in the issue metadata
                # "wait_ffmpeg_encoding.mp4"
                # Also copy the thumb file:
                # "wait_ffmpeg_encoding_thumb.png"
                # Then the cron job will encode it later

                wait_video = self.make_resource()
                # Create the thumbnail PNG resources
                # A copy of the file in the database
                wait_video_thumbnail = self.make_resource(
                                thumbfilename,
                                Image,
                                body=thumbbody,
                                filename=thumbfilename,
                                extension=thumbextension,
                                format=thumbmimetype)
                is_thumb = Property(True)
                wait_video_thumbnail.set_property('is_thumb', is_thumb)




                # Make Thumbnail for it, and encode it
                # in a Low version (319px width)
                # First, upload it, then encode it, and make a thumb for the
                # encoded file.
                # video.mp4, video_low.mp4, video_low_thumb.jpg
                # If the video is h264 and wider than 319px,
                # so create a Low copy.
                dirname = mkdtemp('videoencoding', 'ikaaro')
                tempdir = vfs.open(dirname)
                # Paste the file in the tempdir
                tmpfolder = "%s" % (dirname)
                #root_path = file.handler.database.path
                tmp_uri = ("%s%s%s" % (tmpfolder, sep, name))
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
                #if int(width) > 319:
                #video_low = ("%s_low" % name)
                # video is already in temp dir, so encode it
                encoded = VideoEncodingToFLV(tmpfile).encode_video_to_mp4(
                    tmpfolder, name, name, width_low, encode='one_chroma_faststart')

                if encoded is not None:
                    vidfilename, vidmimetype, vidbody, vidextension, \
                            width, height = encoded['videoFile']
                    thumbfilename, thumbmimetype, \
                            thumbbody, thumbextension = encoded['videoThumb']
                    # Create the video resources
                    self.make_resource(vidfilename, Video,
                        body=vidbody, filename=vidfilename,
                        extension=vidextension, format=vidmimetype)

                    #height_low = int(round(float(width_low) / ratio))

                    vid = self.get_resource(vidfilename)
                    metadata = vid.metadata

                    # Get sizes from encoded['flvfile'] instead of *_low
                    # width_low = width now, sure!
                    width_low = Property(width)
                    metadata.set_property('width', width_low)
                    height_low = Property(height)
                    metadata.set_property('height', height_low)
                    ratio = Property(ratio)
                    metadata.set_property('ratio', ratio)
                    has_thumb = Property(True)
                    metadata.set_property('has_thumb', has_thumb)

                    # Create the thumbnail PNG resources
                    self.make_resource(thumbfilename, Image,
                        body=thumbbody, filename=thumbfilename,
                        extension=thumbextension, format=thumbmimetype)
                    is_thumb = Property(True)
                    self.get_resource(thumbfilename).metadata.set_property(
                        'is_thumb', is_thumb)
                    # As the video is a low version and reencoded
                    att_name = vidfilename

                # Clean the temporary folder
                vfs.remove(dirname)

            # Default case
            else:
                cls = get_resource_class(mimetype)
                self.make_resource(name, cls, body=body, filename=filename,
                extension=extension, format=mimetype)

            # Link
            # The "ids" in comments is ids-1
            attachment = Property(att_name, comment=ids)
            self.set_property('attachment', attachment)

        # Comment
        date = context.timestamp
        user = context.user
        author = user.name if user else None
        # Check for empty comment
        comment_check = " ".join(comment.split())
        if comment_check == '' and attachment is not None:
            comment = "comment_is_empty_but_has_attachment"
        if attachment is not None:
            self.set_property('last_attachment', att_name)

        comment = Property(comment, date=date, author=author)

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
        tracker_title = self.parent.get_property('title') or u'Tracker Issue'
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
        #body += '%s\n\n' % module
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


    #######################################################################
    # User Interface
    #######################################################################
    def get_context_menus(self):
        return [IssueTrackerMenu()] + self.parent.get_context_menus()


    #######################################################################
    # Update
    #######################################################################
    def update_20130427(self):
        """Delete the ids property"""
        metadata = self.metadata
        metadata.del_property('ids')


    def update_20100507(self):
        """Fake update to pass the inherited method"""
        print "Fake update"

