from odoo import models, fields


class BSSprint(models.Model):
    _name = "bs.sprint"
    _description = "Business Sense Sprint"
    _order = "start_date desc, id desc"

    name = fields.Char(
        string="Sprint Name",
        required=True,
    )

    start_date = fields.Date(
        string="Start Date",
    )

    end_date = fields.Date(
        string="End Date",
    )

    goal = fields.Text(
        string="Goal",
    )

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("planning", "Planning"),
            ("active", "Active"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    sprint_item_ids = fields.One2many(
    "bs.sprint.item",
    "sprint_id",
    string="Sprint Items",
    )