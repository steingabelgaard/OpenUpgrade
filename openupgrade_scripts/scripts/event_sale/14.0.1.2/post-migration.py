from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "event_sale", "14.0.1.2/noupdate_changes.xml")
    # This event type is in use. Issue#48803
    # openupgrade.delete_records_safely_by_xml_id(
    #    env, [("event_sale.event_type_data_sale")]
    # )
