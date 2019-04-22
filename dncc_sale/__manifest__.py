# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'DNCC Sale Customization ',
    'version': '1.1',
    'category': 'sale',
    'sequence': 35,
    'summary': 'DNCC specific Customization',
    'description': """
""",
    'website': 'https://www.aordco.com',
    'depends': ['sale', 'sale_enterprise', 'sales_team', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_data.xml',
        'views/sale_payment_views.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,

}
