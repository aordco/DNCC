# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'DNCC Sales Stock Customization ',
    'version': '1.1',
    'category': 'sale',
    'sequence': 35,
    'summary': 'DNCC specific Customization',
    'description': """
""",
    'website': 'https://www.aordco.com',
    'depends': ['sale', 'sale_enterprise', 'sales_team', 'sale_stock'],
    'data': [
        'views/sales_team_views.xml',
        # 'views/sale_order_views.xml'

    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,

}
