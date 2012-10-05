# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
# Copyright (C) 2007-2008 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Nicolas Deram <nicolas@itaapy.com>
# Copyright (C) 2007-2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
# Copyright (C) 2009 Armel FORTUN <armel@tchack.com>
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
from itools.csv import Property
from itools.datatypes import Unicode, XMLContent
from itools.gettext import MSG
from itools.web import get_context, BaseView, STLView
from itools.xml import XMLParser

# Import from ikaaro
from ikaaro.autoadd import AutoAdd
from ikaaro.autoedit import AutoEdit
from ikaaro.fields import Textarea_Field, File_Field
from ikaaro.messages import MSG_CHANGES_SAVED
from ikaaro.views import ContextMenu
from ikaaro.widgets import Widget
from ikaaro.utils import make_stl_template

# Import from tchacker
from datatypes import get_issue_fields
from comments import TchackerCommentsView
#from issue import Issue


def check_properties_differencies(prop1, prop2):
    "Check for differences of properties values"
    if type(prop1) in (Property, list):
        return prop1 != prop2
    elif prop1 is None:
        return prop2 is not None
    else:
        raise TypeError('This method wait for Property, or list of Property')



###########################################################################
# Widgets
###########################################################################
class ProductsSelectWidget(Widget):

    template = make_stl_template("""
    <script type="text/javascript">
    var list_products = {<stl:inline stl:repeat="product products">
        "${product/id}":
            {'module':
                [<stl:inline stl:repeat="module product/modules">
                    {"id": "${module/id}", "value": "${module/value}"},
                </stl:inline>],
                'version':
                [<stl:inline stl:repeat="version product/versions">
                    {"id": "${version/id}", "value": "${version/value}"},
                </stl:inline>]}
            ,</stl:inline>
        }
    function update_tracker(){
      update_tracker_list('version');
      update_tracker_list('module');
    }
    </script>
    <select id="${id}" name="${name}" multiple="${multiple}" size="${size}"
      class="${css}">
      <option value="" stl:if="has_empty_option"></option>
      <option stl:repeat="option options" value="${option/name}"
        selected="${option/selected}">${option/value}</option>
    </select>""")


    css = None
    has_empty_option = True
    size = None


    def multiple(self):
        #print("multiple = %s" % self.datatype.multiple)
        return self.datatype.multiple


    def products(self):
        context = get_context()
        if context is None:
            return
        resource = context.resource
        #XXX Issue?
        """
        if isinstance(resource, issue.Issue):
            tracker = resource.parent
        else:
            tracker = context.resource
        """
        tracker = context.resource
        return tracker.get_list_products_namespace()

    def options(self):
        value = self.value
        print("self.datatype.get_namespace(value) = %s" %
                    self.datatype.get_namespace(value))
        print("value = %s" % value)
        # Check whether the value is already a list of options
        # FIXME This is done to avoid a bug when using a select widget in an
        # auto-form, where the 'datatype.get_namespace' method is called
        # twice (there may be a better way of handling this).
        if type(value) is not list:
            return self.datatype.get_namespace(value)
        return value


###########################################################################
# Menu
###########################################################################
class IssueTchackerMenu(ContextMenu):

    title = MSG(u'Tchacker')

    def get_items(self):
        path = self.context.get_link(self.resource.parent)
        return [
            {'title': MSG(u'Search for issues'), 'href': '%s/;search' % path},
            {'title': MSG(u'Add a new issue'), 'href': '%s/;add_issue' % path}]



###########################################################################
# Views
###########################################################################
class Issue_DownloadAttachments(BaseView):

    access = 'is_allowed_to_edit'

    def GET(self, resource, context):
        names = resource.get_property('attachment')
        data = resource.export_zip(names)
        # Content-Type & Content-Disposition
        context.set_content_type('application/zip')
        filename = '%s-attachments.zip' % resource.name
        context.set_content_disposition('inline', filename)
        # Ok
        return data



