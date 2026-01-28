from odoo import fields, models, Command, _, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    product_template_ids = fields.Many2many('product.template')

    #append sale order lines
    # @api.onchange('product_template_ids')
    # @api.constrains('product_template_ids')
    # def _update_sale_order_lines(self):
    #     for rec in self:
    #         rec.order_line.update({
    #             ''
    #         })

# class SaleOrderLine(models.Model):
#     _inherit = "sale.order.line"