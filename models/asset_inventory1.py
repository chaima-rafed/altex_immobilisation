import time
from odoo import api, fields, models
import logging

from odoo.exceptions import ValidationError
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('sqlalchemy.engine')


class AssetInventory1(models.Model):
    _name = 'asset.inventory.verify1'
    _rec_name = 'departement_id'
    _description = 'Asset Inventory Verify'
    _inherit = ['mail.thread']


    get_inventory_verify_line = fields.One2many('asset.inventory.verify.line1', 'asset_inventory_verify',
                                                string='Immobilisation')
    inv_lines_id = fields.Many2one('immo.inv', string="INV LINES", domain=lambda self: self._get_inv_lines_domain())

    # category_id = fields.Many2one('account.asset.category', string='Catégorie d\'immobilisation', required=True, change_default=True)
    employee_inv_id = fields.Many2one('hr.employee', string='Agent Inventaire')
    code_bare = fields.Char(string='CODE BARE', required=False)
    company_id = fields.Many2one('res.company', string='SITE')
    departement_id = fields.Many2one('hr.department', string='BAT', required=True)
    desktop_id = fields.Many2one('hr.work.location', string='BUR', required=False)

    date_verification = fields.Datetime(string="Date verification", readonly=True, default=fields.Datetime.now)
    date_debut_inv = fields.Datetime(string="Début Comptage", required=True)
    date_fin_inv = fields.Datetime(string="Fin Comptage", required=True)
    asset_verify = fields.Selection([('oui', 'Verifier'), ('non', 'Non Verifier')], copy=False, default='non')
    scan_bat = fields.Char(string="SCANNER BAT")
    scan_bur = fields.Char(string="SCANNER BUR")

    asset_id = fields.Many2one('account.asset.asset', string='DESIGNATION')
    badge = fields.Selection([
        ('red', 'Not Allowed'),
        ('yellow', 'Allowed'),
    ], default='red')

    domain_departement_id = fields.Char(
        compute='_compute_domain_departement_id')  # compute='_compute_domain_departement_id'
    domain_desktop_id = fields.Char(
        compute='_get_assets_departement_departe')  # compute='_get_assets_departement_departe'

    prevent = fields.Boolean(string='prevent', default=False)

    @api.model
    def create(self, vals):
        get_emp = self.get_employee_user(self.env.user.id)
        if get_emp:
            vals['employee_inv_id'] = get_emp.id  # Set the current user's ID
            vals['company_id'] = self.env.company.id
            print(f'vals = {vals}')

            # Set skip_onchange context to True initially
            context = dict(self.env.context, skip_onchange=True)
            self = self.with_context(context)

            # update prevent to True when reating
            # self.write({'prevent', '=', True})
            vals['prevent'] = True
            # Perform creation logic
            new_record = super(AssetInventory1, self).create(vals)

            # Reset skip_onchange context after creation
            self = self.with_context(dict(self.env.context, skip_onchange=True))
            return new_record
        else:
            raise ValueError('Créer un employer pour ce utilisateur STP !!!')

    def write(self, vals):

        context = dict(self.env.context, skip_onchange=True)
        self = self.with_context(context)

        new_record = super(AssetInventory1, self).write(vals)

        self = self.with_context(dict(self.env.context, skip_onchange=False))
        return new_record

    # Delete all selected row of 'asset.inventory.verify1' and his get_inventory_verify_line rows or records
    def unlink(self):
        for record in self:
            record.get_inventory_verify_line.unlink()
        return super(AssetInventory1, self).unlink()

    # Filter the departements as the admin gives to the agent from 'Créer un nouveau inventaire' menu
    @api.onchange('inv_lines_id')
    def _compute_domain_departement_id(self):
        dict(self.env.context, skip_onchange=True)
        print(f'simple inscription ...')
        # if self.env.context.get('skip_onchange', False):
        #    print(f'what happening ....')
        #    self.domain_departement_id = '[]'
        #    return

        print(f'nastrrrrrrrrrrrrr {self.inv_lines_id}')
        domain = []
        if self.inv_lines_id:
            # Fetching related immo.inv lines
            immo_inv_lines = self.env['immo.inv'].browse(self.inv_lines_id.id).immo_inv_id.mapped('id')
            print(f'immo_inv_lines {immo_inv_lines}')
            # Fetching related departments from immo.inv.lines
            # departments = self.env['hr.department.immo.inv.line.rel'].search([('immo_inv_line_id', 'in', immo_inv_lines)]).mapped('hr_departement_id')
            departments = self.env['immo.inv.line'].search(
                [('id', '=', immo_inv_lines)]).departement_id  # .mapped('departement_id')
            print(f'departments {departments}')

            # Prepare domain to filter departement_id field
            department_ids = departments.ids
            # Prepare domain to filter departement_id field
            domain = [('id', 'in', department_ids)]
        self.domain_departement_id = repr(domain) if domain else "[]"

    @api.model
    def _get_inv_lines_domain(self):
        current_year = datetime.now().year
        print(f"Current Year: {current_year}")
        domain = [('date_depart', '!=', False), ('date_depart', '>=', f'{current_year}-01-01'),
                  ('date_depart', '<=', f'{current_year}-12-31')]
        print(f"Domain: %s {domain}")
        return domain

    @api.constrains('date_debut_inv')
    def _check_dates(self):
        for line in self.inv_lines_id:
            get_date_debut_comptage = line.date_debut_comptage
            if self.date_debut_inv.date() > get_date_debut_comptage:
                raise ValidationError(
                    "Vous n'avez pas respecté la date du comptage (Début Comptage) que l'administrateur vous a donnée")

    # Get the concerned Employee to make Inventory
    @api.onchange('inv_lines_id')
    def inventory_autorise_by_concerned_employee(self):
        # if self.env.context.get('skip_onchange', False):
        #    print('Skipping onchange method due to context')
        #    return

        found = []
        # todo The current user
        # Access the current user's employee record
        print(f'userrrrrrr {self.env.user.employee_ids}')
        print(f'userrrrrrr !33333 {self.env.user.employee_ids[0]}')
        current_user = self.env.user.employee_ids and self.env.user.employee_ids[0] or None
        if self.inv_lines_id:
            list_employee_concerned = self.inv_lines_id.immo_inv_id
            for employee_concerned in list_employee_concerned:
                if (current_user.id == employee_concerned.employee_id.id) and (employee_concerned.equipe == 'equipe1'):
                    found.append(True)
            if self.count_found(found) > 0:
                self.write({'badge': 'yellow'})
                # todo Call function to set the Departement and desktop concerned
                # get_dep_ids = self.get_deprt_desktop_concerned()

                # Browse the common departments
                # common_departments = self.env['hr.department'].browse(list(get_dep_ids))

                # for dept in common_departments:
                #   print(f'dept  === {dept.id}')
                #  self.departement_id = dept.id
                # print(f'common_departments  nasssss {common_departments}')
                # Set the computed field
                # self.departement_id = common_departments

                # departements_1 = self.env['hr.department'].browse([])
                # print(f'jkvnsjbvjvjks;vsjkbvjkfbvFBVJKKF    DJNV {departements_1}')

                ## Get the IDs of the departments
                # print(f'self.departement_id {self.departement_id}')
                # print(f'self.departement_id.ids {self.departement_id.ids}')

                # departements_1_ids = set(departements_1.ids)
                # departements_2_ids = set(get_dep_ids.ids)

                # print(f'departements_1_ids nasss {departements_1_ids}')
                # print(f'departements_2_ids nasss {departements_2_ids}')

                ## Find the common IDs
                # common_ids = departements_1_ids.intersection(departements_2_ids)

                ## Browse the common departments
                # common_departments = self.env['hr.department'].browse(list(common_ids))
                # print(f'common_departments  nasssss {common_departments}')
                ## Set the computed field
                # self.common_ids = common_departments
            else:
                self.write({'badge': 'red'})

    # Set the Departement and desktop concerned
    def get_deprt_desktop_concerned(self):
        if self.inv_lines_id:
            get_records = self.inv_lines_id.immo_inv_id
            departements_1 = self.env['hr.department'].browse([1, 3])
            if get_records:
                for record in get_records:
                    if (record.employee_id.id == self.get_employee_user(self.env.user.id).id) \
                            and (record.company_id.id == self.env.company.id) \
                            and (record.equipe == 'equipe1'):
                        print(f'record.departement_id ======== {record.departement_id}')
                        print(f'uyyyyyyyyyyyyyyyy yyy yyy {departements_1}')
                        return record.departement_id

                        # for rec in record.departement_id:
                        # self.departement_id = ''
                        # self.departement_id = rec
                        # print(f'departement_id {rec.id}')
                        # for r in record.desktop_id:
                        # print(f'desktop_id {r.id}')

    # todo Count True in found
    def count_found(self, found):
        count = 0
        for line in found:
            if line == True:
                count += 1
        return count

    # Get Employee for the local user
    def get_employee_user(self, local_user):
        employee_record = self.env['hr.employee'].search([('user_id', '=', local_user)], limit=1)
        if employee_record:
            return employee_record
        else:
            return False

    # Filter the desktops as the admin gives to the agent from 'Créer un nouveau inventaire' menu
    @api.onchange('departement_id')
    def compute_domain_desktop_id(self):
        eec = self.env.context.get('skip_onchange', False)
        print(f'onchange_departement_id called  {eec}')
        if self.env.context.get('skip_onchange', False):
            print('Skipping onchange method due to context')
            return

        print('Executing onchange logic')

        if self.departement_id:
            # Fetching related immo.inv lines
            immo_inv_lines = self.env['immo.inv'].browse(self.inv_lines_id.id).immo_inv_id.mapped('id')
            print(f'immo_inv_lines {immo_inv_lines}')
            # Fetching related departments from immo.inv.lines
            # departments = self.env['hr.department.immo.inv.line.rel'].search([('immo_inv_line_id', 'in', immo_inv_lines)]).mapped('hr_departement_id')
            desktops = self.env['immo.inv.line'].search(
                [('id', '=', immo_inv_lines)]).desktop_id  # .mapped('departement_id')
            print(f'departments {desktops}')

            # Prepare domain to filter departement_id field
            desktops_ids = desktops.ids

            # self.desktop_id = self.departement_id.desktop_ids.id
            return {'domain': {'desktop_id': [
                ('departement_id', '=', self.departement_id.id),
                ('id', 'in', desktops_ids)
            ]}}
        else:
            # Clear departement_id if no agence is selected
            return {'domain': {'desktop_id': []}, 'value': {'desktop_id': False}}

    # Get All asset exist in the departement and not exist on the desktop
    # AND
    # Filter the desktops as the admin gives to the agent from 'Créer un nouveau inventaire' menu
    # @api.onchange('departement_id')
    def _get_assets_departement_departe(self):
        if self.env.context.get('skip_onchange', False):
            self.domain_desktop_id = "[]"
            return

        if self.prevent == True:
            print(f'prevent True exit')
            self.domain_desktop_id = "[]"
            return

        print('heloo departement ')
        # Initializing
        found = []
        # get_assets_data = self.env['account.asset.asset'].browse([])
        if self.departement_id:
            # Clear the desktop list
            self.desktop_id = False
            print(f'hello deprt {self.departement_id}')
            # Clear existing lines
            self.get_inventory_verify_line = [(5, 0, 0)]

            filtered_domain = [
                ('departement_id', '=', 1),  # self.departement_id.id
                # ('desktop_id', '=', False)
            ]
            get_assets_data = self.env['account.asset.asset'].search(filtered_domain)
            print(f'get_assets_data uuuuuuu  {get_assets_data}')
            for get_asset_data in get_assets_data:
                self.truOrFalseUpdateState(found, get_asset_data)

                if self.isTrueOrFalse(found) == 0:
                    self.get_inventory_verify_line = [(0, 0, {
                        'asset_id': get_asset_data.id,
                        'marque': get_asset_data.marque,
                        'genre': get_asset_data.genre,
                        'code_bare': get_asset_data.code_bare,
                        'code_bare_nv': get_asset_data.code_bare_nv,
                        'employee_id': get_asset_data.employee_id.id,
                        'status': 'a_compter'
                    })]

                    # Fetching related immo.inv lines
                    immo_inv_lines = self.env['immo.inv'].browse(self.inv_lines_id.id).immo_inv_id.mapped('id')
                    print(f'immo_inv_lines desktopppppppppppppppppp {immo_inv_lines}')
                    # Fetching related departments from immo.inv.lines
                    # departments = self.env['hr.department.immo.inv.line.rel'].search([('immo_inv_line_id', 'in', immo_inv_lines)]).mapped('hr_departement_id')
                    desktops = self.env['immo.inv.line'].search(
                        [('id', '=', immo_inv_lines)]).desktop_id  # .mapped('departement_id')
                    print(f'desktops desktopppppppppppppppppp desktopppppppppppppppppp {desktops}')

                    # Prepare domain to filter departement_id field
                    desktops_ids = desktops.ids

                    domain_get = [('id', 'in', desktops_ids)]
                    # self.domain_desktop_id = repr(domain_get)

                    # Get the desktops of the selected departement_id
                    # Fetch desktops associated with the selected department
                    desktops_departement_id = self.env['hr.work.location'].search([
                        ('departement_id', '=', self.departement_id.id)
                    ])

                    # List of specific desktop IDs you want to filter by
                    specific_desktop_ids = [4, 5]  # Adjust this list as per your requirement

                    # Filter desktops of the selected department by specific IDs
                    filtered_desktops = desktops_departement_id.filtered(lambda d: d.id in desktops_ids)
                    domain_get = [('id', 'in', filtered_desktops.ids)]
                    # self.domain_desktop_id = repr(domain_get)
                    self.domain_desktop_id = repr(domain_get) if domain_get else "[]"
                else:
                    self.domain_desktop_id = "[]"
                    # Clear departement_id if no agence is selected
                    return {'domain': {'desktop_id': []}, 'value': {'desktop_id': False}}

    # Using code bat to get All departement
    @api.onchange('scan_bat')
    def get_bat(self):
        if self.env.context.get('skip_onchange', False):
            return

        desired_departement_ids = [1]

        if self.scan_bat:
            self.desktop_id = ''
            filtered = [
                ('code_bat', '=', self.scan_bat)
            ]
            get_bats = self.env['hr.department'].search(filtered)
            print(f'get_bat {get_bats}')

            if get_bats:
                departements = get_bats.filtered(lambda d: d.id in desired_departement_ids)
                if departements:
                    print(f'departement jjj {departements}')
                    self.departement_id = departements
                else:
                    self.scan_bat = ''
                    return {
                        'warning': {
                            'title': 'Warning!',
                            'message': "Vous avez pas l'autorisation de compte cette Département",
                        },
                    }

            self.scan_bat = ''
        else:
            self.departement_id = ''
            self.desktop_id = ''

    # Using code bur to get All asset of a departement
    @api.onchange('scan_bur')
    def get_bur(self):
        if self.env.context.get('skip_onchange', False):
            return

        if self.scan_bur:
            self.desktop_id = ''
            filtered = [
                ('code_bur', '=', self.scan_bur),
            ]
            get_burs = self.env['hr.work.location'].search(filtered, limit=1)
            self.desktop_id = get_burs
            self.scan_bur = ''
        else:
            self.desktop_id = ''

    # Get the desktop Assets
    @api.onchange('desktop_id')
    def get_assets_desktop_desktop(self):
        if self.env.context.get('skip_onchange', False):
            return

        print(f'sardina ')
        # Initializing
        found = []
        if self.desktop_id:
            # Clear existing lines
            self.get_inventory_verify_line = [(5, 0, 0)]

            filtered_domain = [
                ('company_name', '=', self.company_id.id),
                ('departement_id', '=', self.departement_id.id),
                ('desktop_id', '=', self.desktop_id.id),
            ]
            get_assets_data = self.env['account.asset.asset'].search(filtered_domain)
            for get_asset_data in get_assets_data:
                self.truOrFalseUpdateState(found, get_asset_data)

                if self.isTrueOrFalse(found) == 0:
                    self.get_inventory_verify_line = [(0, 0, {
                        'asset_id': get_asset_data.id,
                        'marque': get_asset_data.marque,
                        'genre': get_asset_data.genre,
                        'code_bare': get_asset_data.code_bare,
                        'code_bare_nv': get_asset_data.code_bare_nv,
                        'employee_id': get_asset_data.employee_id.id,
                        'status': 'a_compter'
                    })]

        # Return the value

    def isTrueOrFalse(self, found):
        count = 0
        if found:
            for f in found:
                if f == True:
                    count += 1

        return count

    # Searched this get asset if exists on the table
    def truOrFalseUpdateState(self, found, get_asset_data):
        print(f'self.get_inventory_verify_line {self.get_inventory_verify_line}')
        for record in self.get_inventory_verify_line:
            print(f'record {record}')
            for line in record:
                print(f'line {line}')
                asset_id = line.asset_id.id  # Assuming 'asset_id' is a field in 'asset.inventory.verify.line'
                print(f'exist get_asset_data {get_asset_data.id}  asset_id {asset_id} ')
                if get_asset_data.id == asset_id:
                    found.append(True)
                    # update the status ti exist
                    # line.write({'status': 'exist'})
                    line.status = 'exist'
                else:
                    found.append(False)

    # Get asset data
    @api.onchange('code_bare')
    def get_assets(self):
        if self.env.context.get('skip_onchange', False):
            return

        # Initializing
        found = []
        if self.code_bare:
            domain = [
                '&', '&',
                ('code_bare', '=', self.code_bare),
                ('company_name', '=', self.company_id.id), #self.env.company.id
                '|',
                ('departement_id', '=', self.departement_id.id),
                ('desktop_id', '=', self.desktop_id.id)
            ]
            get_asset_data = self.env['account.asset.asset'].search(domain, limit=1)
            print(f'waaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaay {get_asset_data.id}')
            if get_asset_data:
                # Clear existing lines
                # self.get_inventory_verify_line = [(5, 0, 0)]

                # Searched this get asset if exists on the table
                self.truOrFalseUpdateState(found, get_asset_data)

            #
            if self.isTrueOrFalse(found) == 0:
                self.get_inventory_verify_line = [(0, 0, {
                    'asset_id': get_asset_data.id,
                    'marque': get_asset_data.marque,
                    'genre': get_asset_data.genre,
                    'code_bare': get_asset_data.code_bare,
                    'code_bare_nv': get_asset_data.code_bare_nv,
                    'employee_id': get_asset_data.employee_id.id,
                    'status': 'added'
                })]

        self.code_bare = ''

    @api.depends('asset_id', 'code')
    def _compute_name(self):
        for record in self:
            if record.asset_id:
                data = [record.code]
        return data

    @api.model
    def compute_and_display_differencesAA(self, selected_records=None):
        if selected_records is None:
            # If no specific records are selected, get all records
            selected_records = self.env['asset.inventory.verify'].search([])

        # Ensure selected_records is a recordset
        if not isinstance(selected_records, models.BaseModel):
            selected_records = self.env['asset.inventory.verify'].browse(selected_records)

        # Filter selected records where asset_verify is False
        assets_to_compute = selected_records.filtered(lambda record: not record.asset_verify)

        if not assets_to_compute:
            # No records with asset_verify=False, redirect to Asset Inventory Differences menu
            menu_action = self.env.ref('altex_imobilisation.menu_asset_inventory_difference').read()[0]
            return menu_action

        # Your logic to compute differences for assets_to_compute
        differences = self.env['asset.inventory.difference']

        for asset_verify_record in assets_to_compute:
            # Check if there is a corresponding record in account.asset.asset
            asset_record = self.env['account.asset.asset'].search([
                ('id', '=', asset_verify_record.asset_id.id),
                ('employee_id', '=', asset_verify_record.employee_id.id),
                ('company_id', '=', asset_verify_record.company_id.id),
                ('departement_id', '=', asset_verify_record.departement_id.id),
                ('desktop_id', '=', asset_verify_record.desktop_id.id),
            ])

            if not asset_record:
                # If no corresponding record found, add to differences
                differences |= self.env['asset.inventory.difference'].create({
                    'id': asset_verify_record.asset_id.id,
                    'employee_id': asset_verify_record.employee_id.id,
                    'company_id': asset_verify_record.company_id.id,
                    'departement_id': asset_verify_record.departement_id.id,
                    'desktop_id': asset_verify_record.desktop_id.id,
                    'code': asset_verify_record.code,
                    'code_site': asset_verify_record.code_site,
                    'code_bat': asset_verify_record.code_bat,
                    'code_inv': asset_verify_record.code_inv,
                    'code_buro': asset_verify_record.code_buro,
                    'num_niv': asset_verify_record.num_niv,
                    'compte_g': asset_verify_record.compte_g,
                    'code_bare': asset_verify_record.code_bare,
                    'qte': asset_verify_record.qte,
                })

        if differences:
            # Open a new window with the computed differences
            action = self.env.ref('altex_imobilisation.action_asset_inventory_difference').read()[0]
            action['domain'] = [('id', 'in', differences.ids)]
            return action
        else:
            # No records with asset_verify=False, redirect to Asset Inventory Differences menu
            menu_action = self.env.ref('altex_imobilisation.menu_asset_inventory_difference').read()[0]
            return menu_action
