# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class IMSociete(models.Model):
     _inherit = "res.company"
     #_rec_name = 'code_site'

     code_site = fields.Char(string="CODE SITE")
     departement_ids = fields.One2many('hr.department', 'company_id', string="Départemnts")
     asset_ids = fields.One2many('account.asset.asset', 'id', string='Immobilisations')