# -*- coding: utf-8 -*-
from odoo import models, fields


class IMLieu_de_travail(models.Model):
    _inherit = "hr.work.location"
    #_rec_name = 'code_bur'

    name = fields.Char(string="Bureaux", required=True)
    code_bur = fields.Char(string="CODE BUR")
    code_niv = fields.Char(string="CODE NIV", readonly=False)
    departement_id = fields.Many2one('hr.department', string="Département")
