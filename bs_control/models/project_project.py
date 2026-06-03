from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    x_planned_start_date = fields.Date(
        string="Planned Start Date",
        tracking=True,
    )

    x_planned_end_date = fields.Date(
        string="Planned End Date",
        tracking=True,
    )

    x_actual_start_date = fields.Date(
        string="Actual Start Date",
        tracking=True,
    )

    x_actual_end_date = fields.Date(
        string="Actual End Date",
        tracking=True,
    )

    x_project_status = fields.Selection(
        selection=[
            ("planning", "Planning"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        string="Project Status",
        compute="_compute_x_project_status",
        inverse="_inverse_x_project_status",
        store=True,
        readonly=False,
        tracking=True,
        help="Project status is synchronized with the project stage.",
    )

    x_project_priority = fields.Selection(
        selection=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Project Priority",
        default="medium",
        tracking=True,
        help="Manual project priority set from BS Info page.",
    )

    x_total_task_allocated_hours = fields.Float(
        string="Allocated Time",
        compute="_compute_project_time_progress",
        store=True,
        tracking=True,
        help="Total allocated time calculated from all project tasks.",
    )

    x_estimated_hours = fields.Float(
        string="Estimated Hours",
        compute="_compute_project_time_progress",
        store=True,
        tracking=True,
        help="Total allocated hours from all project tasks.",
    )

    x_actual_hours = fields.Float(
        string="Actual Hours",
        compute="_compute_project_time_progress",
        store=True,
        tracking=True,
        help="Total spent hours from all project tasks.",
    )

    x_estimated_cost = fields.Float(
        string="Estimated Cost",
        tracking=True,
    )

    x_actual_cost = fields.Float(
        string="Actual Cost",
        tracking=True,
    )

    x_completion_percentage = fields.Float(
        string="Completion Percentage",
        compute="_compute_project_time_progress",
        store=True,
        tracking=True,
        help="Calculated from project tasks: Spent Hours / Allocated Hours * 100.",
    )

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        copy=False,
    )

    analytic_distribution = fields.Json(
        string="Analytic Distribution",
        copy=False,
    )

    analytic_precision = fields.Integer(
        string="Analytic Precision",
        default=2,
    )

    # ---------------------------------------------------------
    # Project Status / Stage Sync
    # ---------------------------------------------------------

    def _get_bs_stage_name_by_status(self, status):
        stage_names = {
            "planning": "To Do",
            "active": "In Progress",
            "on_hold": "On Hold",
            "closed": "Done",
            "cancelled": "Cancelled",
        }
        return stage_names.get(status)

    def _get_bs_stage_sequence_by_status(self, status):
        sequences = {
            "planning": 10,
            "active": 20,
            "on_hold": 30,
            "closed": 40,
            "cancelled": 50,
        }
        return sequences.get(status, 99)

    def _get_bs_status_by_stage(self):
        self.ensure_one()

        stage_name = (self.stage_id.name or "").strip().lower()

        status_by_stage_name = {
            "to do": "planning",
            "todo": "planning",
            "draft": "planning",
            "planning": "planning",

            "in progress": "active",
            "active": "active",
            "open": "active",

            "on hold": "on_hold",

            "done": "closed",
            "closed": "closed",

            "cancelled": "cancelled",
            "canceled": "cancelled",
        }

        return status_by_stage_name.get(stage_name, "planning")

    def _get_or_create_bs_stage(self, status):
        stage_name = self._get_bs_stage_name_by_status(status)

        if not stage_name:
            return False

        stage = self.env["project.project.stage"].with_context(active_test=False).search(
            [("name", "=", stage_name)],
            limit=1,
        )

        if not stage:
            stage = self.env["project.project.stage"].create({
                "name": stage_name,
                "sequence": self._get_bs_stage_sequence_by_status(status),
            })

        return stage

    @api.depends("stage_id", "stage_id.name")
    def _compute_x_project_status(self):
        for project in self:
            project.x_project_status = project._get_bs_status_by_stage()

    def _inverse_x_project_status(self):
        for project in self:
            if not project.x_project_status:
                continue

            stage = project._get_or_create_bs_stage(project.x_project_status)

            if stage and project.stage_id != stage:
                project.stage_id = stage

    @api.onchange("x_project_status")
    def _onchange_x_project_status(self):
        for project in self:
            if not project.x_project_status:
                continue

            stage = project._get_or_create_bs_stage(project.x_project_status)

            if stage:
                project.stage_id = stage

    @api.onchange("stage_id")
    def _onchange_stage_id_sync_status(self):
        for project in self:
            project.x_project_status = project._get_bs_status_by_stage()

    # ---------------------------------------------------------
    # Project Time / Progress Calculation
    # ---------------------------------------------------------

    @api.depends(
        "task_ids",
        "task_ids.allocated_hours",
        "task_ids.effective_hours",
    )
    def _compute_project_time_progress(self):
        for project in self:
            total_allocated_hours = sum(project.task_ids.mapped("allocated_hours"))
            total_spent_hours = sum(project.task_ids.mapped("effective_hours"))

            project.x_total_task_allocated_hours = total_allocated_hours
            project.x_estimated_hours = total_allocated_hours
            project.x_actual_hours = total_spent_hours

            if total_allocated_hours:
                completion_percentage = (total_spent_hours / total_allocated_hours) * 100
                project.x_completion_percentage = min(completion_percentage, 100.0)
            else:
                project.x_completion_percentage = 0.0

    # ---------------------------------------------------------
    # Dates Validation
    # ---------------------------------------------------------

    @api.constrains(
        "x_planned_start_date",
        "x_planned_end_date",
        "x_actual_start_date",
        "x_actual_end_date",
    )
    def _check_bs_project_dates(self):
        for project in self:
            if (
                project.x_planned_start_date
                and project.x_planned_end_date
                and project.x_planned_end_date < project.x_planned_start_date
            ):
                raise ValidationError(_(
                    "Planned End Date cannot be before Planned Start Date."
                ))

            if (
                project.x_planned_start_date
                and project.x_actual_start_date
                and project.x_actual_start_date < project.x_planned_start_date
            ):
                raise ValidationError(_(
                    "Actual Start Date cannot be before Planned Start Date."
                ))

            if (
                project.x_actual_start_date
                and project.x_actual_end_date
                and project.x_actual_end_date < project.x_actual_start_date
            ):
                raise ValidationError(_(
                    "Actual End Date cannot be before Actual Start Date."
                ))

    @api.onchange(
        "x_planned_start_date",
        "x_planned_end_date",
        "x_actual_start_date",
        "x_actual_end_date",
    )
    def _onchange_bs_project_dates(self):
        for project in self:
            if (
                project.x_planned_start_date
                and project.x_planned_end_date
                and project.x_planned_end_date < project.x_planned_start_date
            ):
                return {
                    "warning": {
                        "title": _("Invalid Date"),
                        "message": _("Planned End Date cannot be before Planned Start Date."),
                    }
                }

            if (
                project.x_planned_start_date
                and project.x_actual_start_date
                and project.x_actual_start_date < project.x_planned_start_date
            ):
                return {
                    "warning": {
                        "title": _("Invalid Date"),
                        "message": _("Actual Start Date cannot be before Planned Start Date."),
                    }
                }

            if (
                project.x_actual_start_date
                and project.x_actual_end_date
                and project.x_actual_end_date < project.x_actual_start_date
            ):
                return {
                    "warning": {
                        "title": _("Invalid Date"),
                        "message": _("Actual End Date cannot be before Actual Start Date."),
                    }
                }

    # ---------------------------------------------------------
    # Analytic Account / Distribution Logic
    # ---------------------------------------------------------

    @api.onchange("analytic_account_id")
    def _onchange_analytic_account_id(self):
        for project in self:
            if project.analytic_account_id:
                project.analytic_distribution = {
                    str(project.analytic_account_id.id): 100.0
                }
            else:
                project.analytic_distribution = False

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        for project in self:
            distribution = project.analytic_distribution or {}

            if distribution and len(distribution) == 1:
                analytic_id = list(distribution.keys())[0]
                project.analytic_account_id = int(analytic_id)
            else:
                project.analytic_account_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("analytic_account_id") and not vals.get("analytic_distribution"):
                vals["analytic_distribution"] = {
                    str(vals["analytic_account_id"]): 100.0
                }

        return super().create(vals_list)

    def write(self, vals):
        if vals.get("analytic_account_id") and "analytic_distribution" not in vals:
            vals["analytic_distribution"] = {
                str(vals["analytic_account_id"]): 100.0
            }

        elif "analytic_account_id" in vals and not vals.get("analytic_account_id"):
            vals["analytic_distribution"] = False

        return super().write(vals)