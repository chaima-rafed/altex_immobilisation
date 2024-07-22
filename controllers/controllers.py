from odoo import http
from odoo.http import request
from odoo.tools import json


class MyAPI(http.Controller):

    #Get Asset data
    @http.route('/api/get_data', auth='none', methods=['GET'], csrf=False, type='http')
    def get_data(self, **kwargs):
        print(f'hi nassreddine')
        try:

            data = []
            # Example: Fetch records in batches of 100
            offset = 0
            limit = 100
            while True:
                records = http.request.env['account.asset.asset'].search([], offset=offset, limit=limit)
                if not records:
                    break

                for record in records:
                    data.append({
                        'id': record.id,
                        'name': record.name,
                        'code': record.code,
                        'desc': record.desc,
                        'code_inv': record.code_inv,
                        'compte_g': record.compte_g,
                    })
                offset += limit
            print(f'finnnnnn')
            # Return the data as an HTTP response
            return http.Response(
                status=200,
                headers={'Content-Type': 'application/json'},
                content_type='application/json',
                body=json.dumps(data)
            )

        except Exception as e:
            return http.Response(
                status=500,
                headers={'Content-Type': 'application/json'},
                content_type='application/json',
                body=json.dumps({'error': str(e)})
            )
