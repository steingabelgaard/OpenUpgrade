# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2.extensions import AsIs
from odoo.addons.openupgrade_records.lib import apriori
from openupgradelib import openupgrade


# backup of
# - datetime field because it changes to date field
column_copies = {
    'res_currency_rate': [('name', None, None)],
}
column_renames = {
    'ir_actions': [('usage', None)],
}


# rename_tables is not needed because "ir.actions.report.xml" and
# "ir.actions.report" result both in "ir_act_report_xml"
model_renames_ir_actions_report = [
    ('ir.actions.report.xml', 'ir.actions.report')
]


def handle_partner_sector(env):
    if openupgrade.table_exists(env.cr, 'res_partner_sector'):
        # Module `partner_sector` was installed in 10.0
        openupgrade.rename_models(
            env.cr, [('res.partner.sector', 'res.partner.industry')],
        )
        openupgrade.rename_tables(
            env.cr, [(('res_partner_sector', 'res_partner_industry'))]
        )
        openupgrade.rename_fields(
            env, [
                ('res.partner', 'res_partner', 'sector_id', 'industry_id'),
            ],
        )


def fill_cron_action_server_pre(env):
    """Prefill the column with a fixed value for avoiding the not null error,
    but wait until post for filling correctly the field and related record.
    """
    openupgrade.add_fields(
        env, [
            ('ir_actions_server_id', 'ir.cron', 'ir_cron', 'many2one', False,
             'base'),
        ],
    )
    env.cr.execute("SELECT MIN(id) FROM ir_act_server")
    row = env.cr.fetchone()
    server_action_id = row and row[0] or 1
    # Write in the ir.cron record the parent ir.actions.server ID
    env.cr.execute(
        "UPDATE ir_cron SET ir_actions_server_id = %s",
        (server_action_id, ),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr, apriori.renamed_modules.items()
    )
    openupgrade.update_module_names(
        env.cr, apriori.merged_modules.items(), merge_modules=True)
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_columns(env.cr, column_renames)
    openupgrade.rename_models(env.cr, model_renames_ir_actions_report)
    handle_partner_sector(env)
    env.cr.execute(
        """UPDATE ir_actions SET type = 'ir.actions.report'
        WHERE type = 'ir.actions.report.xml'""")

    rule_xml_ids = ('ir_config_parameter_rule', 'ir_values_default_rule')
    env.cr.execute(
        """ DELETE FROM ir_rule WHERE id IN (
                SELECT res_id FROM ir_model_data WHERE module = 'base'
                    AND name IN %s) """, (rule_xml_ids,))
    env.cr.execute(
        """ DELETE FROM ir_model_data WHERE module = 'base'
                AND name IN %s """, (rule_xml_ids,))

    # All existing server actions are of type server action
    env.cr.execute(
        """ ALTER TABLE ir_act_server ADD COLUMN usage VARCHAR;
        UPDATE ir_act_server SET usage = 'ir_actions_server'""")
    # For some window actions, there is a value in the old column
    # that was inherited from ir_actions before
    env.cr.execute(
        """ ALTER TABLE ir_act_window ADD COLUMN usage VARCHAR;
        UPDATE ir_act_window SET usage = %s""",
        (AsIs(openupgrade.get_legacy_name('usage')),))

    # work_days interval was removed from selection values
    env.cr.execute(
        """
        UPDATE ir_cron SET interval_type = 'days'
        WHERE interval_type = 'work_days'""")
    fill_cron_action_server_pre(env)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'base', ['lang_km'], True)
