# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('website_project_timesheet.portal_task_timesheet_rule',
     'hr_timesheet.timesheet_rule_portal'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'hr_timesheet', ['group_hr_timesheet_user'], True)
