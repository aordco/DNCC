# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError


class SettleCommissionLine(models.TransientModel):
    _name = 'settle.commission.line'

    user_id = fields.Many2one("res.users", string="Users")
    total_commission = fields.Float(string="Total Commission")
    settlement_id = fields.Many2one("settle.commission", string="Settlement")


# #######################################################


class SettleCommission(models.TransientModel):
    _name = 'settle.commission'

    @api.model
    def default_get(self, fields):
        res = super(SettleCommission, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'sale.commission' and active_ids:
            commission = self.env["sale.commission"].browse(active_ids)
            payments = commission.partial_payments
            users = commission.partial_payments.mapped("user_id")
            user_total = [{'user_id': user, 'amount': sum(payments.filtered(lambda pay: pay.user_id == user).mapped("commission_amount"))} for user in users]
            res['commission_id'] = active_ids[0]
            lines = []

            for user in user_total:
                vals = {
                    'user_id': user['user_id'].id,
                    'total_commission': user["amount"],
                }
                lines.append((0, 0, vals))

            res["line_ids"] = lines
        return res

    commission_id = fields.Many2one("sale.commission", string="Commission", readonly=True)
    line_ids = fields.One2many("settle.commission.line", "settlement_id", string="Lines")

    def create_invoice(self, line):
        partner = line.user_id.partner_id
        invoice = self.env["account.invoice"].create({
            'partner_id': partner.id,
            'type': 'in_invoice',
            'currency_id': self.commission_id.currency_id.id,
            'commission_id': self.commission_id.id
        })
        self.create_invoice_line(invoice, line)
        return invoice

    def create_invoice_line(self, invoice_id, line):
        line_obj = self.env["account.invoice.line"]
        product = self.commission_id.company_id.commission_product
        if not product:
            raise ValidationError(_("Configure Commission Product in Sale configuration"))
        invoice_line = line_obj.new({
            'product_id': product.id,
            'invoice_id': invoice_id,
            'tax_ids': False,
            'quantity': 1,
            'origin': str(self.commission_id.name),
            'name': 'Sale Commission'
        })
        invoice_line._onchange_product_id()
        invoice_line_dict = invoice_line._convert_to_write({
            name: invoice_line[name] for name in invoice_line._cache})
        invoice_line_dict['price_unit'] = line.total_commission
        invoice_line_dict['invoice_line_tax_ids'] = False
        line_obj.create(invoice_line_dict)

    def do_create_invoices(self):
        for line in self.line_ids:
            self. create_invoice(line)
        self.commission_id.state = 'settle'
        self.commission_id.invoice_ids.write(
            {
                'comm_settle': True
            }
        )