class Issue_NewInstance(AutoAdd):

    automatic_resource_name = True

    fields = ['title', 'assigned_to', 'product', 'type', 'cc_list', 'module',
              'version', 'state', 'priority', 'comment', 'attachment']

    comment = Textarea_Field(title=MSG(u'Comment'))
    #attachment = File_Field(title=MSG(u'Attachment'))

    def make_new_resource(self, resource, context, form):
        proxy = super(Issue_NewInstance, self)
        new_issue = proxy.make_new_resource(resource, context, form)
        
        new_issue.add_comment(context, form, new=True)
        
        return new_issue
    
    def get_field(self, name):
        field = super(Issue_NewInstance, self).get_field(name)
        print("name = %s" % name)
        if (name == 'title' or name == 'product' or
            name == 'comment' or name == 'state' or name == 'type'):
            return field(required=True)
        return field

#    access = 'is_allowed_to_edit'
#    title = MSG(u'Add')
#    icon = 'new.png'
#    #template = '/ui/tchacker/add_issue.xml'
#    styles = ['/ui/tchacker/style.css']
#    scripts = ['/ui/tchacker/tchacker.js']
#    form_id = "tchacker-add-issue"
#    method = 'post'
#
#    widgets = freeze([
#        TextWidget('title', title=MSG(u'Title:')),
#        SelectWidget('assigned_to', title=MSG(u'Assigned To:')),
#        ProductsSelectWidget('product', title=MSG(u'Product:')),
#        SelectWidget('type', title=MSG(u'Type:')),
#        SelectWidget('cc_list', title=MSG(u'CC:')),
#        SelectWidget('module', title=MSG(u'Module:')),
#        SelectWidget('version', title=MSG(u'Version:')),
#        SelectWidget('state', title=MSG(u'State:')),
#        SelectWidget('priority', title=MSG(u'Priority:')),
#        MultilineWidget('comment', title=MSG(u'New Comment:')),
#        FileWidget('attachment', title=MSG(u'Attachment:')),
#        ProgressBarWidget()
#        ])
#
#
#    def get_schema(self, resource, context):
#        schema = get_issue_fields(resource)
#        comment = context.get_form_value('comment')
#        attachment = context.get_form_value('attachment')
#        if comment is None and attachment is True:
#            schema['comment'] = Unicode(mandatory=False)
#        if (comment is None or comment == '') and attachment is None:
#            schema['comment'] = Unicode(mandatory=True)
#        return schema
#
#
#    def get_value(self, resource, context, name, datatype):
#        if getattr(datatype, 'mandatory', False):
#            datatype = datatype(mandatory=False)
#        value = context.get_form_value(name, datatype)
#        if value is None:
#            value = datatype.get_default()
#            return value
#        if issubclass(datatype, Enumerate):
#            value = datatype.get_namespace(value)
#        # By default, set cc_list to the current user
#        if name == 'cc_list' and not value:
#            return [context.user.name]
#        return value
#
#
#    def get_namespace(self, resource, context):
#        proxy = super(Tchacker_AddIssue, self)
#        namespace = proxy.get_namespace(resource, context)
#        fields = self.get_schema(resource, context)
#        namespace['list_products'] = resource.get_list_products_namespace()
#        #print("namespace = %s" % namespace['fields']['comment'])
#        #for x in namespace['fields']['comment']:
#        #    print x
#        """
#        if(namespace['comment']['error'] is not None):
#            namespace['comment']['error'] = MSG(
#                u'This field is required (or can be emtpy if an attachment is joined)')
#        """
#        return namespace
#
#
#    def action(self, resource, context, form):
#        comment = form['comment']
#        attachment = form['attachment']
#        if comment == '' and attachment is not None:
#            form['comment'] = "comment_is_empty_but_has_attachment"
#
#        # Add
#        id = resource.get_new_id()
#        issue_cls = resource.issue_class
#        issue = resource.make_resource(id, issue_cls)
#        issue.add_comment(context, form, new=True)
#
#        # Ok
#        message = INFO(u'New issue added.')
#        goto = './%s/' % id
#        return context.come_back(message, goto=goto)



