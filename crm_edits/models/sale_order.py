from odoo import models, fields, api, Command


class SaleOrder(models.Model):
    _inherit = "sale.order"

    product_template_ids = fields.Many2many('product.template')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        template_cmds = res.get('product_template_ids')
        if not template_cmds:
            return res

        template_ids = []
        for cmd in template_cmds:
            if cmd[0] == 6:
                template_ids = cmd[2]

        if not template_ids:
            return res

        order_lines = []
        templates = self.env['product.template'].browse(template_ids)

        for template in templates:
            product = template.product_variant_id

            order_lines.append(Command.create({
                'product_id': product.id,
                'name': product.with_context(
                    lang=self.env.user.lang
                ).display_name,
                'product_uom_qty': 1,
                'tax_ids': [],
                'price_unit': product.lst_price,
            }))

        res['order_line'] = order_lines
        return res
