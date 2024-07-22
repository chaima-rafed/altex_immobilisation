from odoo import models, fields, api


class TempImobilisation(models.Model):
    _name = "temp.imobilisation"
    _description = "Temporary Imobilisation"

    name = fields.Char(string="Name Immo")
    code = fields.Char(string='CODE D\'IMOBILISATION')
    code_inv = fields.Char(string='INV')
    compte_g = fields.Char(string='COMPTE G')
    code_bare = fields.Char(string='CODE BARE', unique=True)
    qte = fields.Integer(string="Quantity", default=1)
    desc = fields.Char(string="Description")
    num_garante = fields.Char(string="Num Garantie")
    marque = fields.Char(string="Marque")
    genre = fields.Char(string="Genre")
    num_serie = fields.Char(string="Num Série")
    category_id = fields.Many2one('account.asset.category', string='Category Immo')
    date = fields.Date(string='Date Aquisition', default=fields.Date.context_today)
    date_amortissement = fields.Date(string='Date Amortissement', default=fields.Date.context_today)
    value = fields.Float(string='Gross Value')
    salvage_value = fields.Float(string='Salvage Value')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    company_name = fields.Many2one('res.company', string="SITE")
    departement_id = fields.Many2one('hr.department', string="BAT")
    desktop_id = fields.Many2one('hr.work.location', string="BUR")
    categuorie_article = fields.Many2one('product.category', string="Categuorie Article")
    product_id = fields.Many2one('product.product', string='Produit Lié')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    note_commision = fields.Text(string="Note de Commission")
    date_commission = fields.Date(string="Date Commission")
    commission_id = fields.One2many('p.commission', 'get_asset_ids', string="Membre Commission")
    etat = fields.Selection([('verte', 'Trés Bien'), ('orange', 'Bien'), ('rouge', 'Mal fonctionné')], default='verte')
    state = fields.Selection(
        [
            ('draft', 'En attente amortissement'),
            ('open', 'En Cours Amortissement'),
            ('sortie', 'Fin Amortissement')
        ], 'Status Amortissement', default='draft')
    state_life = fields.Selection(
        [
            ('en_cours_affecter', 'En Cours Affectation'),
            ('in_use', 'En Cours d\'Utilisation'),
            ('attente_comission', 'Décission Commission'),
            ('wait_sold', 'En attente de vente'),
            ('sold', 'Vendu'),
            ('scrapped', 'Détruit')
        ], 'Status Immobilisation', default='en_cours_affecter')
    file = fields.Binary(string='File')