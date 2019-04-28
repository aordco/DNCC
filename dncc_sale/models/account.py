# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
from odoo.addons.account.models.account_payment import MAP_INVOICE_TYPE_PARTNER_TYPE


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # only for vendor bills, source document is commission
    commission_id = fields.Many2one("sale.commission", string="Sale Commission")

    # commissioned, for customer invoices to avoid re-issuing commissions
    comm_settle = fields.Boolean(string="Commission Settled", readonly=True)

###################################################


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_validate_invoice_payment(self):
        """ override the exception in case payment is from sales payment model
        """
        if any(len(record.invoice_ids) != 1 for record in self) and not self._context.get("sale_payment", False):
            # For multiple invoices, there is account.register.payments wizard
            raise UserError(_("This method should only be called to process a single invoice's payment."))
        return self.post()

    def post(self):
        for record in self:
            if self._context.get("sale_payment", False):
                active_id = self._context.get("active_id")
                sale_payment = self.env["sale.payment"].browse([active_id])
                vals = {
                    'state': 'process',
                    'payment_id': record.id,
                }
                sale_payment.write(vals)
        super(AccountPayment, self).post()

###############################################


class AccountAbstractPayment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    @api.onchange('currency_id')
    def _onchange_currency(self):
        if not self._context.get("sale_payment", False):
            self.amount = abs(self._compute_payment_amount())
        else: self.amount = abs(self.amount)
