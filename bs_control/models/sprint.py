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
            ("closed", "Done"),
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

    @api.onchange("start_date", "end_date")
    def _onchange_sprint_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                rec.end_date = False
                return {
                    "warning": {
                        "title": _("Invalid Sprint Dates"),
                        "message": _("End Date cannot be earlier than Start Date."),
                    }
                }

    @api.constrains("start_date", "end_date")
    def _check_sprint_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError(
                    _("End Date cannot be earlier than Start Date.")
                )

    def _is_locked_for_item_changes(self):
        self.ensure_one()
        return self.status in ["active", "closed", "cancelled"]

    def _check_sprint_item_changes_allowed(self):
        for rec in self:
            if rec._is_locked_for_item_changes():
                raise ValidationError(
                    _(
                        "You cannot add, remove, or edit Sprint Items because this Sprint has already started."
                    )
                )

    def write(self, vals):
        if "sprint_item_ids" in vals:
            self._check_sprint_item_changes_allowed()

        return super().write(vals)

    def _check_sprint(self):
        for rec in self:
            if rec.status == "active":
                raise ValidationError(
                    _("لا يمكنك إضافة مهمات عمل إلى الاسبرينت في هذه الحالة")
                )