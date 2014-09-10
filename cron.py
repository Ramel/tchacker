# -*- coding: UTF-8 -*-
# Copyright (C) 2014 Armel FORTUN <armel@tchack.com>
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
from datetime import timedelta
from cStringIO import StringIO
from os import sep
from threading  import Thread
import pexpect

# Import from itools
from itools.fs import lfs, vfs
from itools.loop import cron
from itools.database import PhraseQuery, AndQuery
from itools.csv import Property
from itools.web import get_context
from itools.core import get_abspath

# Import from ikaaro
from ikaaro.server import get_fake_context
from ikaaro.registry import get_resource_class

# Import from PIL
from PIL import Image as PILImage

# Import from videoencoding
from videoencoding import VideoEncodingToFLV

from monkey import Image


ffmpeg_worker = {'worker': False, 'pass': False}


def run_cron(self):
    cron(self._make_image_thumbnails,
            timedelta(seconds=30),
            first_call_delay=timedelta(seconds=30))


def make_thumbnails(self):
    self.run_cron()


def update_database(context, database, resource):
    try:
        context.set_mtime = True
        # Reindex resource without committing
        catalog = database.catalog
        catalog.unindex_document(str(resource.abspath))
        catalog.index_document(resource.get_catalog_values())
        catalog.save_changes()
    except Exception as e:
        print('CRON ERROR COMMIT CATALOG')
        print("%s" % e)


class ThreadWorker():
    """The basic idea is given a function create an object.
    The object can then run the function in a thread.
    It provides a wrapper to start it,check its status,and get data out the function.
    """

    def __init__(self,func):
        self.thread = None
        self.data = None
        self.func = self.save_data(func)

    def save_data(self,func):
        '''modify function to save its returned data'''
        def new_func(*args, **kwargs):
            self.data=func(*args, **kwargs)

        return new_func

    def start(self,params):
        self.data = None
        if self.thread is not None:
            if self.thread.isAlive():
                return 'running' #could raise exception here

        #unless thread exists and is alive start or restart it
        self.thread = Thread(target=self.func,args=params)
        self.thread.start()
        return 'started'

    def status(self):
        if self.thread is None:
            return 'not_started'
        else:
            if self.thread.isAlive():
                return 'running'
            else:
                return 'finished'

    def get_results(self):
        if self.thread is None:
            return 'not_started' #could return exception
        else:
            if self.thread.isAlive():
                return 'running'
            else:
                return self.data


def ffmpeg(cli):
    """Thrown the ffmpeg command line, and return True if completed
    """
    thread = pexpect.spawn(cli)
    cpl = thread.compile_pattern_list(pexpect.EOF)
    i = thread.expect_list(cpl, timeout=None)
    while 1:
        if i == 0:
            return True
        else:
            return False


