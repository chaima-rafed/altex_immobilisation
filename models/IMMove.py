from odoo import api, fields, models, _
import string
from odoo.exceptions import ValidationError
import copy
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class IMMove(models.Model):
    _name = "asset.move"
    _description = "Asset Move"

    name = fields.Char(string='REF D\'emplacement', default=lambda self: _("New"), copy=False, readonly=True,
                       required=False)
    from_company = fields.Many2one('res.company', string='Du SITE', required=False)
    from_departement_id = fields.Many2one('hr.department', string='Du BAT', required=False)
    from_desktop_id = fields.Many2one('hr.work.location', string='Du BUR', required=False)
    asset_id = fields.Many2one('account.asset.asset', string='Immobilisation', required=True)
    to_company_id = fields.Many2one('res.company', string='À SITE', required=False)
    to_departement_id = fields.Many2one('hr.department', string='À BAT', required=False)
    to_desktop_id = fields.Many2one('hr.work.location', string='À BUR', required=False)
    from_employee_id = fields.Many2one('hr.employee', string='De l\'Employé', required=False)
    to_employee_id = fields.Many2one('hr.employee', string='À l\'Employé', required=False)
    date_move = fields.Date(string='Date De Mouvement', required=False, default=fields.Date.context_today)

    code = fields.Char(string='CODE')
    code_inv = fields.Char(string='CODE INV')
    compte_g = fields.Char(string='COMPTE G')
    code_bare = fields.Char(string='CODE BARE')
    """state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], string='State', track_visibility='onchange', default='draft', copy=False)"""

    @api.model
    def create(self, vals):
        # print(f"vals create est = {vals} and self = {self} \n")
        if vals.get('name', _("New")) == _("New"):
            vals['name'] = self.env['ir.sequence'].next_by_code('asset.move') or 'New'
        result = super(IMMove, self).create(vals)
        ## Employee Code
        if vals.get('asset_id', False):
            if result.asset_id.employee_id != result.from_employee_id:
                raise ValidationError(_(
                    "L'employé actuel et l'employé de provenance doivent être les mêmes lors de la création de l'immobilisation."))
            # Move Employee to asset.employee table
            result.asset_id.employee_id = result.to_employee_id

        # Location code
        if vals.get('to_company_id', False) or vals.get('to_departement_id', False) or vals.get('to_desktop_id', False):
            # Move location to asset.location table
            result.asset_id.company_name = result.to_company_id
            result.asset_id.departement_id = result.to_departement_id
            result.asset_id.desktop_id = result.to_desktop_id

        return result

    def write(self, vals):
        if vals.get('name', _("New")) == _("New"):
            vals['name'] = self.env['ir.sequence'].next_by_code('asset.move') or 'New'
        result = super(IMMove, self).create(vals)
        ## Employee Code
        if vals.get('asset_id', False):
            if result.asset_id.employee_id != result.from_employee_id:
                raise ValidationError(_(
                    "L'employé actuel et l'employé de provenance doivent être les mêmes lors de la création de l'immobilisation."))
            # Move Employee to asset.employee table
            result.asset_id.employee_id = result.to_employee_id

        # Location code
        if vals.get('to_company_id', False) or vals.get('to_departement_id', False) or vals.get('to_desktop_id', False):
            # Move location to asset.location table
            result.asset_id.company_name = result.to_company_id
            result.asset_id.departement_id = result.to_departement_id
            result.asset_id.desktop_id = result.to_desktop_id

        return result

    def action_move(self):
        for move in self:
            move.asset_id.current_loc_id = move.to_loc_id and move.to_loc_id.id or False
            move.state = 'done'
        return True

    # Get other fields of selected Asset
    @api.onchange('asset_id')
    def get_othe_fields(self):
        if self.asset_id:
            # Fetch the value of the 'code' field from the selected asset
            self.code = self.asset_id.code
            self.code_inv = self.asset_id.code_inv
            self.compte_g = self.asset_id.compte_g
            self.code_bare = self.asset_id.code_bare
            self.from_employee_id = self.asset_id.employee_id.id
            self.from_company = self.asset_id.company_name.id
            self.from_departement_id = self.asset_id.departement_id.id
            self.from_desktop_id = self.asset_id.desktop_id.id

        else:
            # Clear the 'code' field if no asset is selected
            self.code = ''
            self.code_inv = ''
            self.compte_g = ''
            self.code_bare = ''
            self.from_employee_id = False
            self.from_company = False
            self.from_departement_id = False
            self.from_desktop_id = False

    #Get to_departement company
    @api.onchange('to_company_id')
    def get_departement_company(self):
        if self.to_company_id:
            self.to_departement_id = self.asset_id.departement_id.id
            self.to_desktop_id = self.asset_id.desktop_id.id
        else:
            self.to_departement_id = False
            self.to_desktop_id = False

    #Get to_desktop departement
    @api.onchange('to_departement_id')
    def get_desktop_departement(self):
        if self.to_departement_id:
            self.to_desktop_id = self.asset_id.desktop_id.id
        else:
            self.to_desktop_id = False