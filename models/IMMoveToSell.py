from odoo import api, fields, models


class IMMoveToSell(models.Model):
    _name = 'asset.move.tosell'
    _rec_name = 'asset_code'
    _description = 'Assets to Sell'

    asset_id = fields.Many2one('account.asset.asset', string='Nom d\'immobilisation', required=True)
    asset_code = fields.Char(string='Code', required=True)
    asset_compte_g = fields.Char(string='COMPTE G')
    asset_code_inv = fields.Char(string='Code INV')
    asset_code_bur = fields.Char(string='Code BUR')
    asset_code_niv = fields.Char(string='Code NIV')
    asset_code_bat = fields.Char(string='Code BAT')
    asset_code_bare = fields.Char(string='Code BAR')
    asset_marque = fields.Char(string="Marque")
    asset_genre = fields.Char(string="Genre")
    asset_num_serie = fields.Char(string="Num Série")
    qte = fields.Integer(string='QTE', default=1)
    employee = fields.Many2one('hr.employee', string="Employee", required=True)
    societe = fields.Char(string="SITE")
    departement = fields.Char(string="BAT")
    desktop = fields.Char(string="BUR")
    sale_order_id = fields.Many2one('sale.order', string='Bon de Commande', copy=False)
    product_id = fields.Integer(string='Produit Lié')
    value = fields.Char(string='Valeur Brute')
    currency_id = fields.Char(string='Devise')
    category = fields.Char(string='Catégorie')
    # categuorie_article = fields.Many2one('product.category', string="Categuorie Article", required=True)
    partner_id = fields.Many2one('res.partner', string='Partenaires', required=True)
    value_residual = fields.Char(string='Residual Value')
    salvage_value = fields.Char(string='Valeur de Récupération')
    # remaining_value = fields.Monetary(string='Valeur Résiduelle', required=True)
    # depreciated_value = fields.Monetary(string='Valeur Amortie', required=True)
    # depreciation_date = fields.Date('Date de Dépréciation', index=True)
    price_to_sell = fields.Char(string='Prix de Vente', required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('is_sold', 'Est Vendu')], default='draft', string='État')

    @api.onchange('asset_id')
    def onchange_get_other_fields(self):
        if self.asset_id:
            self.asset_code = self.asset_id.code
            self.asset_compte_g = self.asset_id.compte_g
            self.asset_code_inv = self.asset_id.code_inv
            self.asset_marque = self.asset_id.marque
            self.asset_genre = self.asset_id.genre
            self.asset_num_serie = self.asset_id.num_serie
            self.employee = self.asset_id.employee_id.id
            self.value_residual = self.asset_id.value_residual
            self.salvage_value = self.asset_id.salvage_value
            # self.remaining_value = self.asset_id.remaining_value
            # self.depreciated_value = self.asset_id.depreciated_value
            # self.depreciation_date = self.asset_id.depreciation_date

    # Sell Asset
    def sell_asset(self):
        # Create a new sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,  # Assuming partner_id is the customer
        })
        # print(f'order_id = {sale_order.id} \n product_id = {self.product_id} \n product_name = {self.name} \n qte = {self.qte} \n price = {self.value} ')

        sale_order_line = self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product_id,
            'product_uom_qty': self.qte,
            'price_unit': self.price_to_sell,
        })

        self.write({'sale_order_id': sale_order.id})
        # change te state to Is sold
        self.write({'state': 'is_sold'})

        #update the state on account.asset.asset set it to close cause is bought it
        get_asset = self.env['account.asset.asset'].search([('code', '=', self.asset_code)])
        get_asset.write({'state_life': 'sold'})
        print(f'get_asset = {get_asset} ')

        # Redirect the user to the sale order form view
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'view_id': self.env.ref('sale.view_order_form').id,
            'target': 'current',
        }
