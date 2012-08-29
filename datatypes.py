# -*- coding: UTF-8 -*-
# Copyright (C) 2008 David Versmisse <david.versmisse@itaapy.com>
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
from itools.core import thingy_property
from itools.datatypes import Enumerate, Unicode
from itools.datatypes import Unicode, Integer
from itools.web import get_context

# Import from ikaaro
from ikaaro.datatypes import FileDataType
from ikaaro.cc import UsersList



class Tchacker_UsersList(UsersList):

    @thingy_property
    def included_roles(self):
        return self.resource.get_property('included_roles')



class TchackerList(Enumerate):

    @staticmethod
    def decode(value):
        if not value:
            return None
        return int(value)


    @staticmethod
    def encode(value):
        if value is None:
            return ''
        return str(value)


    def get_options(cls):
        elements = cls.tchacker.get_resource(cls.element).handler
        return [{'name': record.id,
                 'value': elements.get_record_value(record, 'title')}
                for record in elements.get_records_in_order()]



class ProductInfoList(Enumerate):

    @staticmethod
    def decode(value):
        if not value:
            return None
        return int(value)


    @staticmethod
    def encode(value):
        if value is None:
            return ''
        return str(value)


    def get_options(cls):
        tchacker = cls.tchacker
        products = tchacker.get_resource('product').handler
        elements = tchacker.get_resource(cls.element).handler

        options = []
        for record in elements.get_records_in_order():
            title = elements.get_record_value(record, 'title')
            product_id = elements.get_record_value(record, 'product')

            # Product title
            if product_id is None:
                continue
            product_id = int(product_id)
            product_record = products.get_record(product_id)
            product_title = products.get_record_value(product_record, 'title')

            options.append({'name': record.id,
                            'value': '%s - %s' % (product_title, title)})
        return options


    def is_valid(cls, name):
        # Get the product number
        product =  get_context().get_form_value('product')
        if product is None:
            return True
        product = int(product)

        # Match our choice ?
        choice = int(name)
        elements = cls.tchacker.get_resource(cls.element).handler
        record = elements.get_record(choice)
        product_id = int(elements.get_record_value(record, 'product'))

        return product_id == product



def get_issue_fields(tchacker):
    return {
            'title': Unicode(mandatory=True),
            'product': TchackerList(element='product', tchacker=tchacker,
                                    mandatory=True),
            'module': ProductInfoList(element='module', tchacker=tchacker),
            'version': ProductInfoList(element='version', tchacker=tchacker),
            'type': TchackerList(element='type', tchacker=tchacker, mandatory=True),
            'state': TchackerList(element='state', tchacker=tchacker, mandatory=True),
            'priority': TchackerList(element='priority', tchacker=tchacker),
            'assigned_to': Tchacker_UsersList(resource=tchacker),
            'cc_list': Tchacker_UsersList(resource=tchacker, multiple=True),
            'comment': Unicode,
            'attachment': FileDataType,
            'ids': Integer}
