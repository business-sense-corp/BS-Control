from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    project_ids = fields.One2many('project.project','partner_id')
    project_count = fields.Integer(compute='_compute_project_count')


    @api.depends('project_ids')
    def _compute_project_count(self):
        for rec in self:
            rec.project_count = len(rec.project_ids)

    def action_open_projects(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'res_model': 'project.project',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
            }
        }
