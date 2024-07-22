import barcode
from barcode.writer import ImageWriter

from odoo import fields, models, api
import base64
from io import BytesIO


class IMVerify1(models.Model):
    _name = 'asset.inventory.verify.line2'

    asset_inventory_verify = fields.Many2one('asset.inventory.verify2', string='Asset Inventory Verify Line')

    asset_id = fields.Many2one('account.asset.asset', string='DESIGNATION', required=True)
    asset_id_tmp = fields.Many2one('temp.imobilisation', string='Nom d\'immobilisation1', required=False)
    # asset_id = fields.Integer(string='Nom d\'immobilisation1', required=True)
    #code = fields.Char(string='CODE', default="code hhh", required=True)
    code_inv = fields.Char(string='CODE INV', required=False)
    compte_g = fields.Char(string='COMPTE G', required=False)
    code_bare_nv = fields.Char(string='Nouveaux BARCODE', required=False, unique=True)
    code_bare = fields.Char(string='Ancian BARCODE', required=False, unique=True)
    marque = fields.Char(string="Marque", placeholder="Marque")
    genre = fields.Char(string="Genre", placeholder="Genre")
    qte = fields.Integer(string='Quantite', default=1, required=False)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=False)
    status = fields.Selection(
        [('exist', 'EXISTE'), ('not_exist', 'EXISTE PAS'), ('added', 'En Plus'), ('a_compter', 'A Compter')],
        default='not_exist')

    sequence_number = fields.Integer(string='Sequence Number', default=1)
    barcode_image = fields.Binary(string="Barcode Image", readonly=True)

    def print_code_bare(self):
        return self.env.ref('altex_imobilisation.barcode_report_action').report_action(self.id)

    def _create_sequence(self):
        sequence = self.env['ir.sequence'].sudo().create({
            'name': 'Asset Inventory Verify Line Sequence',
            'code': 'asset.inventory.verify.line.sequence',
            'padding': 7,
            'prefix': 'BPH',
        })
        return sequence.id

    def generate_code_bare(self):
        last_record = self.search([], order="sequence_number desc", limit=1)
        next_sequence = last_record.sequence_number + 1 if last_record else 1
        self.code_bare_nv = 'ENTMV   BPH{0:07d}'.format(next_sequence)
        self.sequence_number = next_sequence

        print(f'1')
        # Generate barcode image
        self.generate_barcode_image()
        print('accesss to the def')

    def generate_barcode_image(self):
        barcode_class = barcode.get_barcode_class('code128')  # get_barcode_class('code128')
        code = barcode_class(self.code_bare_nv, writer=ImageWriter())
        buffer = BytesIO()
        code.write(buffer)
        image_data = base64.b64encode(buffer.getvalue())
        self.barcode_image = image_data
        # if isinstance(self.barcode_image, bytes):
        #    self.barcode_image = base64.b64encode(self.barcode_image).decode('utf-8')

    # todo Make status exist
    def status_exist(self):
        self.write({'status': 'exist'})
        self.status = 'exist'

    # todo Make status not exist
    def status_notExist(self):
        self.write({'status': 'not_exist'})
        self.status = 'not_exist'


#class ReportBarcode2(models.AbstractModel):
#   _name = 'report.altex_imobilisation.barcode_report_template'
#   _description = 'Barcode Report2'

#   @api.model
#   def _get_report_values(self, docids, data=None):
#       docs = self.env['asset.inventory.verify.line2'].browse(docids)
#       print(f'image printing ....')
#       print(docs.barcode_image)
#       return {
#           'doc_ids': docids,
#           'doc_model': 'asset.inventory.verify.line2',
#           'docs': docs,
#           'doc': docs[0] if docs else False,
#       }
