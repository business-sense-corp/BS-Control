from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = "project.task"

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
    ], string="Task Type", default='development')

    story_points = fields.Integer()

    department = fields.Selection([
        ('odoo_dev', '⚙️ Odoo Development'),
        ('implementation', '🚀 Odoo Implementation'),
        ('support', '🎧 Technical Support'),
        ('analysis', '📊 Business Analysis'),
        ('training', '📚 Training'),
        ('sales', '💰 Sales'),
        ('marketing', '📢 Marketing'),
        ('accounting', '💵 Accounting'),
        ('hr', '👥 Human Resources'),
    ], string="Department", default='odoo_dev')

    definition_of_done = fields.Text()
    # lifecycle state will be the stages in the project

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for rec in self:
            rec.partner_id = rec.project_id.partner_id