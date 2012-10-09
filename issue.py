# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2007-2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
# Copyright (C) 2009 Armel FORTUN <armel@tchack.com>
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
#from os.path import basename
from tempfile import mkdtemp
from os import sep

# Import from itools
from itools.csv import Property
from itools.datatypes import Unicode
#from itools.datatypes import Integer, String, Unicode, Tokens, URI
from itools.fs import FileName, vfs
from itools.gettext import MSG
from itools.handlers import checkid
from itools.web import get_context
from itools.database import Metadata

# Import from ikaaro
from ikaaro.comments import Comment, CommentsAware
from ikaaro.config_models import Model
from ikaaro.config_models import ModelField_Inherited
from ikaaro.config_models import ModelField_Choices, Choice
from ikaaro.folder import Folder
from ikaaro.database import Database
from ikaaro.utils import generate_name
from ikaaro.fields import Integer_Field, URI_Field
from ikaaro.fields import Text_Field
from ikaaro.cc import Followers_Field

# Import from videoencoding
from videoencoding import VideoEncodingToFLV

# Import from PIL
from PIL import Image as PILImage

# Import from Tchacker
from issue_views import Issue_NewInstance
from issue_views import IssueTchackerMenu, Issue_History
from issue_views import Issue_DownloadAttachments, Issue_Edit
from monkey import Image, Video



