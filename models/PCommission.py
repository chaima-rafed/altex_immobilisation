# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Commission(models.Model):
    _name = 'p.commission'

    get_asset_ids = fields.Many2one('account.asset.asset', string="Immobilisations")
    employee_id = fields.Many2one('hr.employee', string='Les membres du comité')
    grade = fields.Selection([
        ('chef', 'CHEF COMMISSION'),
        ('membre', 'MEMBRE COMMISSION')
    ])