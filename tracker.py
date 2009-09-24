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
    class_version = '20090706'
    class_title = MSG(u'Tchack Issue Tracker')
    class_description = MSG(u'To manage images, bugs and tasks')
    class_views = Tracker.class_views + ['zip']

    # Configuration
    issue_class = Tchack_Issue

    # Views
    view = Tchacker_View()
    zip = Tracker_Zip_Img()

    #######################################################################
    # Update
    #######################################################################
    def update_20090705(self):
        """
        Encode the unencoded MOV or AVI file, and add the thumb, erase the
        original file.
        """
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
                        if ext is None:
                            mimetype = file.get_content_type()
                            ext = guess_extension(mimetype)[1:]
                        if(mimetype == 'video/x-msvideo'
                            or mimetype == 'video/quicktime'):
                            pprint("The file %s.%s will be encoded in FLV, \
                                replaced by, then erased." % (filename, ext))
                            
                            handler_path = get_uri_path(issue.handler.uri)
                            
                            dirname = mkdtemp('videoencoding', 'ikaaro')
                            tempdir = vfs.open(dirname)
                            
                            # Paste the file in the tempdir
                            tmp_uri= "file:///%s/%s" % (dirname, filename)
                            vfs.copy(file.handler.uri, tmp_uri)
                            
                            # Encode to 512 of width
                            encoded = VideoEncodingToFLV(file).encode_avi_to_flv(
                                 dirname, filename, name, 512)
                            
                            if encoded is not None:
                                flvfilename, flvmimetype,
                                flvbody, flvextension = encoded['flvfile']
                                thumbfilename, thumbmimetype,
                                thumbbody, thumbextension = encoded['flvthumb']
                            # Create the video FLV and thumbnail PNG resources
                            video = get_resource_class(flvmimetype)
                            thumbnail = get_resource_class(thumbmimetype)
                            # Remove the original files
                            if vfs.exists(file.handler.uri):
                                vfs.remove(file.handler.uri)
                            if vfs.exists(file.metadata.uri):
                                vfs.remove(file.metadata.uri)
                            
                            video.make_resource(video, issue, name,
                                body=flvbody, filename=flvfilename,
                                extension=flvextension, format=flvmimetype)
                            thumbnail.make_resource(thumbnail, issue, thumbfilename,
                                body=thumbbody, filename=thumbfilename,
                                extension=thumbextension, format=thumbmimetype)
                            
                            # Clean the temporary folder
                            vfs.remove(dirname)
                            
                            pprint("====================")
                        pprint("xxxxxxxxxxxxxxxx")

###########################################################################
# Register
###########################################################################

register_resource_class(Tchack_Tracker)