def _make_image_thumbnails(self):
    """The callback
    """
    # A variable shared between the different callback's calls
    ffmpeg_worker = self.ffmpeg_worker['worker']
    ffmpeg_pass = self.ffmpeg_worker['pass']
    #print("ffmpeg_worker = %s" % ffmpeg_worker)

    print("cron started!")

    # Check if there is a lock
    encodingfolder = get_abspath('ffmpeg-encoding%s' % sep)
    #self.encoding = lfs.resolve2(self.target, encodingfolder)
    encoding = lfs.open(encodingfolder)

    lock = False

    for name in encoding.get_names():
        if name == 'lock':
            #print("lock")
            lock = True

    if not lock:
        #print("Need to create a lock file while encoding/resizing video/image!")
        encoding.make_file('lock')

    database = self.database
    database.save_changes()

    # Build fake context
    context = get_fake_context()
    context.server = self
    context.database = self.database
    context.root = self.root
    context.site_root = self.root

    ##############
    # Images
    ##############
    # Search for images without thumbnails
    q1 = PhraseQuery('has_thumb', False)
    q2 = PhraseQuery('need_thumb', True)
    q3 = PhraseQuery('is_image', True)
    query = AndQuery(q1, q2, q3)

    for image in self.root.search(query).get_documents():
        name = image.name
        print("\tFound an image without thumbnails: %s" % name)
        abspath = image.abspath
        # Get the resource
        resource = context.root.get_resource(abspath)
        container = resource.parent
        abspath = container.abspath
        tmpdata = resource.get_handler().key

        low = 256, 256
        med = 800, 800
        hig = 1024, 1024

        # Create the thumbnail PNG resources
        thumbext = (["_HIG", hig], ["_MED", med], ["_LOW", low])

        for te in thumbext:
            try:
                im = PILImage.open(str(tmpdata))
            except IOError as e:
                print("IOError = %s" % e)
            # make a thumbnail
            im.thumbnail(te[1], PILImage.ANTIALIAS)
            ima = name + te[0]
            # Some images are in CMYB, force RVB if needed
            if im.mode != "RGB":
                im = im.convert("RGB")
            # Copy the thumb content
            thumb_filename = ima + ".jpg"
            # Copy the thumb content
            thumb_file = StringIO()
            im.save(thumb_file, 'jpeg', quality=85)
            thumb_file.seek(0)
            try:
                thumb_data = thumb_file.read()
            finally:
                thumb_file.close()
            format = 'image/jpeg'
            cls = get_resource_class(format)

            imageThumb = container.make_resource(
                    ima, Image,
                    body=thumb_data,
                    filename=thumb_filename,
                    extension='jpg',
                    format=format
                    )
            imageThumb.init_resource()
            is_thumb = Property(True)
            imageThumb.metadata.set_property('is_thumb', is_thumb)

            update_database(context, database, imageThumb)

        # Now we need to update the has_thumb property in the file metadata
        has_thumb = Property(True)
        resource.metadata.set_property('has_thumb', has_thumb)
        need_thumb = Property(False)
        resource.metadata.set_property('need_thumb', need_thumb)

        update_database(context, database, resource)

        # Save changes
        print("\t\tAdd thumbnails for: %s" % image.abspath)
        context.git_message = "Add thumbnails for: %s" % image.abspath
        database.save_changes()

    ##############
    # Videos
    ##############
    # Search for videos unencoded
    q1 = PhraseQuery('encoded', False)
    q2 = PhraseQuery('is_video', True)
    query = AndQuery(q1, q2)

    #search = self.root.search(query)

    for video in self.root.search(query).get_documents():
        name = video.name
        print("\tFound a video to encode: %s" % name)
        abspath = video.abspath
        context = get_context()
        # Get the resource
        resource = context.root.get_resource(abspath)
        container = resource.parent

        #print("target = %s" % self.target)
        ffmpeg_encoding_folder = lfs.resolve2(self.target, 'ffmpeg-encoding')
        if not lfs.exists(ffmpeg_encoding_folder):
            lfs.make_folder(ffmpeg_encoding_folder)
        resource_tmp_folder = resource.get_property("tmp_folder")
        tmp_folder = get_abspath('%s%s%s%s' % (
                            ffmpeg_encoding_folder, sep,
                            resource_tmp_folder, sep))

        print("tmp_folder = %s" % tmp_folder)

        WIDTH_LOW = 640
        EXTENSION = "mp4"
        COPYRIGHTS = u"Tous droits réservés - Tchack/ALUMA Productions"
        tmp_uri = ("%s%s%s" % (tmp_folder, sep, name))
        tmpfile = open("%s" % tmp_uri)
        video_filename = "%s.%s" % (name, EXTENSION)
        tmp_video_path_filename = tmp_folder + video_filename
        WAIT = 30

        # Get ratio
        o_video = VideoEncodingToFLV(tmpfile)
        ratio = o_video.get_ratio(tmp_folder, name)

        # Find if the video is landscape or portrait
        output_size = int(WIDTH_LOW)
        size = o_video.get_size_frompath(tmp_folder, name)
        in_w = int(size[0])
        in_h = int(size[1])
        if in_w > in_h:
            # Landscape
            if in_w < output_size:
                width = in_w
                height = in_h
            else:
                width = output_size
                height = int(round(float(output_size)/ratio))
        else:
            # Portrait
            if in_h < output_size:
                width = in_w
                height = in_h
            else:
                width = int(round(float(output_size)*ratio))
                height = output_size

        #print("Size: FROM %sx%s TO %sx%s" % (in_w, in_h, width, height))

        print("ffmpeg_worker = %s" % ffmpeg_worker)
        # First pass
        if not ffmpeg_worker and not ffmpeg_pass:
            ffmpeg_cli = 'nice -n 8 ffmpeg -y -i %s%s -f %s '\
                    '-pass 1 '\
                    '-preset slow ' \
                    '-vprofile baseline -vcodec libx264 -vb 512k -bufsize 512k '\
                    '-an '\
                    '-pix_fmt yuv420p -strict -2 -r 25 '\
                    '-vf '\
                    '"scale=trunc(%s/2)*2:-1,scale=trunc(%s/2)*2:trunc(%s/2)*2,'\
                    'drawtext=fontfile='\
                    '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'\
                    ':fontsize=12:timecode=\'00\:00\:00\:00\':rate=25:'\
                    'fontcolor=white:borderw=2:x=10:y=10,'\
                    'drawtext=fontfile='\
                    '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'\
                    ':fontcolor=white@0.25:x=(w-tw)/2'\
                    ':y=h-(2*lh):fontsize=10:text=\'%s\'" '\
                    '-passlogfile %s%s '\
                    '/dev/null' % (
                    tmp_folder, name, EXTENSION,
                    int(width), int(width), int(height),
                    COPYRIGHTS,
                    tmp_folder, name)
            #print(ffmpeg_cli)
            print("ffmpeg_worker does not exist, start it!")
            ffmpeg_worker = ThreadWorker(ffmpeg)
            ffmpeg_worker.start((ffmpeg_cli,))
            ffmpeg_status = ffmpeg_worker.status()
            #print("ffmpeg_worker.status() = %s" % ffmpeg_status)
            self.ffmpeg_worker['worker'] = ffmpeg_worker
            self.ffmpeg_worker['pass'] = "first"
            return WAIT
        if ffmpeg_worker and ffmpeg_pass == 'first':
            ffmpeg_status = ffmpeg_worker.status()
            #print("ffmpeg_status = %s" % ffmpeg_status)
            if ffmpeg_status == 'running':
                print "First pass running"
                return WAIT
            elif ffmpeg_status == 'not_started':
                print "First pass not started! Bug!"
                return False
            elif ffmpeg_status == 'finished':
                print "First pass finished"
                # Second pass
                ffmpeg_cli = 'nice -n 8 ffmpeg -y -i %s%s -f %s '\
                        '-pass 2 -preset slow '\
                        '-vprofile baseline -vcodec libx264 -vb 512k -bufsize 512k '\
                        '-acodec libfaac -ab 128k '\
                        '-pix_fmt yuv420p -strict -2 -r 25 '\
                        '-movflags +faststart '\
                        '-vf '\
                        '"scale=trunc(%s/2)*2:-1,scale=trunc(%s/2)*2:trunc(%s/2)*2,'\
                        'drawtext=fontfile='\
                        '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'\
                        ':fontsize=12:timecode=\'00\:00\:00\:00\':rate=25:'\
                        'fontcolor=white:borderw=2:x=10:y=10,'\
                        'drawtext=fontfile='\
                        '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'\
                        ':fontcolor=white@0.25:x=(w-tw)/2'\
                        ':y=h-(2*lh):fontsize=10:text=\'%s\'" '\
                        '-passlogfile %s%s '\
                        '%s' % (
                        tmp_folder, name, EXTENSION,
                        int(width), int(width), int(height),
                        COPYRIGHTS,
                        tmp_folder, name,
                        tmp_video_path_filename)
                #print(ffmpeg_cli)
                print("Start second pass!")
                ffmpeg_worker = ThreadWorker(ffmpeg)
                ffmpeg_worker.start((ffmpeg_cli,))
                ffmpeg_status = ffmpeg_worker.status()
                #print("ffmpeg_worker.status() = %s" % ffmpeg_status)
                self.ffmpeg_worker['worker'] = ffmpeg_worker
                self.ffmpeg_worker['pass'] = "second"
                return WAIT
        else:
            ffmpeg_status = ffmpeg_worker.status()
            #print("ffmpeg_status = %s" % ffmpeg_status)
            if ffmpeg_status == 'running':
                print "running"
                return WAIT
            elif ffmpeg_status == 'not_started':
                print "Not started bug!"
                return False
            elif ffmpeg_status == 'finished':
                print "finished"
                # if finished, check if the folder is not already deleted
                if not lfs.exists(tmp_video_path_filename):
                    return WAIT
                else:
                    pass

                o_video.make_video_thumbnail(tmp_folder, name, EXTENSION, width)

                tmpdir = vfs.open(tmp_folder)

                # Copy the video content to a data variable
                video_file = tmpdir.open(video_filename)
                try:
                    video_data = video_file.read()
                finally:
                    video_file.close()

                # Copy the thumb content
                thumb_filename= '%s.png' % name
                thumb_file = tmpdir.open(thumb_filename)
                try:
                    thumb_data = thumb_file.read()
                finally:
                    thumb_file.close()
                # Need to add the PNG to ikaaro

                # Return a FLV file and a PNG thumbnail
                mp4file = [name, 'video/%s' % EXTENSION,
                            video_data, EXTENSION, width, height]
                mp4thumb = ['%s_thumb' % name, 'image/png', thumb_data, 'png']

                if((len(video_data) == 0) or (len(thumb_data) == 0)):
                     #exit
                    encoded = None
                else:
                    encoded = {'videoFile':mp4file, 'videoThumb':mp4thumb}

                tmpfile.close()
                ########
                # Encoded
                if encoded:
                    vidfilename, vidmimetype, vidbody, vidextension, \
                            width, height = encoded['videoFile']
                    ratio = float(width)/float(height)
                    thumbfilename, thumbmimetype, \
                            thumbbody, thumbextension = encoded['videoThumb']
                    # Create the video resources
                    resource = container.get_resource(vidfilename)
                    handler = resource.get_handler()
                    handler.set_data(vidbody)

                    metadata = resource.metadata

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
                    encoded = Property(True)
                    metadata.set_property('encoded', encoded)

                    update_database(context, database, resource)
                    #context.git_message = "Encoded video: %s" % vidfilename
                    #database.save_changes()

                    # Create the thumbnail PNG resources
                    resource = container.get_resource(thumbfilename)
                    handler = resource.get_handler()
                    handler.set_data(thumbbody)

                    is_thumb = Property(True)
                    resource.metadata.set_property('is_thumb', is_thumb)

                    update_database(context, database, resource)
                    #context.git_message = "Add thumbnail for: %s" % thumbfilename
                    context.git_message = "Add encoded video, with is thumbnail: %s" % vidfilename
                    database.save_changes()
                else:
                    print("Not encoded! This should never append!")
                    # Encoding process is finished
        # ffmpeg_worker can now be reseted
        self.ffmpeg_worker['worker'] = False
        self.ffmpeg_worker['pass'] = False
        # Clean the temporary folder
        print("Delete '%s'" % tmp_folder)
        vfs.remove(tmp_folder)

    encoding.remove('lock')
    return False