class Issue_Edit(AutoEdit):

    title = MSG(u'Edit Issue')
    fields = ['title', 'assigned_to', 'product', 'type', 'cc_list', 'module',
              'version', 'state', 'priority', 'comment', 'attachment']
    """
    def get_field(self, resource, name):
        field = super(Issue_Edit, self).get_field(resource, name)
        if (name == 'title' or name == 'product' or
            name == 'comment' or name == 'state' or name == 'type'):
            return field(required=True)
        return field
    """
#   template = '/ui/tchacker/edit_issue.xml'
#   styles = ['/ui/tchacker/style.css', '/ui/thickbox/style.css']
#   scripts = ['/ui/tchacker/tchacker.js', '/ui/thickbox/thickbox.js',
#              '/ui/flowplayer/flowplayer-3.2.2.min.js']


#   def get_schema(self, resource, context):
#       tchacker = resource.parent
#       return get_issue_fields(tchacker)


#   def get_value(self, resource, context, name, datatype):
#       if name in ('comment'):
#           return datatype.get_default()
#       return resource.get_property(name)


#   def get_namespace(self, resource, context):
#       namespace = STLView.get_namespace(self, resource, context)

#       tracker = resource.parent
#       namespace['list_products'] = tracker.get_list_products_namespace()

#       # Local variables
#       root = context.root

#       # Comments
#       namespace['comments'] = TchackerCommentsView().GET(resource, context)

#       # cc_list
#       cc_list = resource.get_property('cc_list')
#       cc_list_userslist = self.get_schema(resource, context)['cc_list']
#       cc = []
#       nocc = []
#       for user in cc_list_userslist.get_options():
#           if user['name'] in cc_list:
#               cc.append(user)
#           else:
#               nocc.append(user)
#       namespace['cc'] = cc
#       namespace['nocc'] = nocc

#       # Reported by
#       reported_by = resource.get_reported_by()
#       namespace['reported_by'] = root.get_user_title(reported_by)

#       # Attachments
#       links = []
#       get_user = root.get_user_title
#       for attachment_name in resource.get_property('attachment'):
#           attachment = resource.get_resource(attachment_name, soft=True)
#           missing = (attachment is None)
#           author = mtime = None
#           if missing is False:
#               mtime = attachment.get_property('mtime')
#               mtime = context.format_datetime(mtime)
#               author = get_user(attachment.get_property('last_author'))

#           links.append({
#               'author': author,
#               'missing': missing,
#               'mtime': mtime,
#               'name': attachment_name})

#       namespace['attachments'] = links

#       namespace['which_module'] = None #resource.get_property('module')
#       for module in namespace['module']['value']:
#           if module['selected'] == True in module.values():
#               #print "module['selected'] = %s " % module #['value'][module]['value']
#               namespace['which_module'] = module['value']

#       return namespace


#   def action(self, resource, context, form):
#       # Edit
#       resource.add_comment(context, form)
#       # Change
#       context.database.change_resource(resource)
#       context.message = MSG_CHANGES_SAVED



