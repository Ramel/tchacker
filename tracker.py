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

# Import from itools
from itools.gettext import MSG

# Import from ikaaro
from ikaaro.tracker import Tracker
from ikaaro.registry import register_resource_class
from ikaaro.registry import get_resource_class

#from resources import Tchack_Resources
from issue import Tchack_Issue
from tracker_views import Tchacker_View, Tracker_Zip_Img


class Tchack_Tracker(Tracker):

    class_id = 'tchack_tracker'
    #class_version = '20100718'
    #class_version = '20110121'
    class_version = '20110125'
    class_title = MSG(u'Tchack Issue Tracker')
    class_description = MSG(u'To manage images, videos, bugs and tasks')
    class_views = Tracker.class_views + ['zip']

    # Configuration
    issue_class = Tchack_Issue

    # Views
    view = Tchacker_View()
    zip = Tracker_Zip_Img()

    #######################################################################
    # Update
    #######################################################################

    def update_20110125(self):
        """Create thumbnails for all images present in the Tchacker"
        """
        import glob, os
        from tempfile import mkdtemp
        from PIL import Image as PILImage
        from itools.fs import vfs
        from ikaaro.file import Image
        from issue import Tchack_Issue


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
                        print("Issue.%s.id.%s contain an image that need a Thumbnail"
                            % (issue.name, record.id))
                        name = file.name
                        mimetype = file.handler.get_mimetype()
                        body = file.handler.to_str()

                        dirname = mkdtemp('makethumbs', 'ikaaro')
                        tempdir = vfs.open(dirname)
                        #print("dirname = %s" % dirname)
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
                        cls = get_resource_class('image/png')
                        thumbext = (["_LOW", low], ["_MED", med], ["_HIG", hig])
                        for te in thumbext:
                            im = PILImage.open(tmp_uri)
                            im.thumbnail(te[1], PILImage.ANTIALIAS)
                            uri = tmpfolder + os.sep 
                            ima = name + te[0] 
                            ext = "png"
                            im.save(uri + ima + ext, "PNG")
                            # Copy the thumb content
                            thumb_file = tempdir.open(ima + ext)
                            try:
                                thumb_data = thumb_file.read()
                            finally:
                                thumb_file.close()
                            self.make_resource(cls, issue, ima,
                                body=thumb_data, filename=ima,
                                extension=ext, format='image/png')
                        
                        file.metadata.set_property('thumbnail', "True")
                        # Clean the temporary folder
                        vfs.remove(dirname)


    def update_20110121(self):
        """If an issue contains a video file,
        encoded in h264 and widder than 319px,
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
                    if not is_video:
                        continue
                    if is_video:
                        name = file.name
                        mimetype = file.handler.get_mimetype()
                        body = file.handler.to_str()

                        thumb = file.metadata.get_property('thumbnail')
                        print("issue = %s, name = %s, thumbnail = %s" %
                            (issue.name, name, thumb))
                        print("issue = %s, name = %s, mimetype = %s" %
                            (issue.name, name, mimetype))
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
                        # Codec 
                        #venc = VideoEncodingToFLV(file).get_video_codec(tmp_uri)
                        # In case of a video in h264 and widder than 319px
                        # We encode it in Flv at 640px width  and make a thumbnail
                        width_low = 640
                        print("Video without Thumbnail, encode it")
                        video_low = ("%s_low" % name)
                        height_low = int(round(float(width_low) / ratio))
                        if thumb == "False":
                            # video is already in temp dir, so encode it
                            encoded = VideoEncodingToFLV(file).encode_video_to_flv(
                                tmpfolder, name, name, width_low)
                            """
                            file.metadata.set_property('width', width)
                            file.metadata.set_property('height', height)
                            file.metadata.set_property('ratio', str(ratio))
                            file.metadata.set_property('thumbnail', "True")
                            """
                            if encoded is not None:
                                vidfilename, vidmimetype, \
                                    vidbody, vidextension = encoded['flvfile']
                                thumbfilename, thumbmimetype, \
                                    thumbbody, thumbextension = encoded['flvthumb']
                                # Create the video resources
                                cls = get_resource_class(vidmimetype)
                                self.make_resource(cls, issue, vidfilename,
                                    body=vidbody, filename=vidfilename,
                                    extension=vidextension, format=vidmimetype)
                                vid = issue.get_resource(vidfilename)
                                vid.metadata.set_property('width', str(width_low))
                                vid.metadata.set_property('height', str(height_low))
                                vid.metadata.set_property('ratio', str(ratio))
                                vid.metadata.set_property('thumbnail', "True")
                                # Create the thumbnail PNG resources
                                cls = get_resource_class(thumbmimetype)
                                self.make_resource(cls, issue, thumbfilename,
                                    body=thumbbody, filename=thumbfilename,
                                    extension=thumbextension, format=thumbmimetype)
                            #print("Old: %s, New: %s" % (name, video_low))
                            #print("issue.get_links() = %s" % issue.get_links())
                            #issue.update_links(record.file, video_low)
                            history.update_record(record.id, **{'file': video_low})
                            #database = get_context().database
                            issue.del_resource(name)
                            try:
                                issue.del_resource("thumb_%s" % name)
                            except LookupError:
                                pass
                        elif (thumb == "True" and issue.get_resource(
                                                        "%s_low" % name, soft=True)):
                            # The thumbnail value was not attributed to the
                            # "low" resource in first version, add it now.
                            vid = issue.get_resource(video_low, soft=True)
                            vid.metadata.set_property('width', str(width_low))
                            vid.metadata.set_property('height', str(height_low))
                            vid.metadata.set_property('ratio', str(ratio))
                            vid.metadata.set_property('thumbnail', "True")
                            #issue.update_links(name, "%s_low" % name)
                            history.update_record(
                                record.id, **{'file': "%s_low" % name})
                            #get_context().database.change_resource(issue)
                            try:
                                issue.del_resource(name)
                            except LookupError:
                                pass
                        else :
                            try:
                                issue.del_resource("thumb_%s" % name)
                            except LookupError:
                                pass
                            #issue.del_resource("thumb_%s" % name)
                            #file.metadata.set_property('thumbnail', 'True')
                            #database.remove_resource(name)

                        # Clean the temporary folder
                        vfs.remove(dirname)



    def update_20100718(self):
        """If an issue contains a video file, encoded in h264 and widder than 640px,
        we encode a low version and create a thumbnail.
        """
        import os
        from datetime import datetime
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
                                    vidbody, vidextension = encoded['flvfile']
                                thumbfilename, thumbmimetype, \
                                    thumbbody,thumbextension = encoded['flvthumb']
                                # Create the video resources
                                cls = get_resource_class(vidmimetype)
                                issue.make_resource(cls, issue, vidfilename,
                                    body=vidbody, filename=vidfilename,
                                    extension=vidextension, format=vidmimetype)
                                height_low = int(round(float(width_low) / ratio))
                                vid = issue.get_resource(vidfilename)
                                vid.metadata.set_property('width',
                                                          str(width_low))
                                vid.metadata.set_property('height',
                                                          str(height_low))
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
