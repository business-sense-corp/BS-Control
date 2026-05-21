from odoo import fields, models


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
        default="planning",
        tracking=True,
    )

    x_estimated_hours = fields.Float(
        string="Estimated Hours",
        tracking=True,
    )

    x_actual_hours = fields.Float(
        string="Actual Hours",
        tracking=True,
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
        tracking=True,
        help="Project completion percentage from 0 to 100.",
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
    )