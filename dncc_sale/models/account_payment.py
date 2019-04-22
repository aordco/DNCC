# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

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
