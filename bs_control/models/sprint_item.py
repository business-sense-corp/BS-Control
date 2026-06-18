from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class BSSprintItem(models.Model):
    _name = "bs.sprint.item"
    _description = "Business Sense Sprint Item"
    _rec_name = "name"
    _order = "sprint_id desc, end_date asc, id desc"

    name = fields.Char(
        string="Task Name",
        required=True,
    )

    sprint_id = fields.Many2one(
        "bs.sprint",
        string="Sprint",
        required=True,
        ondelete="cascade",
    )

    backlog_item_id = fields.Many2one(
        "bs.backlog.item",
        string="Backlog Item",
        ondelete="restrict",
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project",
    )

    assigned_user_id = fields.Many2one(
        "res.users",
        string="Assigned User",
    )

    estimated_hours = fields.Float(
        string="Estimated Hours",
    )

    actual_hours = fields.Float(
        string="Actual Hours",
    )

    remaining_hours = fields.Float(
        string="Remaining Hours",
        compute="_compute_remaining_hours",
        store=True,
    )

    status = fields.Selection(
        [
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("review", "Review"),
            ("blocked", "Blocked"),
            ("done", "Done"),
            ("reopened", "Reopened"),
        ],
        string="Status",
        default="todo",
        required=True,
        group_expand="_group_expand_status",
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

    reopen_count = fields.Integer(
        string="Reopen Count",
        default=0,
        readonly=True,
    )

    completion_percentage = fields.Float(
        string="Completion %",
        compute="_compute_completion_percentage",
        store=True,
    )

    work_session_ids = fields.One2many(
        "bs.work.session",
        "sprint_item_id",
        string="Work Sessions",
    )

    is_work_running = fields.Boolean(
        string="Is Work Running",
        compute="_compute_work_button_states",
    )

    can_start_work = fields.Boolean(
        string="Can Start Work",
        compute="_compute_work_button_states",
    )

    can_resume_work = fields.Boolean(
        string="Can Resume Work",
        compute="_compute_work_button_states",
    )

    @api.model
    def _group_expand_status(self, values, domain, order=None):
        return [key for key, label in self._fields["status"].selection]

    @api.depends("estimated_hours", "actual_hours")
    def _compute_remaining_hours(self):
        for item in self:
            item.remaining_hours = max(
                item.estimated_hours - item.actual_hours,
                0.0,
            )

    @api.depends("estimated_hours", "actual_hours", "status")
    def _compute_completion_percentage(self):
        for item in self:
            if item.status == "done":
                item.completion_percentage = 100.0
            elif item.estimated_hours > 0:
                item.completion_percentage = min(
                    (item.actual_hours / item.estimated_hours) * 100,
                    100.0,
                )
            else:
                item.completion_percentage = 0.0

    @api.depends(
        "status",
        "work_session_ids.user_id",
        "work_session_ids.state",
        "work_session_ids.end_datetime",
    )
    def _compute_work_button_states(self):
        for item in self:
            current_user_sessions = item.work_session_ids.filtered(
                lambda session: session.user_id.id == self.env.user.id
            )

            running_session = current_user_sessions.filtered(
                lambda session: session.state == "running" and not session.end_datetime
            )

            item.is_work_running = bool(running_session)

            item.can_start_work = (
                not running_session
                and not current_user_sessions
                and item.status not in ["done", "blocked"]
            )

            item.can_resume_work = (
                not running_session
                and bool(current_user_sessions)
                and item.status not in ["done", "blocked"]
            )

    @api.onchange("backlog_item_id")
    def _onchange_backlog_item_id(self):
        for item in self:
            if item.backlog_item_id:
                item.name = item.backlog_item_id.display_name

                if "project_id" in item.backlog_item_id._fields:
                    item.project_id = item.backlog_item_id.project_id

                if "priority" in item.backlog_item_id._fields:
                    backlog_priority = item.backlog_item_id.priority
                    sprint_priorities = dict(item._fields["priority"].selection)

                    if backlog_priority in sprint_priorities:
                        item.priority = backlog_priority

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for item in self:
            if item.start_date and item.end_date and item.end_date < item.start_date:
                raise ValidationError(
                    _("End Date cannot be earlier than Start Date.")
                )

    def _activate_sprint_if_needed(self):
        sprints = self.mapped("sprint_id").filtered(
            lambda sprint: sprint.status in ["draft", "planning"]
        )

        if sprints:
            sprints.write({
                "status": "active",
            })

    def _get_running_session(self):
        self.ensure_one()

        return self.env["bs.work.session"].search([
            ("sprint_item_id", "=", self.id),
            ("user_id", "=", self.env.user.id),
            ("state", "=", "running"),
            ("end_datetime", "=", False),
        ], limit=1)

    def _recompute_actual_hours_from_sessions(self):
        for item in self:
            finished_sessions = item.work_session_ids.filtered(
                lambda session: session.end_datetime
            )
            item.actual_hours = sum(finished_sessions.mapped("duration_hours"))

    def _get_backlog_lifecycle_state(self, status):
        if status == "done":
            return "done"

        if status in ["in_progress", "review", "blocked", "reopened"]:
            return "active_sprint"

        return "planned"

    def _sync_backlog_status(self):
        for item in self:
            if not item.backlog_item_id:
                continue

            item.backlog_item_id.write({
                "status": item.status,
                "lifecycle_state": item._get_backlog_lifecycle_state(item.status),
            })

    def action_start_work(self):
        for item in self:
            running_session = item._get_running_session()

            if running_session:
                continue

            self.env["bs.work.session"].create({
                "sprint_item_id": item.id,
                "user_id": self.env.user.id,
                "start_datetime": fields.Datetime.now(),
                "state": "running",
            })

            if item.status in ["todo", "reopened"]:
                item.status = "in_progress"

            item._activate_sprint_if_needed()

        return True

    def action_pause_work(self):
        for item in self:
            running_session = item._get_running_session()

            if running_session:
                running_session.write({
                    "end_datetime": fields.Datetime.now(),
                    "state": "paused",
                })
                item._recompute_actual_hours_from_sessions()

        return True

    def action_resume_work(self):
        for item in self:
            running_session = item._get_running_session()

            if running_session:
                continue

            self.env["bs.work.session"].create({
                "sprint_item_id": item.id,
                "user_id": self.env.user.id,
                "start_datetime": fields.Datetime.now(),
                "state": "running",
            })

            if item.status in ["todo", "reopened"]:
                item.status = "in_progress"

            item._activate_sprint_if_needed()

        return True

    def action_stop_work(self):
        for item in self:
            running_session = item._get_running_session()

            if running_session:
                running_session.write({
                    "end_datetime": fields.Datetime.now(),
                    "state": "done",
                })
                item._recompute_actual_hours_from_sessions()

        return True

    def action_send_to_review(self):
        for item in self:
            item.status = "review"

        return True

    def action_mark_done(self):
        for item in self:
            running_session = item._get_running_session()

            if running_session:
                running_session.write({
                    "end_datetime": fields.Datetime.now(),
                    "state": "done",
                })
                item._recompute_actual_hours_from_sessions()

            item.status = "done"

        return True

    def action_block(self):
        for item in self:
            running_session = item._get_running_session()

            if running_session:
                running_session.write({
                    "end_datetime": fields.Datetime.now(),
                    "state": "paused",
                })
                item._recompute_actual_hours_from_sessions()

            item.status = "blocked"

        return True

    def action_reopen(self):
        for item in self:
            item.status = "reopened"

        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_backlog_status()
        return records

    def write(self, vals):
        status_changed = "status" in vals

        old_status_by_item = {
            item.id: item.status
            for item in self
        }

        result = super().write(vals)

        if status_changed:
            for item in self:
                old_status = old_status_by_item.get(item.id)

                if item.status == "reopened" and old_status != "reopened":
                    item.reopen_count += 1

            self._sync_backlog_status()

            if vals.get("status") == "in_progress":
                self._activate_sprint_if_needed()

        return result