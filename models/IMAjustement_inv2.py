from odoo import fields, models, api
from datetime import date, timedelta


class IMAdjustement_inv2(models.Model):
    _name = 'im.adjustement.inv2'
    _description = "Adjustement d'inventaire2"

    im_adjustement2 = fields.One2many('immo.inv', 'im_adjustement_many2', string="IM Adjustement 01")

    asset_id = fields.Many2one('account.asset.asset', string="Immobilisation")
    code = fields.Char(string="CODE")
    code_inv = fields.Char(string="CODE INV")
    code_bare = fields.Char(string="ANCIAN BARCODE")
    code_bare_nv = fields.Char(string="NOUVEAUX BARCODE")
    compte_g = fields.Char(string="COMPTE G")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=False)
    employee_fait_inv_id = fields.Many2one('hr.employee', string="Agent Inventaire", required=False)
    company_name = fields.Many2one('res.company', string="SITE")
    departement_id = fields.Many2one('hr.department', string="BAT")
    desktop_id = fields.Many2one('hr.work.location', string="BUR")
    inventaire = fields.Char(string="Inventaire")
    status = fields.Char(string="Status")

    count_asset_id = fields.Many2one('account.asset.asset', string="Immobilisation")
    count_code = fields.Char(string="CODE")
    count_code_inv = fields.Char(string="CODE INV")
    count_code_bare = fields.Char(string="CODE BARE")
    count_compte_g = fields.Char(string="COMPTE G")
    count_employee_id = fields.Many2one('hr.employee', string="Employee", required=False)
    count_company_name = fields.Many2one('res.company', string="SITE")
    count_departement_id = fields.Many2one('hr.department', string="BAT")
    count_desktop_id = fields.Many2one('hr.work.location', string="BUR")

    # todo Refresh table to get all the verification inventory
    def refresh_database(self):
        today = date.today()

        # Fetch data from asset.inventory.verify
        get_assets_inv_verify = self.env['asset.inventory.verify2'].search([])

        for asset in get_assets_inv_verify:
            print(f'hi')
            # todo get Inventory Name
            get_inventory_name = asset.inv_lines_id.name

            # print(f'asset = {asset}')
            # print(f'asset id = {asset.id}')
            # print(f'asset get_inventory_verify_line = {asset.get_inventory_verify_line}')

            for line in asset.get_inventory_verify_line:
                # Check if there's an existing entry in im.adjustement.inv with the same asset ID
                existing_adjustement = self.env['im.adjustement.inv2'].search([
                    ('asset_id', '=', line.asset_id.id)
                ], limit=1)

                data = {
                    'asset_id': line.asset_id.id,
                    'code': line.code,
                    'code_inv': line.code_inv,
                    'code_bare': line.code_bare,
                    'code_bare_nv': line.code_bare_nv,
                    'compte_g': line.compte_g,
                    'employee_id': line.employee_id.id,
                    'employee_fait_inv_id': asset.employee_inv_id.id,
                    'company_name': asset.company_id.id,
                    'departement_id': asset.departement_id.id,
                    'desktop_id': asset.desktop_id.id,
                    'status': line.status,
                    'create_date': today,
                    'inventaire': get_inventory_name
                }

                if existing_adjustement:
                    # Update existing record
                    print('exist data')
                    existing_adjustement.write(data)
                else:
                    # Create new record
                    self.env['im.adjustement.inv2'].create(data)

    def refresh_databaseAll(self):
        today = date.today()

        # Fetch all records from account.asset.asset
        all_assets = self.env['account.asset.asset'].search([])

        # Fetch all records from asset.inventory.verify
        all_inventory_verifications = self.env['asset.inventory.verify2'].search([])

        for asset in all_assets:
            # Find the corresponding inventory verification for the asset
            inventory_verification = all_inventory_verifications.filtered(
                lambda iv: iv.get_inventory_verify_line.filtered(lambda line: line.asset_id.id == asset.id))

            if inventory_verification:
                inventory_line = inventory_verification.mapped('get_inventory_verify_line').filtered(
                    lambda line: line.asset_id.id == asset.id)
                if inventory_line:
                    inventory_line = inventory_line[0]  # Get the first matching line

                    data = {
                        'asset_id': asset.id,
                        'code': asset.code,
                        'code_inv': asset.code_inv,
                        'code_bare': asset.code_bare,
                        'compte_g': asset.compte_g,
                        'employee_id': asset.employee_id.id,
                        'employee_fait_inv_id': inventory_verification.employee_inv_id.id,
                        'company_name': asset.company_id.id,
                        'departement_id': asset.departement_id.id,
                        'desktop_id': asset.desktop_id.id,
                        'count_asset_id': asset.id,
                        'count_code': inventory_line.code,
                        'count_code_inv': inventory_line.code_inv,
                        'count_code_bare': inventory_line.code_bare,
                        'count_compte_g': inventory_line.compte_g,
                        'count_employee_id': inventory_line.employee_id.id,
                        'count_company_name': inventory_line.company_id.id,
                        'count_departement_id': inventory_line.departement_id.id,
                        'count_desktop_id': inventory_line.desktop_id.id,
                    }

                    existing_adjustement = self.env['im.adjustement.inv2'].search([('asset_id', '=', asset.id)])

                    if existing_adjustement:
                        # Update existing record
                        existing_adjustement.write(data)
                    else:
                        # Create new record
                        self.env['im.adjustement.inv2'].create(data)
            else:
                data = {
                    'asset_id': asset.id,
                    'code': asset.code,
                    'code_inv': asset.code_inv,
                    'code_bare': asset.code_bare,
                    'compte_g': asset.compte_g,
                    'employee_id': asset.employee_id.id,
                    'company_name': asset.company_id.id,
                    'departement_id': asset.departement_id.id,
                    'desktop_id': asset.desktop_id.id,
                    'count_asset_id': asset.id,
                }
                existing_adjustement = self.env['im.adjustement.inv2'].search([('asset_id', '=', asset.id)])
                if existing_adjustement:
                    existing_adjustement.write(data)
                else:
                    self.env['im.adjustement.inv2'].create(data)

    # Function to calculate the difference between the asset stock and the real asset location (where assinged it ? employee, where is it ? agence, departement and desktop)
    @api.model
    def compute_and_display_differences(self, values):
        differences = []
        # Your logic to compute differences
        differences = self.env['asset.inventory.difference2'].compute_d(self.get_selected_records(differences))
        if differences:
            print(f'deferrence true')
            # Open a new window with the differences
            action = self.env.ref('altex_imobilisation.action_asset_inventory_difference2').read()[0]
            print(f'print data {action}')
            action['domain'] = [('id', 'in', differences.ids)]
            print(f'hello nasreddine {action} ')
            # print("Opening new window with differences:", action)
            return action
        else:
            print(f'deferrence false')
            # Redirect to Asset Inventory Differences menu
            menu_action = self.env.ref('altex_imobilisation.action_asset_inventory_difference2').read()[0]
            # print("Redirecting to Asset Inventory Differences menu:", menu_action)
            return menu_action

    #todo get selected records
    def get_selected_records(self, differences):
        selected_records = self.env['im.adjustement.inv2'].browse(self._context.get('active_ids', []))
        for record in selected_records:
            if record.status != 'exist':
                print(f'status {record.status}')
                differences.append({
                    'asset_id': record.asset_id.id,
                    'employee_id': record.employee_id.id,
                    'company_id': record.company_name.id,
                    'departement_id': record.departement_id.id,
                    'desktop_id': record.desktop_id.id,
                    'code': record.code,
                    'code_inv': record.code_inv,
                    'compte_g': record.compte_g,
                    'code_bare': record.code_bare,
                    'status': record.status,
                    'inventaire': record.inventaire,
                })
        return differences
