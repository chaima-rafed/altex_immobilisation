# -*- coding: utf-8 -*-
{
    'name': "altex_imobilisation",

    'summary': "",

    'description': """
 altex corp 2024
    """,

    'author': "NASREDDINE BOUDENE Consultant Chez ALTEX-CORP",
    'website': "https://www.altex-corp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_accounting_kit', 'hr', 'sale', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/immobilisation_views.xml',
        'views/societe_departement_bureaux.xml',
        'views/imsociete_views.xml',
        'views/imdepartement_views.xml',
        'views/imlieu_de_travail_views.xml',
        'views/asset_move_tosell_views.xml',
        'views/im_move_views.xml',
        'views/asset_inventory_views.xml',
        # 'views/asset_departement_verify_views.xml',
        'views/im_product_views.xml',
        'views/inventaire_immobilisation_views.xml',
        'views/im_adjustement_inv_views1.xml',
        'views/im_adjustement_inv_views2.xml',
        'views/asset_inventory_verify_views1.xml',
        'views/asset_inventory_verify_views2.xml',
        # 'views/asset_inventory_difference_views.xml',
        'views/asset_inventory_difference_views1.xml',
        'views/asset_inventory_difference_views2.xml',
        'views/asset_inventory_difference_beteen_two_table_views.xml',
        'views/templates.xml',
        'views/old_barcode.xml',
        'data/report_data.xml',
        'report_af/report_af.xml',
        'report_af/report_af_template.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',

    ],
    'assets': {
        'web.assets_backend': [
            # '/src/css/style.css',
            'altex_imobilisation/src/js/bs-config.js',
        ],
    },
    'installable': True,
    'application': True,
}
