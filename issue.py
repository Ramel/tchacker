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
from os.path import basename
from tempfile import mkdtemp
from os import sep, path
from sys import exc_info
from base64 import b64encode

# Import from itools
from itools.gettext import MSG
from itools.handlers import checkid
from itools.fs import FileName, vfs, lfs
from itools.core import merge_dicts
from itools.csv import Property
from itools.datatypes import Integer, String, Unicode
from itools.core import get_abspath
from itools.web import get_context

# Import from ikaaro
from ikaaro.tracker.issue import Issue
from ikaaro.utils import generate_name
from ikaaro.registry import get_resource_class
from ikaaro.tracker.issue_views import IssueTrackerMenu

# Import from videoencoding
from videoencoding import VideoEncodingToFLV

# Import from PIL
from PIL import Image as PILImage

# Import from Tchacker
from comments import tchacker_comment_datatype
from monkey import Image, Video
from issue_views import Tchack_Issue_Edit_ProxyView

import re
from StringIO import StringIO

class Tchack_Issue(Issue):

    class_id = 'tchack_issue'
    class_version = '20130427'
    class_title = MSG(u'Tchacker Issue')
    class_description = MSG(u'Tchacker Issue')

    # Views
    edit = Tchack_Issue_Edit_ProxyView()

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

            thumbnail = True
            try:
                originalImage = self.get_resource(last_attachment + "_MED")
            except LookupError:
                thumbnail = False
            except:
                thumbnail = False
                print "Unexpected error:", exc_info()[0]
                raise

            if thumbnail:
                fileabspath = fs.get_absolute_path(originalImage.handler.key)
                #print("fileabspath = %s" % fileabspath)
                originalImage = PILImage.open(str(fileabspath))
            else:
                resource = self.get_resource(last_attachment)
                handler = resource.handler #get_value('data')
                data, format = handler.get_thumbnail(800, 800)
                file_like = StringIO(data)
                originalImage = PILImage.open(file_like)
                file_like.close()
            # paste the tmp onto tmp2
            originalImage.paste(alphaImage, (0, 0), alphaImage)
            alphaImage.close()
            # retrieve the result body
            # Save it in memory
            f = StringIO()
            originalImage.save(f, "PNG")
            body = f.getvalue()
            mimetype = "image/png"
            filename = "online-drawing.png"
            canvasSketch = True
            f.close()

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
                if extension != "psd":
                    # For speed, we need to add _LOW, _MED, _HIG resources, in the DB
                    # used instead of a ;thumb
                    has_thumb = Property(False)
                    tchackerImage.set_property('has_thumb', has_thumb)
                    need_thumb = Property(True)
                    tchackerImage.set_property('need_thumb', need_thumb)
                else:
                    pass

            # Video
            elif (mtype == "video"):
                context = get_context()
                server = context.server
                ffmpeg_encoding_folder = lfs.resolve2(server.target, 'ffmpeg-encoding')
                #ffmpeg_encoding_folder = '../ffmpeg-encoding'
                #print("ffmpeg_encoding_folder = %s" % ffmpeg_encoding_folder)
                if not lfs.exists(ffmpeg_encoding_folder):
                    lfs.make_folder(ffmpeg_encoding_folder)
                dirname = mkdtemp('encoding', 'tchacker',
                                    dir=ffmpeg_encoding_folder)
                # Paste the file in the tempdir
                tmpfolder = "%s" % (dirname)
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
                # Add the files for waiting ffmpeg encoding
                f = open(get_abspath('./ffmpeg-encoding/loading-animation.mp4'), 'r')
                data = f.read()
                f.close()
                self.make_resource(name, Video, body=data,
                                extension='mp4', filename='%s.mp4' % name,
                                format='video/mp4')

                vid = self.get_resource(name)
                metadata = vid.metadata

                width_low = Property(640)
                metadata.set_property('width', width_low)
                height_low = Property(480)
                metadata.set_property('height', height_low)
                ratio = Property(1.)
                metadata.set_property('ratio', ratio)
                is_video = Property(True)
                metadata.set_property('is_video', is_video)
                has_thumb = Property(True)
                metadata.set_property('has_thumb', has_thumb)
                encoded = Property(False)
                metadata.set_property('encoded', encoded)
                #print("dirname = %s" % path.basename(path.basename(tmpfolder)))
                tmp_folder= Property(path.basename(path.basename(dirname)))
                metadata.set_property('tmp_folder', tmp_folder)

                # A "Waiting for encoding" image
                f = open(get_abspath('./ffmpeg-encoding/loading-animation_thumb.png'), 'r')
                data = f.read()
                f.close()
                self.make_resource('%s_thumb' % name, Image, body=data,
                                extension='png',
                                filename='%s_thumb.png' % name,
                                format='image/png')
                is_thumb = Property(True)
                self.get_resource('%s_thumb' % name).metadata.set_property(
                    'is_thumb', is_thumb)

                att_name = name

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
            message = MSG(u'Attachment: {filename}')
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
        # Thrown cron to do the thumnails
        server = context.server
        server.run_cron()


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

    def update_20100506(self):
        from itools.core import fixed_offset
        utc = fixed_offset(0)
        from ikaaro.tracker.obsolete import History

        metadata = self.metadata
        history = self.handler.get_handler('.history', History)

        record = history.records[-1]
        # Title
        lang = self.get_site_root().get_default_language()
        title = history.get_record_value(record, 'title')
        title = Property(title, lang=lang)
        metadata.set_property('title', title)
        # Product, module, etc.
        names = 'product', 'module', 'version', 'type', 'state', 'priority'
        for name in names:
            value = history.get_record_value(record, name)
            if value is not None:
                metadata.set_property(name, value)
        # Assigned
        value = history.get_record_value(record, 'assigned_to')
        if value:
            metadata.set_property('assigned_to', value)
        else:
            author = history.get_record_value(record, 'username')
            metadata.set_property('assigned_to', author)

        # We start at zero, so set id to:
        id = -1
        issue_comments = len(history.records)

        for record in history.records:
            if record is None:
                # deleted record
                continue
            comment = history.get_record_value(record, 'comment')
            date = history.get_record_value(record, 'datetime')
            date = date.replace(tzinfo=utc)
            author = history.get_record_value(record, 'username')
            file = history.get_record_value(record, 'file')
            attfile = self.get_resource(file)

            ##############
            # Images
            ##############
            if isinstance(attfile, Image):
                # Get extension
                filename = attfile.get_property('filename')
                name, extension, language = FileName.decode(filename)
                if extension == 'psd':
                    pass
                else:
                    thumbs = [["_LOW", False], ["_MED", False], ["_HIG", False]]
                    for thumb in thumbs:
                        try:
                            thumb[0] = self.get_resource('%s%s' % (file, thumb[0]))
                            thumb[1] = True
                        except LookupError:
                            print("LookupError, need to create thumnails for '%s'" % file)
                            thumb[1] = False

                    if ((not thumbs[0][1]) and (not thumbs[1][1]) and
                                            (not thumbs[2][1])):
                        dirname = mkdtemp('makethumbs', 'ikaaro')
                        tempdir = vfs.open(dirname)
                        # Paste the file in the tempdir
                        tmpfolder = "%s" % (dirname)
                        tmp_uri = ("%s%s%s" % (tmpfolder, sep, name))
                        tmpfile = open("%s" % tmp_uri, "w+")
                        tmpfile.write(attfile.handler.to_str())
                        tmpfile.close()

                        low = 256, 256
                        med = 800, 800
                        hig = 1024, 1024

                        # Create the thumbnail PNG resources
                        thumbext = (["_HIG", hig], ["_MED", med], ["_LOW", low])

                        uri = tmpfolder + sep

                        for te in thumbext:
                            try:
                                im = PILImage.open(tmp_uri)
                            except IOError:
                                print("IOError at PILImage.open(%s)" % tmp_uri)
                            im.thumbnail(te[1], PILImage.ANTIALIAS)
                            # Need to put the name in lowercase
                            ima = name.lower() + te[0]
                            # Some images are in CMYB, force RVB if needed
                            if im.mode != "RGB":
                                im = im.convert("RGB")
                            im.save(uri + ima + ".jpg", 'jpeg', quality=85)
                            # Copy the thumb content
                            thumb_file = tempdir.open(ima + ".jpg")
                            try:
                                thumb_data = thumb_file.read()
                            finally:
                                thumb_file.close()
                            format = 'image/jpeg'
                            cls = get_resource_class(format)
                            print("Creating %s" % ima)
                            imageThumb = self.make_resource(
                                        ima,
                                        cls,
                                        body=thumb_data,
                                        filename=ima+'.jpg',
                                        extension='jpg',
                                        format=format
                                        )
                            is_thumb = Property(True)
                            imageThumb.set_property('is_thumb', is_thumb)

                        has_thumb = Property(True)
                        attfile.set_property('has_thumb', has_thumb)

                        thumbs[0][1] = True
                        thumbs[1][1] = True
                        thumbs[2][1] = True
                        # Clean the temporary folder
                        vfs.remove(dirname)
                    else:
                        print("Update existing Image's Properties: %s" % attfile.name)
                        attfile.set_property('has_thumb', True)
                        attfile.del_property('thumbnail')
                        self.get_resource('%s_LOW' % file).set_property(
                                                                'is_thumb', True)
                        self.get_resource('%s_MED' % file).set_property(
                                                                'is_thumb', True)
                        self.get_resource('%s_HIG' % file).set_property(
                                                                'is_thumb', True)

            ##############
            # Video
            ##############
            thumb = False
            low_thumb = False
            if isinstance(attfile, Video):
                try :
                    self.get_resource('%s_thumb' % file)
                    thumb = True
                except LookupError:
                    thumb = False
                try :
                    self.get_resource('%s_low_thumb' % file)
                    low_thumb = True
                except LookupError:
                    low_thumb = False

                print("Update Video: %s" % attfile.name)
                self.get_resource(file).del_property('thumbnail')
                self.get_resource(file).set_property('has_thumb', True)
                if thumb:
                    self.get_resource('%s_thumb' % file).set_property('is_thumb', True)
                if low_thumb:
                    resource = self.get_resource('%s_low_thumb' % file, soft=True)
                    handler = resource.get_handler()
                    folder = self.handler
                    filename = resource.get_property('filename')
                    handler_name = basename(handler.key)
                    resource.set_property("filename",
                            filename.replace('_low', ''))
                    print("Need to rename the _low_thumb in _thumb")
                    # Copy the handler, we delete it after
                    folder.copy_handler(handler_name,
                            handler_name.replace('_low', ''))
                    folder.copy_handler('%s.metadata' % filename,
                            '%s.metadata' % filename.replace('_low', ''))
                    # Delete old 'thumb_x' file
                    try:
                        self.get_resource('thumb_%s' % file)
                        self.del_resource('thumb_%s' % file)
                    except LookupError:
                        print("The file 'thumb_%s' doesn't exist" % file)

                    # Now delete the old 'x_low_thumb' file copied before
                    try:
                        filename = '%s_low_thumb' % file
                        if self.get_resource(filename):
                            print("Delete old '%s.metadata'" % filename)
                            self.del_resource(filename)
                    except LookupError:
                        print("File '%s.metadata' doesn't exist!" % filename)

            # Add comment only if it was a comment
            # or a comment AND a file.
            if comment:
                id = id + 1
                comment = Property(comment, date=date, author=author)
            if comment == '' and file:
                id = id + 1
                comment = 'comment_is_empty_but_has_attachment'
                comment = Property(comment, date=date, author=author)
            if not comment and issue_comments == 1:
                id = id + 1
                comment = 'empty'
                comment = Property(comment, date=date, author=author)

            metadata.set_property('comment', comment)
            if file:
                attachment = Property(file, comment=id)
                metadata.set_property('attachment', attachment)
                if isinstance(attfile, Image) or isinstance(attfile, Video):
                    if low_thumb:
                        last_attachment = file.replace('_low', '')
                    else:
                        last_attachment = file
                    metadata.set_property('last_attachment', last_attachment)

        # Set the total of ids in the issue, count only comments with text or
        # image/video, doesn't need to increment 'ids' if the modification
        # is everything else.
        metadata.set_property('ids', id)

        # CC
        reporter = history.records[0].username
        value = history.get_record_value(record, 'cc_list')
        if reporter not in value:
            value = value + (reporter,)
        metadata.set_property('cc_list', value)

        # Remove .history
        self.handler.del_handler('.history')
