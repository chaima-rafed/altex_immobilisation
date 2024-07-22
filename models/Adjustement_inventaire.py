from odoo import api, fields, models


class IMAdjustement(models.Model):
    _name = 'immo.inv'

    immo_inv_id = fields.One2many('immo.inv.line', 'immo_inv', string='Personne a Affecter', ondelete='cascade')
    verify_id = fields.One2many('asset.inventory.verify1', 'inv_lines_id', string="Fait inventaire 01")
    verify_id2 = fields.One2many('asset.inventory.verify2', 'inv_lines_id', string="Fait inventaire 02")

    name = fields.Char(string="Nom d'Inventaire d'immobilisation",
                       placeholder="Entrez la réffirence de ce inventaire par exp . INV Janv-Juine 2024",
                       required=True, help='It\'s a unique name')
    date_depart = fields.Date(string="Date Départ Inventaite", required=True)
    date_cloture = fields.Date(string="Date Cloture Inventaite")
    date_debut_comptage = fields.Date(string="Date Debut Comptage Inventaite")
    date_fin_comptage = fields.Date(string="Date Fin Comptage Inventaite")
    date_debut_adjustement = fields.Date(string="Date Debut Adjustement Inventaite")
    date_fin_adjustement = fields.Date(string="Date Fin Adjustement Inventaite")

    res_informatique = fields.Many2one('res.users', string="Responsable Inventaire", required=True)

    im_adjustement_many1 = fields.Many2one('im.adjustement.inv1', string="IM Adjustement Inv1")
    im_adjustement_many2 = fields.Many2one('im.adjustement.inv2', string="IM Adjustement Inv2")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "A report line with the same code already exists."),
    ]

    #Return to the action_adjustement_inv view
    def get_immo_count_data1(self):
        print('hi')
        return self.env.ref('altex_imobilisation.action_adjustement_inv1').read()[0]


    #Return to the action_adjustement_inv view
    def get_immo_count_data2(self):
        print('hi')
        return self.env.ref('altex_imobilisation.action_adjustement_inv2').read()[0]
