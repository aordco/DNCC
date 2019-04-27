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
        'report/reports.xml',
        'report/report_sale_payment_templates.xml',
        'report/report_sale_commission_templates.xml',
        'wizard/res_config_views.xml',
        'wizard/commission_settle_views.xml',
        'views/sale_payment_views.xml',
        'views/sale_commission_views.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,

}
