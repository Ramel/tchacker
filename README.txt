Tchacker is a module for the Ikaaro CMS.

It's an Issue tracker based on the Ikaaro's one, which been removed from it.

Requirements
============

Software      Version  Used by            Home
----------    -------  ----------------   --------------------------------------
itools        0.62.1  Ikaaro              https://www.github.com/hforge/itools
ikaaro        0.62    Tchacker            https://www.github.com/hforge/ikaaro
videoencoding master  Tchacker            https://www.github/Ramel/videoencoding
thickbox      master  Tchacker            https://www.github/Ramel/thickbox

Check the Videoencoding module requirements.


Install
=============

If you are reading this instructions you probably have already unpacked
the ikaaro tarball with the command line:

  $ tar xzf tchacker-X.Y.Z.tar.gz

And changed the working directory this way:

  $ cd tchacker-X.Y.Z

So now to install ikaaro you just need to type this:

  $ python setup.py install

In the Ikaaro instance folder, edit the config.conf file:

  $ vim .databases/IKAARO_INSTANCE_FOLDER/config.conf

Edit the module import line:

  modules = tchacker videoencoding thickbox


Copyright
=============

Copyright (C) 2002-2012 The Ikaaro authors

Check the CREDITS.txt file for the list of authors.


License
=============

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