class Issue(CommentsAware, Folder):

    class_id = 'issue'
    class_version = '20100506'
    class_title = MSG(u'Issue')
    class_description = None #MSG(u'Adding a new Issue')
    class_views = ['edit', 'edit_resources', 'browse_content', 'history']

    # Views
    new_instance = Issue_NewInstance
    edit = Issue_Edit

    title = Folder.title(title=MSG(u'Subject'),
                            required=True, multilingual=False) 
    # Metadata
    assigned_to = Followers_Field(indexed=True, stored=True,
                                    title=MSG(u'Assigned To'))
    cc_list = Followers_Field(multiple=True,
                                    title=MSG(u'CC List'))
    # Other
    id = Integer_Field(indexed=True, stored=True)
    attachment = URI_Field(multiple=True)
    # Tchacker
    ids = Integer_Field()
    last_attachment = URI_Field(indexed=False, stored=True)
    comment = Text_Field(indexed=False, stored=True, multilingual=False)


    #def get_catalog_values(self):
    #    #document = Folder.get_catalog_values(self)
    #    document = super(Folder, self).get_catalog_values()
    #    print document
    #    document['id'] = int(self.name)
    #    # Override default (FIXME should set default to 'nobody' instead?)
    #    document['assigned_to'] = self.get_value('assigned_to') or 'nobody'
    #    return document


    def get_document_types(self):
        return []


    #######################################################################
    # API
    #######################################################################
    def get_title(self, language=None):
        return u'#%s %s' % (self.name, self.get_value('title'))


    def get_history(self):
        context = get_context()
        database = context.database
        filename = '%s.metadata' % self.get_abspath()
        filename = filename[1:]

        get_blob = database.get_blob_by_revision_and_path

        for commit in database.worktree.git_log(filename, reverse=True):
            sha = commit['sha']
            yield get_blob(sha, filename, Metadata)

    # Tchacker
    def get_comments(self):
        comments = self.metadata.get_value('comment')
        if not comments:
            return None
        #base = self.get_canonical_path()
        return [ ("%s" % x.value) for x in comments ]


    def get_attachments(self):
        attachments = self.metadata.get_value('attachment')
        if not attachments:
            return None

        #base = self.get_canonical_path()
        return set([ str(x.value) for x in attachments ])


    def get_attachments_ordered(self):
        attachments = self.metadata.get_value('attachment')
        if not attachments:
            return []
        #return dict([ (x.get_parameter('comment'), str(x.value)) for x in attachments])
        return [ str(x.value) for x in attachments]


    def add_comment(self, context, form, new=False):
        # Keep a copy of the current metadata
        old_metadata = self.metadata.clone()
        # Title
        language = self.get_edit_languages(context)[0]
        for lang, title in form['title'].items():
            self.set_value('title', title.strip(), language=lang)
        # Version, Priority, etc.
        for name in ['product', 'type', 'state',
                     'priority', 'assigned_to']:
            value = form[name]
            self.set_value(name, value)
        # CCs
        cc_list = form['cc_list']
        self.set_value('cc_list', tuple(cc_list))

        comment = form['comment']

        # Attachment
        attachment = form['attachment']

        ids = 1
        # Check if add (new) or update
        if not new:
            ids = int(self.get_value('ids')) + 1

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
                        cls = Database.get_resource_class(format)
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
                cls = Database.get_resource_class(mimetype)
                self.make_resource(name, cls, body=body, filename=filename,
                extension=extension, format=mimetype)

            # Link
            # The "ids" in comments is ids-1
            attachment = Property(att_name, comment=ids-1)
            self.set_value('attachment', attachment)

        # Comment
        date = context.timestamp
        user = context.user
        author = user.name if user else None
        if comment == '' and attachment is not None:
            comment = "comment_is_empty_but_has_attachment"
        if attachment is not None:
            self.set_value('last_attachment', att_name)
        comment = Property(comment, date=date, author=author)
        #new_comment = self.make_resource(None, Comment)
        #new_comment.set_value('description', comment, language=language)
        self.set_value('comment', comment)
        #ids = int(self.get_value('ids'))
        self.set_property('ids', ids)

        # Send a Notification Email
        # Notify / From
        if user is None:
            user_title = MSG(u'ANONYMOUS')
        else:
            user_title = user.get_title()
        # Notify / To
        to_addrs = set(cc_list)
        assigned_to = self.get_value('assigned_to')
        if assigned_to:
            to_addrs.add(assigned_to)
        if user.name in to_addrs:
            to_addrs.remove(user.name)
        # Notify / Subject
        tchacker_title = self.parent.get_value('title') or u'Tchacker Issue'
        subject = '[%s #%s] %s' % (tchacker_title, self.name, title)
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
        if attachment:
            filename = unicode(filename, 'utf-8')
            message = MSG(u'New Attachment: {filename}')
            message = message.gettext(filename=filename)
            body += message + '\n'
        comment = context.get_form_value('comment', type=Unicode)
        #modifications = self.get_diff_with(old_metadata, context, new=new)
        #if modifications:
        #    body += modifications
        #    body += '\n\n'
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
            to_addr = user.get_value('email')
            root.send_email(to_addr, subject, text=body)


    def get_diff_with(self, old_metadata, context, new=False, language=None):
        """Return a text with the diff between the given Metadata and new
        issue state.
        """
        root = context.root
        modifications = []
        if new:
            # New issue
            template = MSG(u'{field}: {old_value}{new_value}')
            empty = u''
        else:
            # Edit issue
            template = MSG(u'{field}: {old_value} to {new_value}')
            empty = MSG(u'[empty]').gettext(language=language)
        # Modification of title
        last_prop = old_metadata.get_value('title')
        last_title = last_prop.value if last_prop else empty
        new_title = self.get_value('title') or empty
        if last_title != new_title:
            field = MSG(u'Title').gettext(language=language)
            text = template.gettext(field=field, old_value=last_title,
                                    new_value=new_title, language=language)
            modifications.append(text)
        # List modifications
        fields = [
            ('product', MSG(u'Product')),
            ('module', MSG(u'Module')),
            ('version', MSG(u'Version')),
            ('type', MSG(u'Type')),
            ('priority', MSG(u'Priority')),
            ('state', MSG(u'State'))]
        for name, field in fields:
            field = field.gettext(language=language)
            last_prop = old_metadata.get_value(name)
            last_value = last_prop.value if last_prop else None
            new_value = self.get_value(name)
            # Detect if modifications
            if last_value == new_value:
                continue
            new_title = last_title = empty
            csv = self.parent.get_resource(name).handler
            if last_value or last_value == 0:
                rec = csv.get_record(last_value)
                if rec is None:
                    last_title = MSG(u'undefined').gettext(language=language)
                else:
                    last_title = csv.get_record_value(rec, 'title', language)
                    if not last_title:
                        last_title = csv.get_record_value(rec, 'title')
            if new_value or new_value == 0:
                rec = csv.get_record(new_value)
                new_title = csv.get_record_value(rec, 'title', language)
                if not new_title:
                    new_title = csv.get_record_value(rec, 'title')
            text = template.gettext(field=field, old_value=last_title,
                                    new_value=new_title, language=language)
            modifications.append(text)

        # Modifications of assigned_to
        new_user = self.get_value('assigned_to') or ''
        last_prop = old_metadata.get_value('assigned_to')
        last_user = last_prop.value if last_prop else None
        if last_user != new_user:
            if last_user:
                last_user = root.get_user(last_user).get_value('email')
            if new_user:
                new_user = root.get_user(new_user).get_value('email')
            field = MSG(u'Assigned To').gettext(language=language)
            text = template.gettext(field=field, old_value=last_user or empty,
                                    new_value=new_user or empty,
                                    language=language)
            modifications.append(text)

        # Modifications of cc_list
        last_prop = old_metadata.get_value('cc_list')
        last_cc = list(last_prop.value) if last_prop else ()
        new_cc = self.get_value('cc_list')
        new_cc = list(new_cc) if new_cc else []
        if last_cc != new_cc:
            last_values = []
            for cc in last_cc:
                value = root.get_user(cc).get_value('email')
                last_values.append(value)
            new_values = []
            for cc in new_cc:
                value = root.get_user(cc).get_value('email')
                new_values.append(value)
            field = MSG(u'CC').gettext(language=language)
            last_values = ', '.join(last_values) or empty
            new_values = ', '.join(new_values) or empty
            text = template.gettext(field=field, old_value=last_values,
                                    new_value=new_values, language=language)
            modifications.append(text)

        return u'\n'.join(modifications)


    def get_reported_by(self):
        comments = self.metadata.get_value('comment')
        return comments[0].get_parameter('author')


    def to_text(self):
        comments = self.get_value('comment')
        return u'\n'.join(comments)


    #######################################################################
    # User Interface
    #######################################################################
    def get_context_menus(self):
        return self.parent.get_context_menus() + [IssueTchackerMenu()]


    download_attachments = Issue_DownloadAttachments
    edit = Issue_Edit
    history = Issue_History




