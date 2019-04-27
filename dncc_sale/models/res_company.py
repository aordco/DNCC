# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    sale_commission = fields.Boolean("Sales Commissions")

    comiss_delay_days = fields.Integer(string="Days")
    commission = fields.Float(string="Whole Commission")
    commission_part = fields.Float(string="Part Commission")
    tax_exclusion = fields.Text(string="Tax Exclusion formula", default="result=amount/105*100")
    commission_product = fields.Many2one("product.product", string="Commission Product", domain=[('type', '=', 'service')])
