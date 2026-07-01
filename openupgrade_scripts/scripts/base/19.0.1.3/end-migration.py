# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade



def _ir_actions_server_child_ids(env):
    """
    Field was changed from m2m to o2m - set parent_id from m2m table,
    duplicate child actions that had multiple parents
    """
    env.cr.execute(
        """
        SELECT action_id, array_agg(server_id)
        FROM rel_server_actions GROUP BY action_id
        """
    )
    for action_id, parent_ids in env.cr.fetchall():
        action = env["ir.actions.server"].browse(action_id)
        parents = env["ir.actions.server"].browse(parent_ids)
        action.parent_id = parents[0]
        for parent in parents[1:]:
            action.copy({"name": action.name, "parent_id": parent.id})

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.disable_invalid_filters(env)
    _ir_actions_server_child_ids(env)