class IssueModel(Model):

    class_id = 'tchacker-issue-model'
    class_title = MSG(u'Issue model')

    base_class = Issue


    def init_resource(self, **kw):
        # XXX This should be done in ikaaro
        for field_name, field in self.base_class.get_fields():
            if not field.readonly:
                self.make_resource(field_name, ModelField_Inherited)

        ####################
        # Demonstration data
        ####################
        # Priority
        #field = self.make_resource('priority', ModelField_Choices)
        root = self.get_root()
        default_language = root.get_default_language()
        field = self.make_resource('priority', ModelField_Choices)
        field.set_value('required', True)
        field.set_value('choices_widget', 'select')
        field.set_value('title', u'Priority', language=default_language)
        field.make_resource('high', Choice)
        field.make_resource('medium', Choice)
        field.make_resource('low', Choice)
        # Product
        field = self.make_resource('product', ModelField_Choices)
        field.set_value('required', True)
        field.set_value('title', u'Product', language=default_language)
        field.set_value('choices_widget', 'select')
        field.make_resource('projet - module1', Choice)
        field.make_resource('projet - module2', Choice)
        # Type
        field = self.make_resource('type', ModelField_Choices)
        field.set_value('required', True)
        field.set_value('title', u'Type', language=default_language)
        field.set_value('choices_widget', 'select')
        field.make_resource('props - 2d', Choice)
        field.make_resource('props - 3d modelisation', Choice)
        field.make_resource('props - 3d texturing', Choice)
        # State
        field = self.make_resource('state', ModelField_Choices)
        field.set_value('required', True)
        field.set_value('title', u'State', language=default_language)
        field.set_value('choices_widget', 'select')
        field.make_resource('awaiting validation', Choice)
        field.make_resource('in progress', Choice)
        field.make_resource('validated', Choice)

