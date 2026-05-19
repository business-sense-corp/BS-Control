from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = "project.project"

    estimated_cost = fields.Float(string="Estimated Cost")
    member_ids = fields.Many2many(
        'res.users',
        string="Team Members"
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    analytic_distribution = fields.Json(
        string='Analytic Distribution',
        copy=False,
    )

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        for project in self:
            if project.analytic_account_id:
                project.analytic_distribution = {
                    str(project.analytic_account_id.id): 100.0
                }
            else:
                project.analytic_distribution = False

    @api.onchange('analytic_distribution')
    def _onchange_analytic_distribution(self):
        for project in self:
            distribution = project.analytic_distribution or {}
            if distribution and len(distribution) == 1:
                project.analytic_account_id = int(list(distribution.keys())[0])
            else:
                project.analytic_account_id = False

    def write(self, vals):
        res = super().write(vals)

        for project in self:
            if 'analytic_account_id' in vals:
                if project.analytic_account_id:
                    super(ProjectProject, project).write({
                        'analytic_distribution': {
                            str(project.analytic_account_id.id): 100.0
                        }
                    })
                else:
                    super(ProjectProject, project).write({
                        'analytic_distribution': False
                    })

            elif 'analytic_distribution' in vals:
                distribution = project.analytic_distribution or {}
                if distribution and len(distribution) == 1:
                    analytic_id = int(list(distribution.keys())[0])
                    if project.analytic_account_id.id != analytic_id:
                        super(ProjectProject, project).write({
                            'analytic_account_id': analytic_id
                        })
                else:
                    if project.analytic_account_id:
                        super(ProjectProject, project).write({
                            'analytic_account_id': False
                        })

        return res