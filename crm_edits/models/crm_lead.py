from odoo import fields, models, Command, _, api
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    product_template_ids = fields.Many2many('product.template')

    def _prepare_opportunity_quotation_context(self):
        sale_order = super()._prepare_opportunity_quotation_context()
        for rec in self:
            sale_order.update({
                'default_product_template_ids' : rec.product_template_ids.ids
            })
        return sale_order
