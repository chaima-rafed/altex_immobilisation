from odoo import api, fields, models


class AssetInventoryDifferenceBetween2Table(models.Model):
    _name = 'asset.inventory.difference.2.table'
    _description = 'Asset Inventory Difference Between The Two Table'
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

    # Compute differences between the asset in the  and what the employee verify and see in the reality
    @api.model
    def compute_differences(self):
        print(f'hi')
        differences = []

        # Get records from im.adjustement.inv1
        asset_inventory_verify_records = self.env['asset.inventory.difference1'].search([])

        for inventory_verify_record in asset_inventory_verify_records:
            # search if exist on asset.inventory.difference2 or not
            get_asset_inventorydifference = self.env['asset.inventory.difference.2.table'].search([
                ('asset_id', '=', inventory_verify_record.asset_id.id),
                ('code_bare', '=', inventory_verify_record.code_bare),
            ])

            if not get_asset_inventorydifference:

                # Check if there is a corresponding record in asset.inventory.difference.2.table
                asset_record = self.env['asset.inventory.difference.2.table'].search([
                    ('id', '=', inventory_verify_record.asset_id.id),
                    ('code_bare', '=', inventory_verify_record.code_bare),
                    ('employee_id', '=', inventory_verify_record.employee_id.id),
                    ('company_id', '=', inventory_verify_record.company_name.id),
                    ('departement_id', '=', inventory_verify_record.departement_id.id),
                    ('desktop_id', '=', inventory_verify_record.desktop_id.id),
                ])

                # update asset_verify field to True
                # inventory_verify_record.write({'asset_verify': 'oui'})

                # Add record to difference table when we have a difference
                if not asset_record:
                    # If no corresponding record found, add to differences
                    differences.append({
                        'asset_id': inventory_verify_record.asset_id.id,
                        'employee_id': inventory_verify_record.employee_id.id,
                        'company_id': inventory_verify_record.company_name.id,
                        'departement_id': inventory_verify_record.departement_id.id,
                        'desktop_id': inventory_verify_record.desktop_id.id,
                        'code': inventory_verify_record.code,
                        'code_inv': inventory_verify_record.code_inv,
                        'compte_g': inventory_verify_record.compte_g,
                        'code_bare': inventory_verify_record.code_bare,
                    })

                # Create records in asset.inventory.difference1
                self.create(differences)