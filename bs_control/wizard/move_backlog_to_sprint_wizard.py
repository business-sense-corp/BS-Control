from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BSMoveBacklogToSprintWizard(models.TransientModel):
    _name = "bs.move.backlog.to.sprint.wizard"
    _description = "Move Backlog Item To Sprint"

    backlog_item_id = fields.Many2one(
        "bs.backlog.item",
        string="Backlog Item",
        required=True,
        readonly=True,
    )

    sprint_id = fields.Many2one(
        "bs.sprint",
        string="Sprint",
        required=True,
        domain=[("status", "not in", ["closed", "cancelled"])],
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        related="backlog_item_id.project_id",
        readonly=True,
    )

    assigned_user_id = fields.Many2one(
        "res.users",
        string="Assigned User",
    )

    estimated_hours = fields.Float(
        string="Estimated Hours",
    )

    priority = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Priority",
        default="medium",
    )

    start_date = fields.Date(
        string="Start Date",
    )

    end_date = fields.Date(
        string="End Date",
    )

    set_backlog_as_planned = fields.Boolean(
        string="Set Backlog As Planned",
        default=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")

        if active_model == "bs.backlog.item" and active_id:
            backlog_item = self.env["bs.backlog.item"].browse(active_id)

            res.update({
                "backlog_item_id": backlog_item.id,
                "assigned_user_id": backlog_item.assigned_user_id.id,
                "estimated_hours": backlog_item.estimated_hours,
                "priority": backlog_item.priority,
                "end_date": backlog_item.due_date,
            })

        return res

    def action_move_to_sprint(self):
        self.ensure_one()

        if not self.backlog_item_id:
            raise ValidationError(_("Please select a Backlog Item."))

        if not self.sprint_id:
            raise ValidationError(_("Please select a Sprint."))

        if self.sprint_id.status in ["closed", "cancelled"]:
            raise ValidationError(
                _("You cannot move tasks to a closed or cancelled sprint.")
            )

        existing_item = self.env["bs.sprint.item"].search([
            ("sprint_id", "=", self.sprint_id.id),
            ("backlog_item_id", "=", self.backlog_item_id.id),
        ], limit=1)

        if existing_item:
            raise ValidationError(
                _("This Backlog Item is already added to this Sprint.")
            )

        sprint_item = self.env["bs.sprint.item"].create({
            "name": self.backlog_item_id.name,
            "sprint_id": self.sprint_id.id,
            "backlog_item_id": self.backlog_item_id.id,
            "project_id": self.backlog_item_id.project_id.id,
            "assigned_user_id": self.assigned_user_id.id,
            "estimated_hours": self.estimated_hours,
            "priority": self.priority,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": "todo",
        })

        if self.set_backlog_as_planned:
            lifecycle_state = "active_sprint" if self.sprint_id.status == "active" else "planned"

            self.backlog_item_id.write({
                "lifecycle_state": lifecycle_state,
            })

        return {
            "type": "ir.actions.act_window",
            "name": _("Sprint Item"),
            "res_model": "bs.sprint.item",
            "res_id": sprint_item.id,
            "view_mode": "form",
            "target": "current",
        }