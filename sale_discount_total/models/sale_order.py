# -*- coding: utf-8 -*-
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def onchange_discount_rate(self):
        for order in self:
            if order.discount_type == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_rate
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_rate != 0:
                    discount = (order.discount_rate / total) * 100
                else:
                    discount = order.discount_rate
                for line in order.order_line:
                    line.discount = discount

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('waiting', 'Waiting Approval'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.multi
    def action_confirm(self):
        discnt = 0.0
        no_line = 0.0
        if self.company_id.so_double_validation == 'two_step':
            for line in self.order_line:
                no_line += 1
                discnt += line.discount
            discnt = (discnt / no_line)
            if self.company_id.so_double_validation_limit and discnt > self.company_id.so_double_validation_limit:
                self.state = 'waiting'
                return True
        super(SaleOrder, self).action_confirm()

    @api.multi
    def action_approve(self):
        super(SaleOrder, self).action_confirm()
        return True

    @api.multi
    def _prepare_invoice(self,):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate
        })
        return invoice_vals
