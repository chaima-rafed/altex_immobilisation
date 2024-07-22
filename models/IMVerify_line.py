import barcode
from barcode.writer import ImageWriter

from odoo import fields, models, api
import base64
from io import BytesIO


class IMVerify1(models.Model):
    _name = 'asset.inventory.verify.line1'

    asset_inventory_verify = fields.Many2one('asset.inventory.verify1', string='Asset Inventory Verify Line')

    asset_id = fields.Many2one('account.asset.asset', string='DESIGNATION', required=True)
    asset_id_tmp = fields.Many2one('temp.imobilisation', string='Nom d\'immobilisation1', required=False)
    # asset_id = fields.Integer(string='Nom d\'immobilisation1', required=True)
    # code = fields.Char(string='CODE', default="code hhh", required=True)
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
    barcode_image = fields.Binary(string="Barcode Image")
    old_barcode_image = fields.Binary(string="Ancian Barcode Image")

    def print_code_bare(self):
        return self.env.ref('altex_imobilisation.barcode_report_action').report_action(self.id)

    def print_ancian_code_bare(self):
        #generate the image_barcode
        self.generate_old_barcode_image()
        return self.env.ref('altex_imobilisation.old_barcode_report_action').report_action(self.id)

    def _create_sequence(self):
        sequence = self.env['ir.sequence'].sudo().create({
            'name': 'Asset Inventory Verify Line Sequence',
            'code': 'asset.inventory.verify.line.sequence',
            'padding': 7,
            'prefix': 'PA01-',
        })
        return sequence.id

    #todo Generate a new code bare
    def generate_code_bare(self):
        date_aquisition = self.asset_id.date
        year_aqui = date_aquisition.strftime('%Y')
        last_record = self.search([], order="sequence_number desc", limit=1)
        next_sequence = last_record.sequence_number + 1 if last_record else 1
        self.code_bare_nv = 'PA01-'+year_aqui+'-{0:07d}'.format(next_sequence)
        self.sequence_number = next_sequence

        print(f'1')
        # Generate barcode image
        self.generate_barcode_image()
        print('accesss to the def')

    # todo Generate a new code bare
    def generate_barcode_image(self):
        if self.code_bare_nv:
            barcode_class = barcode.get_barcode_class('code128')
            code = barcode_class(self.code_bare_nv, writer=ImageWriter())
            buffer = BytesIO()
            code.write(buffer)
            image_data = base64.b64encode(buffer.getvalue())
            self.barcode_image = image_data
            self._cr.commit()  # Ensure the transaction is committed
            print(f'image_data: {image_data}')
            print(f'self.barcode_image: {self.barcode_image}')

    #todo Generate an ancian image for an existing barcode (old)
    def generate_old_barcode_image(self):
        if self.code_bare:
            barcode_class = barcode.get_barcode_class('code128')
            code = barcode_class(self.code_bare, writer=ImageWriter())
            buffer = BytesIO()
            code.write(buffer)
            image_data = base64.b64encode(buffer.getvalue())
            self.old_barcode_image = image_data
            self._cr.commit()  # Ensure the transaction is committed
            print(f'image_data: {image_data}')
            print(f'self.barcode_image: {self.barcode_image}')

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


class ReportBarcode(models.AbstractModel):
    _name = 'report.altex_imobilisation.barcode_report_template'
    _description = 'Barcode Report1'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['asset.inventory.verify.line1'].browse(docids)
        print(f'doc.barcode_image: {docs.barcode_image}')
        print(f'doc.old_barcode_image: {docs.old_barcode_image}')
        return {
            'doc_ids': docids,
            'doc_model': 'asset.inventory.verify.line1',
            'docs': docs,
            'doc': docs[0] if docs else False,
        }


#class OldReportBarcode(models.AbstractModel):
#    _name = 'report.altex_imobilisation.old_barcode_report_template'
#    _description = 'OLD Barcode Report'
#
#    @api.model
#    def _get_report_values(self, docids, data=None):
#        docs = self.env['asset.inventory.verify.line1'].browse(docids)
#        for doc in docs:
#            print(f'doc.barcode_image: {doc.barcode_image}')
#        return {
#            'doc_ids': docids,
#            'doc_model': 'asset.inventory.verify.line1',
#            'docs': docs,
#            'doc': docs[0] if docs else False,
#        }