class Issue_History(STLView):

    access = 'is_allowed_to_view'
    title = MSG(u'History')
    icon = 'history.png'
    template = '/ui/tchacker/issue_history.xml'
    styles = ['/ui/tchacker/style.css']


    def get_namespace(self, resource, context):
        # Local variables
        users = resource.get_resource('/users')
        tracker = resource.parent
        versions = tracker.get_resource('version').handler
        types = tracker.get_resource('type').handler
        states = tracker.get_resource('state').handler
        products = tracker.get_resource('product').handler
        modules = tracker.get_resource('module').handler
        priorities = tracker.get_resource('priority').handler
        # Initial values
        previous_title = None
        previous_version = None
        previous_type = None
        previous_state = None
        previous_module = None
        previous_priority = None
        previous_assigned_to = None
        previous_cc_list = None
        previous_product = None
        previous_attachment = None

        # Build the namespace
        rows = []
        i = 0
        for metadata in resource.get_history():
            # Skip old data (before 0.62) FIXME
            mtime = metadata.get_property('mtime')
            if mtime is None:
                continue

            username = metadata.get_property('last_author').value
            title = metadata.get_property('title')
            module = metadata.get_property('module')
            version = metadata.get_property('version')
            type_prop = metadata.get_property('type')
            priority = metadata.get_property('priority')
            assigned_to = metadata.get_property('assigned_to')
            state = metadata.get_property('state')
            comments = metadata.get_property('comment')
            cc_list = metadata.get_property('cc_list')
            product = metadata.get_property('product')
            attachment = metadata.get_property('attachment')

            # Solid in case the user has been removed
            user = users.get_resource(username, soft=True)
            usertitle = user and user.get_title() or username

            if comments and comments[-1].get_parameter('date') == mtime.value:
                comment = comments[-1].value
                comment = XMLContent.encode(Unicode.encode(comment))
                comment = XMLParser(comment.replace('\n', '<br />'))
            else:
                comment = None
            i += 1
            row_ns = {'number': i,
                      'user': usertitle,
                      'datetime': context.format_datetime(mtime.value),
                      'title': None,
                      'version': None,
                      'type': None,
                      'state': None,
                      'module': None,
                      'priority': None,
                      'assigned_to': None,
                      'comment': comment,
                      'cc_list': None,
                      'product': None,
                      'attachment': None}
            if check_properties_differencies(title, previous_title):
                previous_title = title
                row_ns['title'] = title.value
            if check_properties_differencies(version, previous_version):
                previous_version = version
                row_ns['version'] = ' '
                if version is not None:
                    version = versions.get_record(int(version.value))
                    if version:
                        value = versions.get_record_value(version, 'title')
                        row_ns['version'] = value
            if check_properties_differencies(type_prop, previous_type):
                previous_type = type_prop
                row_ns['type'] = ' '
                if type_prop is not None:
                    type_prop = types.get_record(int(type_prop.value))
                    if type_prop is not None:
                        value = types.get_record_value(type_prop, 'title')
                        row_ns['type'] = value
            if check_properties_differencies(state, previous_state):
                previous_state = state
                row_ns['state'] = ' '
                if state is not None:
                    state = states.get_record(int(state.value))
                    if state is not None:
                        value = states.get_record_value(state, 'title')
                        row_ns['state'] = value
            if check_properties_differencies(module, previous_module):
                previous_module = module
                row_ns['module'] = ' '
                if module is not None:
                    module = modules.get_record(int(module.value))
                    if module is not None:
                        value = modules.get_record_value(module, 'title')
                        row_ns['module'] = value
            if check_properties_differencies(priority, previous_priority):
                previous_priority = priority
                row_ns['priority'] = ' '
                if priority is not None:
                    priority = priorities.get_record(int(priority.value))
                    if priority is not None:
                        value = priorities.get_record_value(priority, 'title')
                        row_ns['priority'] = value
            if check_properties_differencies(assigned_to, previous_assigned_to):
                previous_assigned_to = assigned_to
                row_ns['assigned_to'] = ' '
                if assigned_to and len(assigned_to.value):
                    assigned_to_user = users.get_resource(assigned_to.value, soft=True)
                    if assigned_to_user is not None:
                        row_ns['assigned_to'] = assigned_to_user.get_title()
            if check_properties_differencies(cc_list, previous_cc_list):
                root = context.root
                previous_cc_list = cc_list
                new_values = []
                for cc in cc_list.value:
                    user = root.get_user(cc)
                    if user:
                        new_values.append(user.get_property('email'))
                if new_values:
                    row_ns['cc_list'] = u', '.join(new_values)
                else:
                    row_ns['cc_list'] = ' '
            if check_properties_differencies(product, previous_product):
                previous_product = product
                row_ns['product'] = ' '
                if product is not None:
                    product = products.get_record(int(product.value))
                    if product is not None:
                        value = products.get_record_value(product, 'title')
                        row_ns['product'] = value
            if check_properties_differencies(attachment, previous_attachment):
                previous_attachment= attachment
                row_ns['attachment'] = attachment[-1].value

            rows.append(row_ns)
            # Avoid attachment repetition for next comment
            attachment = None

        rows.reverse()

        # Ok
        return {'number': resource.name, 'rows': rows}
