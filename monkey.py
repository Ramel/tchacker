# -*- coding: UTF-8 -*-
# Copyright (C) 2011 Henry Obein <henry@itaapy.com>
# Copyright (C) 2011 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2011 Armel FORTUN <armel@tchack.com>
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

from itools.core import freeze, merge_dicts
from itools.datatypes import Integer, Boolean, Decimal
from itools.database import register_field

from ikaaro.file import Image, Video

Image.class_schema = freeze(merge_dicts(
        Image.class_schema,
        has_thumb=Boolean(source='metadata', indexed=True),
        need_thumb=Boolean(source='metadata', indexed=True),
        is_thumb=Boolean(source='metadata')))


Video.class_schema = freeze(merge_dicts(
        Video.class_schema,
        has_thumb=Boolean(source='metadata'),
        width=Integer(source='metadata'),
        height=Integer(source='metadata'),
        ratio=Decimal(source='metadata')))


# Remove "is_thumb" from indexation
def is_image_content(self):
    try:
        if self.metadata.get_property("is_thumb"):
            return False
    except AttributeError:
        pass
    return super(Image, self).is_content


Image.is_content = property(is_image_content)

register_field('has_thumb', Boolean(indexed=True))
register_field('need_thumb', Boolean(indexed=True))

def run_cron(self):
    cron(self._make_image_thumbnails, timedelta(seconds=1))

def _make_image_thumbnails(self):
    database = self.database

    # Build fake context
    context = get_fake_context()
    context.server = self
    context.database = self.database
    context.root = self.root
    context.site_root = self.root

    # Build fake context
    #context = get_fake_context()
    print("context = %s" % context)
    #database = context.database
    #context.server = self
    #context.database = self.database
    #context.root = self.root
    #context.site_root = self.root
    #context.init_context()
    #root = get_root(database)

    # Go
    #from datetime import datetime
    #t = context.fix_tzinfo(datetime.now())
    q1 = PhraseQuery('has_thumb', False)
    #query = PhraseQuery('is_image', True)
    #q2 = PhraseQuery('is_image', True)
    q2 = PhraseQuery('need_thumb', True)
    #q3 = PhraseQuery('is_image', True)
    #query = AndQuery(q1, q2)
    query = AndQuery(q1,q2)
    #for brain in self.root.search(query).get_documents():
    for brain in self.root.search(query).get_documents():
        print("brain = %s" % brain.name)
    #database = self.database
    # Build fake context
    #context = get_fake_context()
    #database = context.database
    """
    # Get last_attachment
    last_attachment = self.get_property('last_attachment')
    fs = self.metadata.database.fs
    image = self.get_resource(last_attachment)
    print("image.name = %s" % image.name)
    name = image.name
    dirname = mkdtemp('makethumbs', 'ikaaro')
    tempdir = vfs.open(dirname)
    # Paste the file in the tempdir
    tmpfolder = "%s" % (dirname)
    tmp_uri = "%s%s%s" % (tmpfolder, sep, name)
    tmpfile = open("%s" % tmp_uri, "w+")
    # Here we need to open the file in the database
    tmpfile.write(image.get_handler().data)
    tmpfile.close()

    low = 256, 256
    med = 800, 800
    hig = 1024, 1024

    # Create the thumbnail PNG resources
    thumbext = (["_HIG", hig], ["_MED", med], ["_LOW", low])

    uri = tmpfolder + sep

    for te in thumbext:
        try:
            im = PILImage.open(str(tmp_uri))
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
    # Now we need to update the has_thumb property in the file metadata
    has_thumb = Property(True)
    image.set_property('has_thumb', has_thumb)
    # Clean the temporary folder
    #vfs.remove(dirname)
    """
    return 60

from ikaaro.server import Server
Server.run_cron = run_cron
