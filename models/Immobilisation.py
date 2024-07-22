# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlrd
import base64


class Imobilisation(models.Model):
    _inherit = "account.asset.asset"
    _rec_name = 'name'

    name = fields.Char(string="DESIGNATION", required=False)
    code = fields.Char(string='CODE D\'IMOBILISATION', required=False, readonly=False)
    code_inv = fields.Char(string='INV')
    compte_g = fields.Char(string='COMPTE G')
    code_bare = fields.Char(string='CODE BARE', unique=True)
    code_bare_nv = fields.Char(string='Nouveaux BARCODE', unique=True)
    qte = fields.Integer(string="Quantity", default=1)
    desc = fields.Char(string="Description")
    num_garante = fields.Char(string="Num Garantie")
    marque = fields.Char(string="Marque", placeholder="Marque")
    genre = fields.Char(string="Genre", placeholder="Genre")
    num_serie = fields.Char(string="Num Série", placeholder="Num Série")
    category_id = fields.Many2one('account.asset.category',
                                  string='Category Immo',
                                  required=True, change_default=True,
                                  readonly=False, )
    date = fields.Date(string='Date Aquisition', required=True, readonly=False,
                       default=fields.Date.context_today)

    date_amortissement = fields.Date(string='Date Amortissement', required=True, readonly=False,
                                     default=fields.Date.context_today)

    value = fields.Float(string='Gross Value', required=True, readonly=False,
                         digits=0)
    salvage_value = fields.Float(string='Salvage Value', digits=0,
                                 readonly=False,
                                 help="It is the amount you plan to have that "
                                      "you cannot depreciate.")

    employee_id = fields.Many2one('hr.employee', string="Employee", placeholder="Employée")
    company_name = fields.Many2one('res.company', string="SITE", placeholder="Company")
    departement_id = fields.Many2one('hr.department', string="BAT", placeholder="Département")
    desktop_id = fields.Many2one('hr.work.location', string="BUR", placeholder="Bureaux")
    categuorie_article = fields.Many2one('product.category', string="Categuorie Article", required=False,
                                         placeholder="Catéguorie Article")
    product_id = fields.Many2one('product.product', string='Produit Lié', placeholder="Produit")
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False, placeholder="")
    note_commision = fields.Text(string="Note de Commission", placeholder="Note du Commission")
    date_commission = fields.Date(string="Date Commission", placeholder='12/05/2024')
    commission_id = fields.One2many('p.commission', 'get_asset_ids', string="Membre Commission",
                                    placeholder="Membre de Commission")
    etat = fields.Selection([('verte', 'Trés Bien'), ('orange', 'Bien'), ('rouge', 'A Réformer')], required=False,
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

    file = fields.Binary(string='File')

    def calc_dotation_number_of_entries(self, mantant_aquisition, taux_amor):
        return mantant_aquisition * (int(taux_amor) / 100)

    def format_number(self,number_str):
        number_str = str(int(float(number_str)))

        # Remove leading zeros
        number_str = number_str.lstrip('0')

        # Format the number to be exactly 6 digits long by adding leading zeros if necessary
        formatted_number = number_str.zfill(6)

        # Concatenate with prefix
        result = f"Q01{formatted_number}"

        return result

    def complter_generer_codebare(self):
        print(f'a')
        assets = self.env['account.asset.asset'].search([])
        print(f'assets {assets}')
        for aa in assets:
            print(f'loop {aa}')
            get_code_br = aa.code_bare
            new_br_code = self.format_number(get_code_br)
            print(f'new barcode {new_br_code}')

            # Update the code_bare field for all found records
            aa.write({'code_bare': new_br_code})
            #break


    def import_data(self):
        try:
            # raise UserError(_("This method should only be called for a single asset record."))

            decoded_data = base64.decodebytes(self.file)
            excel_file = xlrd.open_workbook(file_contents=decoded_data)

            sheet_indices = [2]

            for sheet_index in sheet_indices:
                # Assuming data is in the first sheet
                sheet = excel_file.sheet_by_index(sheet_index)

                for row_index in range(1, sheet.nrows - 1):  # Skip header row
                    print(f'sheet.nrows {sheet.nrows}')
                    print(f'Row number is : {row_index}')

                    print('Hi 01')
                    row = sheet.row_values(row_index)

                    get_asset_searched = self.env['account.asset.asset'].search(
                        [('code', '=', row[0])])
                    print(f'coddddddddddddddddddde {get_asset_searched}')
                    print(f'coddddddddddddddddddde {get_asset_searched.code}')
                    if not get_asset_searched:

                        print('Hi 02')
                        # get categuorie_id

                        print('Hi 04')

                        print('Hi 05')
                        print(f'Date is {self.convert_to_date(row[11])}')

                        print('Hi 06')
                        get_code_bat = self.getCodeBat(row[2], row[1])
                        get_site = self.getCodeSite(row[1])
                        method_number = 100 / int(row[15])
                        # todo Calculer 'Dotation {salvage_value} et 'Number of entries' dans Type Immobilisation '

                        data = {
                            'name': row[7],
                            'code_bare': row[0],
                            'company_name': get_site,
                            'departement_id': get_code_bat,
                            # 'num_niv': row[3],
                            'desktop_id': self.getCodeBur(row[4], row[3], row[14], get_code_bat),
                            'code_inv': row[3],
                            'compte_g': row[6],
                            'category_id': self.getCateguorieID(row[6], method_number, get_site),
                            'marque': row[8],
                            'genre': row[9],
                            'date': self.convert_to_date(row[11]),
                            'qte': row[12],
                            'value': row[13],
                            'date_amortissement': self.convert_to_date(row[11]),
                            # 'local': row[17],
                            # 'first_depreciation_manual_date': self.convert_to_date(row[22]),
                            'salvage_value': self.calc_dotation_number_of_entries(row[13], row[15]),
                            'currency_id': 111,
                            'categuorie_article': 1  # 9986
                        }

                        # Add Navire & Trajet
                        # data['navire'] = self.navire
                        # data['trajet_id'] = self.trajet_id.id

                        self.env['account.asset.asset'].create(data)
                    else:
                        print(f'Cete immo est deja exist')

            # return {'type': 'ir.actions.act_window_close'}
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Données importées avec succès!',
                    'type': 'success',  # Use 'success', 'warning', 'danger', 'info'
                }
            }
        except Exception as e:
            # raise UserError(f"An error occurred: {e}")
            print(f"The error is {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Danger',
                    'message': f"Il y a un problème : {e}",
                    'type': 'danger',  # Use 'success', 'warning', 'danger', 'info'
                }
            }

    # get code site
    def getCodeSite(self, input):
        company = self.env['res.company'].search([('code_site', '=', input)])
        if company:
            print(f'code site agence_id = {company.id}')
            return company.id

        new_data = {
            'name': input,
            'street': '',
            'city': '',
            'country_id': 1,
            'code_site': input
        }
        company = self.env['res.company'].sudo().create(new_data)
        return company.id

    def getCodeBat(self, input, code_site):
        get_code_bat = self.env['hr.department'].search([('code_bat', '=', input)])

        if get_code_bat:
            print(f'Found existing department with ID: {get_code_bat.id}')
            return get_code_bat.id

        company_id = self.getCodeSite(code_site)

        # Create the new department using sudo()
        new_data = {
            'name': input,
            'manager_id': self.get_employee_user(self.env.user.id),  # Set the current user as the manager
            'company_id': company_id,
            'code_bat': input
        }

        new_department = self.env['hr.department'].sudo().create(new_data)
        print(f'Department created with ID: {new_department.id}')
        return new_department.id

    def import_data22(self):
        try:
            # raise UserError(_("This method should only be called for a single asset record."))

            decoded_data = base64.decodebytes(self.file)
            excel_file = xlrd.open_workbook(file_contents=decoded_data)

            sheet_indices = [0]

            for sheet_index in sheet_indices:
                # Assuming data is in the first sheet
                sheet = excel_file.sheet_by_index(sheet_index)

                for row_index in range(1, sheet.nrows - 1):  # Skip header row
                    print(f'sheet.nrows {sheet.nrows}')
                    print(f'Row number is : {row_index}')
                    print('Hi 01')
                    row = sheet.row_values(row_index)
                    # Assuming column order: field1, field2, ..., field7
                    print('Hi 02')
                    # get categuorie_id

                    print('Hi 04')

                    print(f'Categuroie ID is = {self.getCateguorieID(row[7])}')

                    print('Hi 05')
                    print(f'Date is {self.convert_to_date(row[11])}')

                    print('Hi 06')
                    get_code_bat = self.getCodeBat(row[2], row[1])
                    data = {
                        'code': row[0],
                        'company_name': self.getCodeSite(row[1]),
                        'departement_id': get_code_bat,
                        # 'num_niv': row[3],
                        'desktop_id': self.getCodeBur(row[4], row[3], row[17], get_code_bat),
                        'code_inv': row[5],
                        'compte_g': row[6],
                        'category_id': self.getCateguorieID(row[7]),
                        'marque': row[8],
                        'genre': row[9],
                        'date': self.convert_to_date(row[11]),
                        'qte': row[12],
                        'value': row[16],
                        'date_amortissement': self.convert_to_date(row[22]),
                        # 'local': row[17],
                        # 'first_depreciation_manual_date': self.convert_to_date(row[22]),
                        'salvage_value': row[24],
                        'currency_id': 111,
                        'categuorie_article': 1  # 9986
                    }

                    # Add Navire & Trajet
                    # data['navire'] = self.navire
                    # data['trajet_id'] = self.trajet_id.id

                    self.env['account.asset.asset'].create(data)

            # return {'type': 'ir.actions.act_window_close'}
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Données importées avec succès!',
                    'type': 'success',  # Use 'success', 'warning', 'danger', 'info'
                }
            }
        except Exception as e:
            # raise UserError(f"An error occurred: {e}")
            print(f"The error is {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Danger',
                    'message': f"Il y a un problème : {e}",
                    'type': 'danger',  # Use 'success', 'warning', 'danger', 'info'
                }
            }

    # get code site
    def getCodeSite22(self, input):
        company = self.env['res.company'].search([('code_site', '=', input)])
        if company:
            print(f'code site agence_id = {company.id}')
            return company.id

        new_data = {
            'name': input,
            'street': '',
            'city': '',
            'country_id': 1,
            'code_site': input
        }
        company = self.env['res.company'].sudo().create(new_data)
        return company.id

    def getCodeBat22(self, input, code_site):
        get_code_bat = self.env['hr.department'].search([('code_bat', '=', input)])

        if get_code_bat:
            print(f'Found existing department with ID: {get_code_bat.id}')
            return get_code_bat.id

        company_id = self.getCodeSite(code_site)

        # Create the new department using sudo()
        new_data = {
            'name': input,
            'manager_id': self.get_employee_user(self.env.user.id),  # Set the current user as the manager
            'company_id': company_id,
            'code_bat': input
        }

        new_department = self.env['hr.department'].sudo().create(new_data)
        print(f'Department created with ID: {new_department.id}')
        return new_department.id

    # Get Employee for the local user
    def get_employee_user(self, local_user):
        employee_record = self.env['hr.employee'].search([('user_id', '=', local_user)], limit=1)
        if employee_record:
            return employee_record.id
        else:
            # Create an employee for the user if not found
            user = self.env['res.users'].browse(local_user)
            new_employee = self.env['hr.employee'].create({
                'name': user.name,
                'user_id': user.id,
            })
            return new_employee.id

    # get code bur
    def getCodeBur(self, code_bur, code_niv, local, code_bat):
        getIDdesktop = None
        get_code_bur = self.env['hr.work.location'].search([('code_bur', '=', code_bur)])
        print('hi get_code_bur')
        if get_code_bur:
            print(f'hi found code_bur {get_code_bur.id}')
            return get_code_bur.id

        if not get_code_bur:
            print('hi not found code_bur')
            new_data = {
                'name': local,
                'address_id': 1,
                'code_bur': code_bur,
                'code_niv': code_niv,
                'departement_id': code_bat
            }
            self.env['hr.work.location'].create(new_data)
            getIDdesktop = self.env['hr.work.location'].search(
                [('code_bur', '=', code_bur)])
            print(f'get id desktop {getIDdesktop}')

        return getIDdesktop.id

    # Get Categuorie ID
    def getCateguorieID(self, input, taux_amortissement, site):
        get_categuorie_id = self.env['account.asset.category'].search(
            [('name', '=', input)])
        if not get_categuorie_id:
            new_categuorie_data = {
                'active': True,
                'name': input,
                'account_asset_id': 161,
                'account_depreciation_id': 161,
                'account_depreciation_expense_id': 162,
                'journal_id': 2,
                'company_id': 1,
                'method': 'linear',
                'method_number': taux_amortissement,
                'method_period': 12,
                'method_progress_factor': 0.3,
                'method_time': 'number',
                'prorata': False,
                'open_asset': False,
                'group_entries': False,
                'type': 'purchase',
                'price': 0.00,
                # 'date_first_depreciation': 'manual',
            }
            self.env['account.asset.category'].create(new_categuorie_data)
            print('Hi 03-02')
            get_categuorie_id = self.env['account.asset.category'].search(
                [('name', '=', input)])
            print('Hi 03-03')
        return get_categuorie_id.id

    @api.model
    def create(self, vals):
        insert = False
        asset = super(Imobilisation, self.with_context(mail_create_nolog=True)).create(vals)
        asset.sudo().compute_depreciation_board()
        print('Enter product 00')
        # Create or find a product template
        product_template = self.env['product.template'].search([
            ('name', '=', asset.name),
            ('categ_id', '=', asset.categuorie_article.id),  # asset.categuorie_article.id
        ], limit=1)
        print(f'product_template = {product_template}')
        print('Enter product 01')
        if not product_template:
            product_template = self.env['product.template'].create({
                'name': asset.name,
                'type': 'product',
                'categ_id': asset.categuorie_article.id,  # asset.categuorie_article.id,
                'list_price': asset.value,
                'default_code': asset.code_bare,
            })
            print(f'product_template = {product_template}')
            insert = True
            print('Enter product 02')

        else:
            print("The product template is already exists")
        print('Enter product 03')

        # todo update is_immo make is True
        product_template.write({'is_immo': True})

        print(f'catgory_id : {asset.category_id}')
        # todo update asset_category_id to getbthe value of category_id
        product_template.write({'asset_category_id': asset.category_id})

        # Check if a product variant already exists
        product_variant = self.env['product.product'].search([
            ('product_tmpl_id', '=', product_template.id),
            ('default_code', '=', asset.code_bare),
        ], limit=1)
        print(f'product_variant = {product_variant}')

        print('Enter product 04')

        if insert:
            insert = False
            if not product_variant:
                # Create a product variant linked to the asset
                product_variant = self.env['product.product'].create({
                    'product_tmpl_id': product_template.id,
                    'default_code': asset.code_bare,
                })
                insert = True
                print(f'product_variant = {product_variant}')
                print('Enter product 05')
            else:
                print("The product variant is already exists")
                print('Enter product 06')

            print('Enter product 07')
            # Link the created product to the asset
            asset.write({'product_id': product_variant.id})
            asset.write({'state_life': 'en_cours_affecter'})
            # self.state_life = 'en_cours_affecter'
            print('Enter product 08')

        return asset

    # En cours utiliation
    def in_use(self):
        self.state_life = 'in_use'

    # @api.multi
    def validate(self):
        res = super(Imobilisation, self).validate()
        return res

    # Affecter Immo
    def affect_immo(self):
        self.write({'state_life': 'in_use'})

    # to do def maintenance
    def maintenance(self):
        self.write({'state_life': 'maintenance'})

    # to do def awaiting_approval
    def awaiting_approval(self):
        self.write({'state_life': 'awaiting_approval'})

    # to do def retired
    def retired(self):
        self.write({'state_life': 'retired'})

    # to do def attente_comission
    def attente_comission(self):
        self.write({'state_life': 'attente_comission'})

    # to do def wait_sold
    def wait_sold(self):
        self.write({'state_life': 'wait_sold'})

    # to do def sold
    def sold(self):
        self.write({'state_life': 'sold'})

    # to do def scrapped
    def scrapped(self):
        self.write({'state_life': 'scrapped'})

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id,
                           f'CODE = {record.code} * CATEGORIE = {record.category_id.name}  * MARQUE = {record.marque} * GENRE = {record.genre} '))
            # result.append((record.id, f'CODE = {record.code}  * SITE = {record.code_site} * CATEGORIE = {record.category_id.name}  * MARQUE = {record.marque} * GENRE = {record.genre} '))
        return result

        # Convert to date

    def convert_to_date(self, input):
        date_string = input
        date_format = "%Y-%m-%d"  # Format of the date string

        try:
            date_object = xlrd.xldate.xldate_as_datetime(date_string, 0)
            print("Date converted to datetime object:", date_object)
            return date_object
        except ValueError:
            print("Error: Unable to parse date.")

    # Asset move to sell table
    def move_to_sell(self):
        """Move the current asset to the 'to sell' table."""
        AssetMoveToSell = self.env['asset.move.tosell']

        # Ensure there is only one record (should be the case for a single record, but added the check for safety)
        if len(self) != 1:
            raise UserError(_("This method should only be called for a single asset record."))

        asset = self

        # Extracting the last depreciation line for additional fields
        last_depreciation_line = asset.depreciation_line_ids[-1]

        get_employee = False
        if asset.employee_id:
            get_employee = asset.employee_id.id

        print(f'etablissement {asset.company_name.id}')
        print(f'employee {get_employee}')

        # Create a record in the 'asset.move.tosell' table
        move_to_sell_vals = {
            'asset_code': asset.code,
            # 'asset_compte_g': asset.company_name.code_site,
            'asset_code_bat': asset.departement_id.code_bat,
            'asset_code_inv': asset.code_inv,
            'asset_code_bur': asset.desktop_id.code_bur,
            'asset_code_niv': asset.desktop_id.code_niv,
            'asset_compte_g': asset.compte_g,
            'asset_code_bare': asset.code_bare,
            'qte': 1,
            'employee': get_employee,
            'societe': asset.company_name.id,
            'departement': asset.departement_id.id,
            'desktop': asset.desktop_id.id,
            'sale_order_id': asset.sale_order_id.id,
            # 'is_sold': asset.is_sold,
            # 'is_disposed': asset.is_disposed,
            'value': asset.value,
            'currency_id': asset.currency_id.id,
            # 'company_id': asset.company_id.id,
            # 'note': asset.note,
            'category': asset.category_id.id,
            'partner_id': asset.partner_id.id,
            'asset_id': asset.id,
            # 'value_residual': asset.value_residual,
            'salvage_value': asset.salvage_value,
            # 'amount': last_depreciation_line.amount,
            # 'remaining_value': last_depreciation_line.remaining_value,
            # 'depreciated_value': last_depreciation_line.depreciated_value,
            # 'depreciation_date': last_depreciation_line.depreciation_date,
            'product_id': asset.product_id,
            'price_to_sell': asset.value,
        }

        move_to_sell = AssetMoveToSell.create(move_to_sell_vals)

        # Mark the original asset as sold
        # asset.write({'is_sold': True, 'sale_order_id': False})  # Update the values as needed

        # Update the state to move_to_sell it mean marked as moved to move_to_sell table
        self.write({'state_life': 'wait_sold'})

        # Open the view for the created record
        action = self.env.ref('altex_imobilisation.action_asset_move_tosell')
        result = action.read()[0]
        result['res_id'] = move_to_sell.id
        return result

    #
    def _compute_etat_color(self):
        for record in self:
            if record.etat == 'verte':
                record.etat_color = 'green'
            elif record.etat == 'orange':
                record.etat_color = 'orange'
            elif record.etat == 'rouge':
                record.etat_color = 'red'
