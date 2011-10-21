# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
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

from os.path import basename

# Import from itools
from itools.gettext import MSG
from itools.fs import FileName

# Import from ikaaro
from ikaaro.tracker import Tracker
from ikaaro.registry import register_resource_class
from ikaaro.registry import get_resource_class

from issue import Tchack_Issue
from tracker_views import Tchack_Tracker_View #, Tracker_Zip_Img
from tracker_views import Tchack_LastComments_View 
from tracker_views import Tchack_Tracker_ExportToCSVForm 
from tracker_views import Tchack_Tracker_ExportToCSV 
from tracker_views import Tchack_Tracker_AddIssue



class Tchack_Tracker(Tracker):

    class_id = 'tchack_tracker'
    class_version = '20110408'
    class_title = MSG(u'Tchack Tracker')
    class_description = MSG(u'To manage images, videos, bugs and tasks')
    class_views = Tracker.class_views #+ ['zip']

    # Configuration
    issue_class = Tchack_Issue

    # Views
    view = Tchack_Tracker_View()
    last_comments_view = Tchack_LastComments_View()
    add_issue = Tchack_Tracker_AddIssue()
    
    #export_to_csv_form = Tchack_Tracker_ExportToCSVForm()
    #export_to_csv = Tchack_Tracker_ExportToCSV()

    #search = Tchacker_Search()
    #zip = Tracker_Zip_Img()

    #######################################################################
    # Update
    #######################################################################

    def update_20110408(self):
        import os
        from tempfile import mkdtemp
        from itools.fs import vfs
        from ikaaro.file import Video
        from ikaaro.file import Image
        from issue import Tchack_Issue
        from videoencoding import VideoEncodingToFLV

        for issue in self.search_resources(cls=Tchack_Issue):

            attachments = issue.get_attachments()

            if attachments:
                for attachment in attachments:
                    file = issue.get_resource(attachment)
                    is_video = isinstance(file, Video)
                    if not is_video:
                        continue
                    if is_video:
                        has_thumb = False
                        try:
                            issue.get_resource("%s_thumb" % attachment)
                            has_thumb = True
                        except LookupError:
                            print("There is no thumbnail")
                            has_thumb = False

                    if not has_thumb:
                        # Create a thumbnail
                        thumbnail = issue.get_resource(attachment)
                        body = thumbnail.handler.to_str()
                        dirname = mkdtemp('thumb', 'ikaaro')
                        tempdir = vfs.open(dirname)
                        # Paste the file in the tempdir
                        tmpfolder = "%s" % (dirname)
                        #root_path = file.handler.database.path
                        name = thumbnail.name
                        tmp_uri = ("%s%s%s" % (tmpfolder, os.sep, name))
                        tmpfile = open("%s" % tmp_uri, "w+")
                        tmpfile.write(body)
                        tmpfile.close()
                        """
                        make_thumbnail_only(self, tmpfolder, inputfile, name, width):
                        """
                        # Get size
                        dim = VideoEncodingToFLV(thumbnail).get_size_and_ratio(tmp_uri)
                        width, height, ratio = dim
                        output = VideoEncodingToFLV(thumbnail).make_thumbnail_only(tmpfolder, name, name, width)
                        if output is not None:
                            thumbfilename, thumbmimetype,\
                            thumbbody, thumbextension = output['flvthumb']
                            #cls = get_resource_class(thumbmimetype)
                            issue.make_resource(thumbfilename, Image,
                                body=thumbbody, filename=thumbfilename,
                                extension=thumbextension, format=thumbmimetype)
                            #file.set_property("thumbnail", "True")
                            print("Issue:%s, Thumbnail: '%s' is created!" % (
                                                            issue.name, thumbfilename))
                        # Clean the temporary folder
                        vfs.remove(dirname)


    def update_20110125(self):
        """Create thumbnails for all images present in the Tchacker"
        """
        import os
        from tempfile import mkdtemp
        from PIL import Image as PILImage
        from itools.fs import vfs
        from ikaaro.file import Image
        from issue import Tchack_Issue

        i = 0

        for issue in self.search_resources(cls=Tchack_Issue):

            history = issue.get_history()

            for record in history.get_records():

                filename = record.file
                comment = record.comment
                is_image = False
                if not comment and not filename:
                    continue
                if filename:
                    file = issue.get_resource(filename)
                    is_image = isinstance(file, Image)
                    if not is_image:
                        continue
                    if is_image:
                        if file.metadata.format == "image/x-photoshop":
                            break
                        print("%s.Tracker.%s.Issue.%s.id.%s contain an image that need a Thumbnail"
                            % (i, issue.parent.parent.name, issue.name, record.id))

                        name = file.name
                        # Handler is cached, and cache grow so much that it kill
                        # the process, so we need to use a simple os file open().
                        handler = file.handler
                        filename, extension, language = FileName.decode(basename(handler.key))

                        fs = self.metadata.database.fs
                        #print("Image that need Thumbnail = %s" % fs.get_absolute_path(file.handler.key))
                        fileabspath = fs.get_absolute_path(file.handler.key)
                        with open("%s" % fileabspath, "r") as f:
                            body = f.read()

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
                                print("IOError = %s" % fileabspath)
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
                            self.make_resource(cls, issue, ima,
                                body=thumb_data, filename=ima,
                                extension=ext, format='image/%s' % ext)
                            print("Image %s, Taille %s" % (ima, te[1]))
                        file.metadata.set_property('thumbnail', "True")
                        # Clean the temporary folder
                        vfs.remove(dirname)
                    i+= 1


    def update_20110122(self):
        """If an issue contains a video file,
        encoded in h264 and widder than 319px,
        we encode a low version and create a thumbnail,
        and erase the original file.
        """
        import os
        from issue import Tchack_Issue
        from ikaaro.file import Video
        from ikaaro.exceptions import ConsistencyError

        for issue in self.search_resources(cls=Tchack_Issue):

            history = issue.get_history()

            for record in history.get_records():

                filename = record.file
                comment = record.comment
                is_video = False
                if not comment and not filename:
                    continue
                if filename:
                    file = issue.get_resource(filename)
                    is_video = isinstance(file, Video)
                    if not is_video:
                        continue
                    if is_video:
                        name = file.name
                        thumb = file.metadata.get_property('thumbnail')
                        filename = file.metadata.get_property('filename')

                        handler = file.handler.key
                        video = basename(handler)
                        videoname, videoext = os.path.splitext(video)

                        as_low = issue.get_handler().has_handler(
                            "%s_low.flv" % videoname)
                        low = video.rfind("_low")
                        if low == -1:
                            is_low = False
                        else:
                            is_low = True
                            bigfile = name.replace("_low","")
                        is_big = issue.get_handler().has_handler(
                            "%s" % video)

                        old_thumb = "thumb_%s" % name
                        as_old_thumb = issue.get_handler().has_handler(
                            "%s" % old_thumb)

                        if thumb == "False" and as_low and is_big:
                            print("Remove Big original file : %s" % name)
                            issue.del_resource(
                                name, soft='False')
                        if thumb == "False" and is_low:
                            print("Set thumbnail to True : %s" % name)
                            file.set_property("thumbnail", "True")
                            print("Remove Big original file : %s" % video)
                            try:
                                issue.del_resource(
                                    bigfile, soft='False')
                            except ConsistencyError:
                                print '*'
                                print '* Before going further, you nedd to run the following command on the instance:'
                                print '     $ icms-update-catalog.py <instance>'
                                print '*'
                                exit(0)
                        if as_old_thumb:
                            print("Remove the Old thumb for '%s'" % name)
                            issue.del_resource(old_thumb, soft='False')
                        #XXX Need to erase the original file (big one)


    def update_20110121(self):
        """If an issue contains a video file,
        larger than 319px,
        we encode a low version and create a thumbnail,
        and erase the original file.
        """
        import os
        from tempfile import mkdtemp
        from issue import Tchack_Issue
        from ikaaro.file import Video
        from itools.fs import vfs
        from ikaaro.registry import get_resource_class
        from videoencoding import VideoEncodingToFLV


        for issue in self.search_resources(cls=Tchack_Issue):

            history = issue.get_history()

            for record in history.get_records():

                filename = record.file
                comment = record.comment
                is_video = False
                if not comment and not filename:
                    continue
                if filename:
                    file = issue.get_resource(filename)
                    is_video = isinstance(file, Video)
                    mimetype = file.handler.get_mimetype()
                    print("file = %s, filename = %s, mimetype = %s" % (file, filename, mimetype))

                    if not is_video:
                        continue
                    if is_video:
                        name = file.name
                        mimetype = file.handler.get_mimetype()
                        name , ext, lang = FileName.decode(filename)

                        handler = file.handler.key
                        videoname = basename(handler)

                        thumb = file.metadata.get_property('thumbnail')
                        #joinfilename = file.metadata.get_property('filename')

                        as_low = issue.get_handler().has_handler(
                            "%s_low.flv" % name)
                        is_low = name.rfind("_low")
                        is_big = issue.get_handler().has_handler(
                            "%s" % videoname)

                        if thumb == "False" and not as_low and is_big:
                            # Not low encoded
                            if is_low == -1:
                                print("--> is_low = -1\nThe file '%s' is not \
                                    a low one" % name)
                                print("is_low = -1")
                                body = file.handler.to_str()
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
                                dim = VideoEncodingToFLV(file).get_size_and_ratio(tmp_uri)
                                width, height, ratio = dim
                                # In case of a video in h264 and widder than 319px
                                # We encode it in Flv at 640px width  and make a thumbnail
                                width_low = 640
                                print("XXX - File not encoded, but already have " +
                                    "an old thumb. Encode & create a \"_low_thumb\"." +
                                    " Keep Thumb property to False for late " +
                                    "update AND modify issue value to %s_low_thumb.")
                                encoded = VideoEncodingToFLV(file).encode_video_to_flv(
                                    tmpfolder, name, name, width_low)
                                if encoded is not None:
                                    vidfilename, vidmimetype, \
                                        vidbody, vidextension, \
                                        width, height = encoded['flvfile']
                                    thumbfilename, thumbmimetype, \
                                        thumbbody, thumbextension = encoded['flvthumb']

                                    handler = file.handler
                                    #print("vidfilename = %s" % vidfilename)
                                    #print("filename = %s" % filename)
                                    # Replace
                                    try:
                                        handler.load_state_from_string(vidbody)
                                    except Exception, e:
                                        handler.load_state()
                                        print("Failed to load the file: %s" % str(e))
                                    # Update "filename" property
                                    file.set_property("filename", filename + "." + vidextension)
                                    # Update metadata format
                                    metadata = file.metadata
                                    #print("metadata.format = %s" % metadata.format)
                                    if '/' in metadata.format:
                                        if vidmimetype != metadata.format:
                                            metadata.format = vidmimetype

                                    # Update handler name
                                    handler_name = basename(handler.key)
                                    #print("handler_name = %s" % handler_name)
                                    old_name, old_extension, old_lang = FileName.decode(handler_name)
                                    new_name , new_extension, new_lang = FileName.decode(filename)
                                    # FIXME Should 'FileName.decode' return lowercase extensions?
                                    new_extension = vidextension.lower()
                                    #print("old_name = %s, old_extension = %s, old_lang = %s, new_extension = %s" % (
                                    #    old_name, old_extension, old_lang, new_extension))
                                    if old_extension is not new_extension:
                                        # "handler.png" -> "handler.jpg"
                                        folder = file.parent.handler
                                        filename = FileName.encode((old_name, new_extension, old_lang))
                                        #folder.move_handler(handler_name,
                                        #        vidfilename +"."+ vidextension)
                                        folder.move_handler(handler_name, filename)
                                    # Create the thumbnail PNG resources
                                    cls = get_resource_class(thumbmimetype)
                                    self.make_resource(cls, issue, thumbfilename,
                                        body=thumbbody, filename=thumbfilename,
                                        extension=thumbextension, format=thumbmimetype)
                                    # The size is returned by videoencoding
                                    file.metadata.set_property('width', str(width))
                                    file.metadata.set_property('height', str(height))
                                    file.metadata.set_property('ratio', str(ratio))
                                    # We keep the 'thumbnail' to False
                                    # to make difference between old & new video files
                                    file.set_property("thumbnail", "False")
                                # Clean the temporary folder
                                vfs.remove(dirname)
                                print("\n------")
                            else:
                                print("--> is_low = xxx\nThe file '%s' is already \
                                    a low one\n------" % name)

                        if thumb == "False" and as_low:
                            #The video as thumb value to False, but already
                            #encoded in LOW. Erase the original file.
                            print("333 - Need to change the Thumb value to True, and erase the Big original file, and modify issue value to %s_low")

                        if thumb == "True" and as_low and is_big:
                            #The thumbnail value was not attributed to the
                            #low" resource in first version, add it now.
                            print("444 - Thumb=True and as_lox=True, put the " +
                                "Low link in history. Set thumb to False, %s." % (filename))
                            lowname = "%s_low" % filename
                            history.update_record(
                                record.id, ** {'file':"%s" % lowname})
                            print("history.%s change from '%s' to '%s'" % (
                                record.id, name, lowname))
                            print("record.id = %s, lowname = %s" % (
                                record.id, lowname))
                            # copy metadat Big > Low
                            newfile = issue.get_resource(lowname)
                            newfile.metadata.set_property("thumbnail", "False")
                            # Erase Big in next upgrade
                            print("-----\n")



    def update_20100718(self):
        """If an issue contains a video file, encoded in h264 and widder than 640px,
        we encode a low version and create a thumbnail.
        """
        import os
        from tempfile import mkdtemp
        from issue import Tchack_Issue
        from ikaaro.file import Video
        #from ikaaro.exceptions import ConsistencyError
        from itools.fs import vfs
        from itools.fs import FileName
        #from itools.core import guess_extension
        #from itools.uri import get_uri_path
        from ikaaro.registry import get_resource_class
        from videoencoding import VideoEncodingToFLV

        for issue in self.search_resources(cls=Tchack_Issue):

            history = issue.get_history()

            for record in history.get_records():

                filename = record.file
                comment = record.comment
                is_video = False
                if not comment and not filename:
                    continue
                if filename:
                    file = issue.get_resource(filename)
                    is_video = isinstance(file, Video)
                    if not is_video:
                        continue
                    if is_video:
                        name = file.name
                        filename, ext, lang = FileName.decode(name)
                        dirname = mkdtemp('videoencoding', 'ikaaro')
                        tempdir = vfs.open(dirname)
                        # Paste the file in the tempdir
                        tmpfolder = "%s" % (dirname)
                        #root_path = file.handler.database.path
                        tmp_uri = ("%s%s%s" % (tmpfolder, os.sep, name))
                        tmpfile = open("%s" % tmp_uri, "w+")
                        tmpfile.write(file.handler.to_str())
                        tmpfile.close()
                        # Get size
                        dim = VideoEncodingToFLV(file).get_size_and_ratio(tmp_uri)
                        width, height, ratio = dim
                        # Codec
                        venc = VideoEncodingToFLV(file).get_video_codec(tmp_uri)
                        # In case of a video in h264 and larger than 319px
                        # We encode it in Flv and make a thumbnail
                        width_low = 640
                        if int(width) > width_low and venc == "h264":
                            #print("The video is in H264 video codec and wider
                            #      than 640px, create a low version")
                            # video is already in temp dir, so encode it
                            encoded = VideoEncodingToFLV(file).encode_video_to_flv(
                                tmpfolder, name, name, width_low)
                            file.metadata.set_property('width', width)
                            file.metadata.set_property('height', height)
                            file.metadata.set_property('ratio', str(ratio))
                            file.metadata.set_property('thumbnail', "True")
                            if encoded is not None:
                                vidfilename, vidmimetype, \
                                    vidbody, vidextension, \
                                    width, height = encoded['flvfile']
                                thumbfilename, thumbmimetype, \
                                    thumbbody,thumbextension = encoded['flvthumb']
                                # Create the video resources
                                cls = get_resource_class(vidmimetype)
                                issue.make_resource(cls, issue, vidfilename,
                                    body=vidbody, filename=vidfilename,
                                    extension=vidextension, format=vidmimetype)
                                #height_low = int(round(float(width_low) / ratio))
                                vid = issue.get_resource(vidfilename)
                                vid.metadata.set_property('width',
                                                          str(width))
                                vid.metadata.set_property('height',
                                                          str(height))
                                # Create the thumbnail PNG resources
                                cls = get_resource_class(thumbmimetype)
                                issue.make_resource(cls, issue, thumbfilename,
                                    body=thumbbody, filename=thumbfilename,
                                    extension=thumbextension, format=thumbmimetype)

                            # Clean the temporary folder
                            vfs.remove(dirname)
                            #print("Done: %s 's low version is created" % name)
                        else:
                            file.metadata.set_property('thumbnail', "False")


###########################################################################
# Register
###########################################################################
register_resource_class(Tchack_Tracker)
