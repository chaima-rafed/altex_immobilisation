from odoo import api, fields, models

class AssetInventoryDifference(models.Model):
    _name = 'asset.inventory.difference'
    _description = 'Asset Inventory Difference'
    # _rec_name = 'asset_id'state_life

    asset_id = fields.Many2one('account.asset.asset', string='Immobilisation')
    employee_id = fields.Many2one('hr.employee', string='Employé')
    company_id = fields.Many2one('res.company', string='SITE')
    departement_id = fields.Many2one('hr.department', string='BAT')
    desktop_id = fields.Many2one('hr.work.location', string='BUR')
    code = fields.Char(string='CODE')
    code_inv = fields.Char(string='CODE INV')
    compte_g = fields.Char(string='COMPTE G')
    code_bare = fields.Char(string='CODE BARE')
    qte = fields.Integer(string='Quantité')
    desc = fields.Char(string="Description")
    num_garante = fields.Char(string="Num Garantie")
    marque = fields.Char(string="Marque")
    genre = fields.Char(string="Genre")
    num_serie = fields.Char(string="Num Série")
    categuorie_article = fields.Many2one('product.category', string="Categuorie Article", required=False)
    product_id = fields.Many2one('product.product', string='Produit Lié')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False)
    inventaire = fields.Char(string="Inventaire")
    status = fields.Char(string="Status")
    etat = fields.Selection([('verte', 'Trés Bien'), ('orange', 'Bien'), ('rouge', 'Mal fonctionné')], required=False,
                            default='verte')
    state = fields.Selection(
        [
            ('draft', 'En attente amortissement'),
            ('open', 'En Cours Amortissement'),
            ('sortie', 'Fin Amortissement')
        ], 'Status Amortissement', required=False, copy=False, default='draft')

    state_life = fields.Selection(
        [
            ('en_cours_affecter', 'En Cours Affectation'),
            ('in_use', 'En Cours d\'Utilisation'),
            ('attente_comission', 'Décission Commission'),
            ('wait_sold', 'En Attente De Vendu'),
            ('sold', 'Vendu'),
            ('scrapped', 'Détruit')
        ], 'Status Immobilisation', default='en_cours_affecter')

