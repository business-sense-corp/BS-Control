from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


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

    def _check_sprint(self):
        for rec in self:
            if rec.status == 'active':
                raise ValidationError(_('لا يمكنك إضافة مهمات عمل إلى الاسبرينت في هذه الحالة'))