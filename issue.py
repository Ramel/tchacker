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

from comments import tchacker_comment_datatype
from monkey import Image, Video



class Tchack_Issue(Issue):

    class_id = 'tchack_issue'
    class_version = '20100506'
    class_title = MSG(u'Tchacker Issue')
    class_description = MSG(u'Tchacker Issue')

    # Views
    edit = TchackIssue_Edit()

    class_schema = merge_dicts(
        Issue.class_schema,
        ids=Integer(source='metadata'),
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


    def get_attachments(self):
        attachments = self.metadata.get_property('attachment')
        if not attachments:
            return None

        base = self.get_canonical_path()
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
        ids = 1
        if not new:
            if ((not(comment) and attachment) or
                        (comment and not(attachment)) or
                        (comment and attachment)):
                ids = int(self.get_property('ids')) + 1
            else:
                ids = int(self.get_property('ids'))

        att_name = ""

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
                # Add attachment
                tchackerImage = self.make_resource(
                                name, Image,
                                body=body,
                                filename=filename,
                                extension=extension,
                                format=mimetype
                                )
                # For speed, we need to add _LOW, _MED, _HIG resources, in the DB
                # used instead of a ;thumb
                if extension == "psd":
                    pass
                else:
                    dirname = mkdtemp('makethumbs', 'ikaaro')
                    tempdir = vfs.open(dirname)
                    # Paste the file in the tempdir
                    tmpfolder = "%s" % (dirname)
                    tmp_uri = ("%s%s%s" % (tmpfolder, sep, name))
                    tmpfile = open("%s" % tmp_uri, "w+")
                    tmpfile.write(body)
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
                            print("IOError = %s" % tmp_uri)
                        im.thumbnail(te[1], PILImage.ANTIALIAS)
                        ima = name + te[0]
                        # Some images are in CMYB, force RVB if needed
                        if im.mode != "RGB":
                            im = im.convert("RGB")
                        im.save(uri + ima + ".jpg", 'jpeg', quality=85)
                        # Copy the thumb content
                        thumb_filename = ima + ".jpg"
                        # Copy the thumb content
                        thumb_file = tempdir.open(thumb_filename)
                        try:
                            thumb_data = thumb_file.read()
                        finally:
                            thumb_file.close()
                        format = 'image/jpeg'
                        cls = get_resource_class(format)
                        imageThumb = self.make_resource(
                                    ima, cls,
                                    body=thumb_data,
                                    filename=thumb_filename,
                                    extension='jpg',
                                    format=format
                                    )
                        is_thumb = Property(True)
                        imageThumb.set_property('is_thumb', is_thumb)
                    has_thumb = Property(True)
                    tchackerImage.set_property('has_thumb', has_thumb)
                    # Clean the temporary folder
                    vfs.remove(dirname)

            # Video
            elif (mtype == "video"):
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
                encoded = VideoEncodingToFLV(tmpfile).encode_video_to_flv(
                    tmpfolder, name, name, width_low, encode='one_chroma_faststart')

                if encoded is not None:
                    vidfilename, vidmimetype, vidbody, vidextension, \
                            width, height = encoded['flvfile']
                    thumbfilename, thumbmimetype, \
                            thumbbody, thumbextension = encoded['flvthumb']
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
            attachment = Property(att_name, comment=ids-1)
            self.set_property('attachment', attachment)

        # Comment
        date = context.timestamp
        user = context.user
        author = user.name if user else None
        if comment == '' and attachment is not None:
            comment = "comment_is_empty_but_has_attachment"
        if attachment is not None:
            self.set_property('last_attachment', att_name)
        comment = Property(comment, date=date,
                            author=author
                            )
        self.set_property('comment', comment)
        #ids = int(self.get_property('ids'))
        #ids = Property(ids)
        #print ids
        #ids = self.get_property(ids)
        self.set_property('ids', ids)

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
