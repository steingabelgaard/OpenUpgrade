from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr, "slide_channel", "description", "description"
    )
    openupgrade.convert_field_to_html(
        env.cr, "slide_channel", "description_short", "description_short"
    )
    openupgrade.convert_field_to_html(
        env.cr, "slide_slide", "description", "description"
    )
    env.ref('website_slides.res_partner_view_form').groups_id = False
