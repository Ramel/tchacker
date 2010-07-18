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

#from resources import Tchack_Resources
from issue import Tchack_Issue
from tracker_views import Tchacker_View, Tracker_Zip_Img


class Tchack_Tracker(Tracker):

    class_id = 'tchack_tracker'
    class_version = '20100718'
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

    def update_20100718(self):
        """If an issues file is a video, encoded in h264 and widder than 640px,
        we ecode a low version and create a thumbnail.
        """
        import os
        from pprint import pprint
        from datetime import datetime
        from tempfile import mkdtemp
        from issue import Tchack_Issue
        from ikaaro.file import Video
        from ikaaro.exceptions import ConsistencyError
        from itools import vfs
        from itools.vfs import FileName
        from itools.core import guess_extension
        from itools.uri import get_uri_path
        from videoencoding import VideoEncodingToFLV
        from ikaaro.registry import get_resource_class
        
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
                        root_path = file.handler.database.path
                        #print("root_path = %s" % root_path)
                        tmp_uri = ("%s%s%s" % (tmpfolder, os.sep, name))
                        tmpfile = open("%s" % tmp_uri, "w+")
                        tmpfile.write(file.handler.to_str())
                        tmpfile.close()
                        # Get size
                        dim = VideoEncodingToFLV(file).get_size_and_ratio(tmp_uri)
                        #print("dim = %s" % dim)
                        width, height, ratio = dim
                        # Codec 
                        venc = VideoEncodingToFLV(file).get_video_codec(tmp_uri)
                        #print("venc = %s" % venc)
                        # In case of a video in h264 and widder than 640px
                        # We encode it in Flv and make a thumbnail
                        width_low = 640
                        print("codec = %s" % venc)
                        if int(width) > width_low and venc == "h264":
                            #print("int(width) > 960 and venc == h264")
                            video_low = ("%s_low" % name)
                            # video is already in temp dir, so encode it
                            encoded = VideoEncodingToFLV(file).encode_video_to_flv(
                                tmpfolder, name, name, width_low)
                            file.metadata.set_property('width', width)
                            file.metadata.set_property('height', height)
                            file.metadata.set_property('ratio', str(ratio))
                            file.metadata.set_property('thumbnail', "True")
                            if encoded is not None:
                                vidfilename, vidmimetype, vidbody, vidextension = encoded['flvfile']
                                thumbfilename, thumbmimetype, thumbbody, thumbextension = encoded['flvthumb']
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
                        else:
                            file.metadata.set_property('thumbnail', "False")


###########################################################################
# Register
###########################################################################

register_resource_class(Tchack_Tracker)

