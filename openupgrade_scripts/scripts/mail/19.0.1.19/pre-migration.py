
from openupgradelib import openupgrade

def migrate(env, version):
    """ Remove activity calendar view from mail_activity_board to avoid
        duplication error """
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "mail_activity_board.mail_activity_action_my_view_calendar",
        ],
    )
