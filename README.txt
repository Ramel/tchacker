Tchacker is a module for the Ikaaro CMS.

It's an Issue tracker based on the Ikaaro's one, which been removed from it.

Requirements
============

Software      Version  Used by            Home
----------    -------  ----------------   --------------------------------------
itools        0.75    Ikaaro              https://www.github.com/hforge/itools
ikaaro        0.75    Tchacker            https://www.github.com/hforge/ikaaro
videoencoding 0.75    Tchacker            https://www.github/Ramel/videoencoding
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
