# -*- coding: UTF-8 -*-
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

# Import from the Standard Library
from datetime import timedelta
from cStringIO import StringIO

# Import from itools
from itools.fs import vfs
from itools.loop import cron
from itools.database import PhraseQuery, AndQuery
from itools.csv import Property

# Import from ikaaro
from ikaaro.server import get_fake_context
from ikaaro.registry import get_resource_class

# Import from PIL
from PIL import Image as PILImage

from monkey import Image

def run_cron(self):
    print("cron started!")
    #cron(self._make_image_thumbnails, timedelta(seconds=1), timedelta(seconds=10))
    cron(self._make_image_thumbnails, timedelta(seconds=1))


def make_thumbnails(self):
    self.run_cron()


def _make_image_thumbnails(self):
    database = self.database

    # Build fake context
    context = get_fake_context()
    context.server = self
    context.database = self.database
    context.root = self.root
    context.site_root = self.root

    # Search for images without thumbnails
    q1 = PhraseQuery('has_thumb', False)
    q2 = PhraseQuery('need_thumb', True)
    q3 = PhraseQuery('is_image', True)
    query = AndQuery(q1, q2, q3)

    for image in self.root.search(query).get_documents():
        abspath = image.abspath
        # Get the resource
        resource = context.root.get_resource(abspath)
        container = resource.parent
        abspath = container.abspath
        name = image.name
        print("image.name = %s" % name)
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
            try:
                imageThumb = container.make_resource(
                        ima, Image,
                        body=thumb_data,
                        filename=thumb_filename,
                        extension='jpg',
                        format=format
                        )
                imageThumb.init_resource()
            except Exception:
                print("Error creating image")
            is_thumb = Property(True)
            imageThumb.set_property('is_thumb', is_thumb)
            try:
                context.set_mtime = True
                # Reindex resource without committing
                catalog = database.catalog
                catalog.unindex_document(str(imageThumb.abspath))
                catalog.index_document(imageThumb.get_catalog_values())
                catalog.save_changes()
            except Exception as e:
                print('CRON ERROR COMMIT CATALOG')
                print("%s" % e)
        # Now we need to update the has_thumb property in the file metadata
        has_thumb = Property(True)
        resource.metadata.set_property('has_thumb', has_thumb)
        need_thumb = Property(False)
        resource.metadata.set_property('need_thumb', need_thumb)
        # Save changes
        context.git_message = "Add thumbnails for: %s" % image.abspath
        database.save_changes()
    return False
