from odoo import fields, api, models

class IMProduct(models.Model):
    _inherit = 'product.template'

    is_immo = fields.Boolean("Is Immo", default=False)