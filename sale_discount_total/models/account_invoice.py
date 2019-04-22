# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('discount_type', 'discount_rate', 'invoice_line_ids')
    def onchange_discount_rate(self):
        for inv in self:
            if inv.discount_type == 'percent':
                for line in inv.invoice_line_ids:
                    line.discount = inv.discount_rate
            else:
                total = discount = 0.0
                for line in inv.invoice_line_ids:
                    total += (line.quantity * line.price_unit)
                if inv.discount_rate != 0:
                    discount = (inv.discount_rate / total) * 100
                else:
                    discount = inv.discount_rate
                for line in inv.invoice_line_ids:
                    line.discount = discount

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]})

