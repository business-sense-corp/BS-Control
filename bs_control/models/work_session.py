from odoo import api, fields, models


class BSWorkSession(models.Model):
    _name = "bs.work.session"
    _description = "Business Sense Work Session"
    _order = "start_datetime desc, id desc"

    sprint_item_id = fields.Many2one(
        "bs.sprint.item",
        string="Sprint Item",
        required=True,
        ondelete="cascade",
    )

    sprint_id = fields.Many2one(
        "bs.sprint",
        string="Sprint",
        related="sprint_item_id.sprint_id",
        store=True,
        readonly=True,
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        related="sprint_item_id.project_id",
        store=True,
        readonly=True,
    )

    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        required=True,
    )

    start_datetime = fields.Datetime(
        string="Start Time",
        required=True,
        default=fields.Datetime.now,
    )

    end_datetime = fields.Datetime(
        string="End Time",
    )

    duration_hours = fields.Float(
        string="Duration Hours",
        compute="_compute_duration_hours",
        store=True,
    )

    state = fields.Selection(
        [
            ("running", "Running"),
            ("paused", "Paused"),
            ("done", "Done"),
        ],
        string="State",
        default="running",
        required=True,
    )

    notes = fields.Text(
        string="Notes",
    )

    @api.depends("start_datetime", "end_datetime")
    def _compute_duration_hours(self):
        for session in self:
            if session.start_datetime and session.end_datetime:
                duration = session.end_datetime - session.start_datetime
                session.duration_hours = duration.total_seconds() / 3600
            else:
                session.duration_hours = 0.0