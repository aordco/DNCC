# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCommissionSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_commission_active = fields.Boolean("Sales Commissions",

                                     default=lambda self: self.env.user.company_id.sale_commission)

    sale_commission = fields.Boolean("Sales Commissions", related="company_id.sale_commission", readonly=False)

    comiss_delay_days = fields.Integer(string="Days", related="company_id.comiss_delay_days", readonly=False)
    commission = fields.Float(string="Whole Commission in %", related="company_id.commission", readonly=False)
    commission_part = fields.Float(string="Part Commission in %", related="company_id.commission_part", readonly=False)
    tax_exclusion = fields.Text(string="Tax Exclusion formula", related="company_id.tax_exclusion", readonly=False)
    commission_product = fields.Many2one("product.product",
                                         string="Commission Product", related="company_id.commission_product", readonly=False)

    def set_values(self):
        super(ResCommissionSettings, self).set_values()
        self.sale_commission = True if self.sale_commission_active else False
