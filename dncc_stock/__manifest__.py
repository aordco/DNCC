# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'DNCC Stock Customization ',
    'version': '1.1',
    'category': 'stock',
    'sequence': 35,
    'summary': 'DNCC specific Customization',
    'description': """
""",
    'website': 'https://www.aordco.com',
    'depends': ['stock', 'stock_enterprise', 'stock_account', 'product'],
    'data': [
        'security/security_rules.xml', #stock based on keeper
        'wizard/stock_quantity_history.xml',
        'views/stock_picking_type_views.xml',
        # 'views/stock_location_views.xml',
        'views/res_users_views.xml',
        'views/product_views.xml',

    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,

}
