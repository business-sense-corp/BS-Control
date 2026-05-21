from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    x_client_status = fields.Selection(
        selection=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("potential", "Potential"),
            ("on_hold", "On Hold"),
        ],
        string="Client Status",
        default="potential",
        tracking=True,
    )

    x_industry = fields.Char(
        string="Industry",
        tracking=True,
    )

    x_client_type = fields.Selection(
        selection=[
            ("customer", "Customer"),
            ("lead", "Lead"),
            ("vendor", "Vendor"),
            ("partner", "Partner"),
            ("internal", "Internal"),
        ],
        string="Client Type",
        default="customer",
        tracking=True,
    )

    x_notes = fields.Text(
        string="Notes",
    )