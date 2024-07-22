from odoo import api, fields, models


class AssetInventoryDifference2(models.Model):
    _name = 'asset.inventory.difference2'
    _description = 'Asset Inventory Difference2'
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

    # Compute differences between the asset in the database and what the employee verify and see in the reality
    @api.model
    def compute_differences(self):
        print(f'hi')
        differences = []

        # Get records from im.adjustement.inv2
        asset_inventory_verify_records = self.env['im.adjustement.inv2'].search([])

        for inventory_verify_record in asset_inventory_verify_records:
            # search if exist on asset.inventory.difference2 or not
            get_asset_inventorydifference = self.env['asset.inventory.difference2'].search([
                ('asset_id', '=', inventory_verify_record.asset_id.id),
                ('code_bare', '=', inventory_verify_record.code_bare),
            ])

            if not get_asset_inventorydifference:
                # print(f'record = {inventory_verify_record}')
                # Check if there is a corresponding record in account.asset.asset
                asset_record = self.env['account.asset.asset'].search([
                    ('id', '=', inventory_verify_record.asset_id.id),
                    ('code_bare', '=', inventory_verify_record.code_bare),
                    ('employee_id', '=', inventory_verify_record.employee_id.id),
                    ('company_name', '=', inventory_verify_record.company_name.id),
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

                # Create records in asset.inventory.difference2
                self.create(differences)

    def compute_d(self, differences):
        diff = []
        if differences:
            for inventory_verify_record in differences:
                print(f'inventory_verify_record {inventory_verify_record}')
                print(f"inventory_verify_record {inventory_verify_record['inventaire']}")
                # search if exist on asset.inventory.difference2 or not (dublicated)
                get_asset_inventorydifference = self.env['asset.inventory.difference2'].search([
                    ('inventaire', '=', inventory_verify_record['inventaire']),
                    ('code', '=', inventory_verify_record['code']),
                ])

                print(f'get ggggggggggggggg  {get_asset_inventorydifference}')

                if not get_asset_inventorydifference:
                    # If no corresponding record found, add to diff
                    diff.append({
                        'asset_id': inventory_verify_record['code_bare'],
                        'employee_id': inventory_verify_record['employee_id'],
                        'company_id': inventory_verify_record['company_id'],
                        'departement_id': inventory_verify_record['departement_id'],
                        'desktop_id': inventory_verify_record['desktop_id'],
                        'code': inventory_verify_record['code'],
                        'code_inv': inventory_verify_record['code_inv'],
                        'compte_g': inventory_verify_record['compte_g'],
                        'code_bare': inventory_verify_record['code_bare'],
                        'status': inventory_verify_record['status'],
                        'inventaire': inventory_verify_record['inventaire'],
                    })

                    # todo Create records in asset.inventory.difference2
                    self.create(diff)

    # Update asset_verify field of asset.inventory.verify2 model to False after delete it
    def update_related_verify_records(self):
        print('2')
        # Get asset IDs from the records
        asset_ids = self.mapped('asset_id')
        print('3')
        print(f'asset_ids = {asset_ids}')
        # Find related records in asset.inventory.verify2 and update asset_verify to False
        verify_records = self.env['asset.inventory.verify2'].search([('asset_id', 'in', asset_ids)])
        if verify_records:
            print(f'verify records = {verify_records}')
            print('4')
            verify_records.write({'asset_verify': 'non'})
            print('5')

    def unlink(self):
        print('1')
        # Update related records in asset.inventory.verify2 before deleting
        # self.update_related_verify_records()
        print('6')

        # Call the unlink method of the superclass
        return super(AssetInventoryDifference2, self).unlink()

    def write(self, vals):
        print(f'dddddddddddddddddddddddd hhhhhhhhhhh ggggggggggg {vals} self {self}')
        if self.asset_id:
            get_asset = self.env['account.asset.asset'].search([('id', '=', self.asset_id.id)])
            if get_asset:
                get_asset.write(vals)
                # get_asset.write({
                #    'code': self.code,
                #    'code_in#v': self.code_inv,
                #    'compte_g': self.compte_g,
                #    'desc': self.desc,
                #    'num_garante': self.num_garante,
                #    'marque': self.marque,
                #    'genre': self.genre,
                #    'num_serie': self.num_serie,
                #    'employee_id': self.employee_id.id,
                #    'company_name': self.company_id.id,
                #    'departement_id': self.departement_id.id,
                #    'desktop_id': self.desktop_id.id,
                #    'categuorie_article': self.categuorie_article.id,
                #    'etat': self.etat,
                #    'state': self.state,
                #    'state_life': self.state_life
                # })
                print(f'its makes updated')

            # Call super to perform default behavior (update record)
            return super(AssetInventoryDifference2, self).write(vals)
