# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IMDepartement(models.Model):
    _inherit = "hr.department"
    # _rec_name = "code_bat"

    code_bat = fields.Char(string="BAT")
    total_bureaux = fields.Integer(compute='_compute_total_bureaux', string='Total Bureaux')

    # The relation between Departement and Desktop
    desktop_ids = fields.One2many('hr.work.location', 'departement_id', string="Bureaux")

    def _compute_total_bureaux(self):
        emp_data = self.env['hr.work.location']._read_group([('departement_id', 'in', self.ids)], ['departement_id'],
                                                            ['__count'])
        result = {department.id: count for department, count in emp_data}
        for department in self:
            department.total_bureaux = result.get(department.id, 0)

    def action_my_custom_action(self):
        # Add your custom logic here
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Action',
            'view_mode': 'tree,form',
            'res_model': 'hr.department',
            'target': 'current',
        }
