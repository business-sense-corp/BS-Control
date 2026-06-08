from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BsBacklogItem(models.Model):
    _name = "bs.backlog.item"
    _description = "BS Backlog Item"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)

    description = fields.Text()

    task_type = fields.Selection([
        ('development', '⚙️ Development'),
        ('analysis', '🔍 Analysis'),
        ('testing', '🧪 Testing'),
        ('meeting', '🤝 Meeting'),
        ('client_visit', '🏢 Client Visit'),
        ('training', '📚 Training'),
        ('marketing', '📢 Marketing'),
        ('support', '🛠️ Support'),
        ('documentation', '📝 Documentation'),
        ('deployment', '🚀 Deployment'),
        ('internal_task', '📌 Internal Task'),
        ('bug', '🐞 Bug'),
        ('change_request', '🔄 Change Request'),
        ('idea', '💡 Idea'),
    ], string="Task Type", default='development', tracking=True)

    partner_id = fields.Many2one(
        'res.partner',
        string="Customer",
        tracking=True
    )

    project_id = fields.Many2one(
        'project.project',
        string="Project",
        tracking=True
    )

    assigned_user_id = fields.Many2one(
        'res.users',
        string="Assigned User",
        tracking=True
    )

    priority = fields.Selection([
        ('low', '🟢 Low'),
        ('medium', '🟡 Medium'),
        ('high', '🟠 High'),
        ('critical', '🔴 Critical'),
    ], default='medium', tracking=True)

    estimated_hours = fields.Float()

    story_points = fields.Float()

    status = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
        ('reopened', 'Reopened'),
    ], default='todo', tracking=True)

    lifecycle_state = fields.Selection([
        ('draft', 'Draft'),
        ('backlog', 'Backlog'),
        ('planned', 'Planned'),
        ('active_sprint', 'Active Sprint'),
        ('done', 'Done'),
        ('archived', 'Archived'),
    ], default='backlog', tracking=True)

    due_date = fields.Date()

    definition_of_done = fields.Text(required=True)

    is_billable = fields.Boolean()

    department_id = fields.Many2one(
        'hr.department',
        string="Department"
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            if rec.project_id and rec.project_id.partner_id != rec.partner_id:
                rec.project_id = False

    @api.constrains('partner_id', 'project_id')
    def _check_project_customer(self):
        for rec in self:
            if rec.project_id and not rec.partner_id:
                raise ValidationError(_(
                    'يجب اختيار العميل أولاً قبل اختيار المشروع.'
                ))

            if rec.partner_id and rec.project_id and rec.project_id.partner_id != rec.partner_id:
                raise ValidationError(_(
                    'المشروع المختار لا يتبع نفس العميل المحدد.'
                ))

    @api.constrains('due_date', 'create_date')
    def _check_dates(self):
        for rec in self:
            if rec.due_date and rec.create_date and rec.due_date < rec.create_date.date():
                raise ValidationError(_(
                    'لا يمكنك إنشاء مهمة عمل وموعد تسليمها سابق لموعد بدءها'
                ))

    def action_open_move_to_sprint_wizard(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Move To Sprint",
            "res_model": "bs.move.backlog.to.sprint.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": self._name,
                "active_id": self.id,
                "default_backlog_item_id": self.id,
                "default_assigned_user_id": self.assigned_user_id.id,
                "default_estimated_hours": self.estimated_hours,
                "default_priority": self.priority,
                "default_end_date": self.due_date,
            },
        }