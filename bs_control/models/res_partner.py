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

    x_industry = fields.Selection(
        selection=[
            ("agriculture", "Agriculture"),
            ("automotive", "Automotive"),
            ("banking", "Banking"),
            ("construction", "Construction"),
            ("consulting", "Consulting"),
            ("education", "Education"),
            ("energy", "Energy"),
            ("engineering", "Engineering"),
            ("facility_management", "Facility Management"),
            ("finance", "Finance"),
            ("food_beverage", "Food & Beverage"),
            ("government", "Government"),
            ("healthcare", "Healthcare"),
            ("hospitality", "Hospitality"),
            ("insurance", "Insurance"),
            ("legal", "Legal"),
            ("logistics", "Logistics"),
            ("manufacturing", "Manufacturing"),
            ("marketing", "Marketing"),
            ("media", "Media"),
            ("ngo", "NGO"),
            ("oil_gas", "Oil & Gas"),
            ("pharmaceutical", "Pharmaceutical"),
            ("real_estate", "Real Estate"),
            ("retail", "Retail"),
            ("security", "Security"),
            ("technology", "Technology"),
            ("telecommunication", "Telecommunication"),
            ("tourism", "Tourism"),
            ("transportation", "Transportation"),
            ("wholesale", "Wholesale"),
            ("other", "Other"),
        ],
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