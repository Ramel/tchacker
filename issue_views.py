# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2007-2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
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
from itools.core import freeze

# Import from ikaaro
from ikaaro.tracker.issue_views import Issue_Edit_AutoForm
from ikaaro.tracker.issue_views import Issue_Edit_ProxyView
from ikaaro.tracker.issue_views import ProductsSelectWidget
from ikaaro.autoform import TextWidget, SelectWidget
from ikaaro.autoform import XHTMLBody

# Import from tchacker
from datatypes import get_issue_fields
from comments import Tchack_CommentsView
from widgets import FileAndSketchTabbedWidget
from widgets import Tchack_ProgressBarWidget
from widgets import Tchack_MultilineWidget
from widgets import OnSubmitButton


class Tchack_Issue_Edit_AutoForm(Issue_Edit_AutoForm):

    template = '/ui/tchacker/tchacker_issue_autoform.xml'
    actions = [OnSubmitButton(access=True, css='button-ok',
                    onclick='updateDrawing()',
                    title=MSG(u'Send the answer'))]
    styles = [
                '/ui/tchacker/jquery-ui-1.8.5/themes/base/jquery.ui.all.css',
                '/ui/tchacker/style.css',
                '/ui/tchacker/progressbar.css',
                '/ui/thickbox/style.css']
    scripts = ['/ui/tchacker/tracker.js',
                '/ui/thickbox/thickbox.js',
                '/ui/tchacker/jquery-ui-1.8.5/ui/minified/jquery.ui.core.min.js',
                '/ui/tchacker/jquery-ui-1.8.5/ui/minified/jquery.ui.widget.min.js',
                '/ui/tchacker/jquery-ui-1.8.5/ui/minified/jquery.ui.tabs.min.js',
                '/ui/flowplayer/flowplayer-3.2.2.min.js',
                '/ui/tchacker/sketch.min.js']

    description = XHTMLBody.decode('<a href="#" class="showall">Show/Hide options</a>')

    widgets = freeze([
        TextWidget('title', title=MSG(u'Title:'),
                                classes=['left-center', 'light']),
        SelectWidget('assigned_to', title=MSG(u'Assigned To:'),
                                classes=['right', 'light']),
        ProductsSelectWidget('product', title=MSG(u'Product:'),
                                classes=['left', 'light']),
        SelectWidget('type', title=MSG(u'Type:'), classes=['center', 'light']),
        SelectWidget('cc_list', title=MSG(u'CC:'), classes=['right', 'light']),
        SelectWidget('module', title=MSG(u'Module:'), classes=['left', 'light']),
        SelectWidget('state', title=MSG(u'State:'), classes=['center']),
        SelectWidget('version', title=MSG(u'Version:'),
                                classes=['left', 'light']),
        SelectWidget('priority', title=MSG(u'Priority:'),
                                classes=['center', 'light']),
        Tchack_MultilineWidget('comment', title=MSG(u'New Comment:'),
                                target="new_comment",
                                classes=['all']),
        FileAndSketchTabbedWidget(classes=['all']),
        Tchack_ProgressBarWidget()
        ])

    def get_schema(self, resource, context):
        tracker = resource.parent
        return get_issue_fields(tracker)

    def get_value(self, resource, context, name, datatype):
        if name == 'cc_list':
            assigned_to = resource.get_property('assigned_to')
            cc_list = list(resource.get_property('cc_list'))
            #print("assigned_to = %s" % assigned_to)
            #print("cc_list = %s" % cc_list)
            if assigned_to in cc_list: cc_list.remove(assigned_to)
            #print("cc_list2 = %s" % cc_list)
            return cc_list
        if name in ('comment'):
            return datatype.get_default()
        if name in ('canvasDrawing'):
            return datatype.get_default()
        return resource.get_property(name)

    def get_namespace(self, resource, context):
        proxy = super(Issue_Edit_AutoForm, self)
        namespace = proxy.get_namespace(resource, context)
        #print("namespace = %s" % namespace)
        # Comments
        namespace['comments'] = Tchack_CommentsView().GET(resource, context)
        return namespace


class Tchack_Issue_Edit_ProxyView(Issue_Edit_ProxyView):

    access = 'is_allowed_to_edit'
    title = MSG(u'Edit Issue')
    subviews = [
            Tchack_Issue_Edit_AutoForm(),
            Tchack_CommentsView()
            ]

    def get_namespace(self, resource, context):
        views = []
        views.append(Tchack_CommentsView().GET(resource, context))
        views.append(Tchack_Issue_Edit_AutoForm().GET(resource, context))
        return {'views': views}
