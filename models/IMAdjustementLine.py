from odoo import fields, models, api

class IMAdjustementLine(models.Model):
    _name = 'immo.inv.line'
    _description = 'Inventory Adjustment Line'

    immo_inv = fields.Many2one('immo.inv', string='Inventory Adjustment', ondelete='cascade')

    employee_id = fields.Many2one('hr.employee', string='Employée', required=True)
    company_id = fields.Many2one('res.company', string='Etablissement', required=True)
    departement_id = fields.Many2many('hr.department', string='Département', required=True)
    desktop_id = fields.Many2many('hr.work.location', string='Bureaux', required=False)
    equipe = fields.Selection([
        ('equipe1','Equipe 01'),
        ('equipe2','Equipe 02'),
    ])
    taux_progres = fields.Char(string='Taux Progress', default='0%')
    state = fields.Selection([('en_cours', 'En cours'), ('fini', 'Terminé')],string='Status', default='en_cours')