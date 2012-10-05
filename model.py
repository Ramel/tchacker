# -*- coding: UTF-8 -*-

from itools.gettext import MSG
from ikaaro.config_models import Model
from issue import Issue


class IssueModel(Model):

    class_id = 'tchacker-issue-model'
    class_title = MSG(u'Issue model')

    base_class = Issue
