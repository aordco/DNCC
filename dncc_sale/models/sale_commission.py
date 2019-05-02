# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class SaleCommission(models.Model):
    _name = "sale.commission"
    _description = "Sales Commissions"

    STATE_SEL = [
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('settle', 'Settled')
    ]

    COVER_SEL = [
        ('all', 'ALL'),
        ('team', 'Team'),
        ('person', 'Person')

    ]

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if any(self.filtered(lambda commission: commission.start_date > commission.end_date)):
            raise ValidationError(_("Payslip 'Date From' must be earlier 'Date To'."))

    def _get_invoice_domain(self):
        start_date = self.start_date
        end_date = self.end_date
        domain = [('type', '=', 'out_invoice'), ('date_invoice', '>=', start_date),
             ('date_invoice', '<=', end_date), ('state', '!=', 'draft'), ('comm_settle', '=', False)]
        cover = self.cover
        if cover == 'team':
            team = self.team_id
            domain.append(('team_id', '=', team.id))
        if cover == 'person':
            salesperson = self.user_id
            domain.append(('user_id', '=', salesperson.id))
        return domain

    @api.depends("start_date", "end_date", "cover", "team_id", "user_id")
    def compute_invoices(self):
        for rec in self:
            domain = rec._get_invoice_domain()
            invoices = rec.env["account.invoice"].search(domain)
            rec.invoice_ids = invoices

    def compute_settle_invoices_count(self):
        for rec in self:
            bills = rec.settle_invoices
            rec.settle_invoices_count = len(bills)

    name = fields.Char("Name", default="/", readonly=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    invoice_ids = fields.Many2many("account.invoice", compute="compute_invoices")
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get())

    currency_id = fields.Many2one('res.currency', string='Company',
                                 readonly=True,
                                 related="company_id.currency_id")
    cover = fields.Selection(COVER_SEL, string="Commission For:", default="all", requied=True)
    team_id = fields.Many2one("crm.team", string="Sale Team")
    user_id = fields.Many2one("res.users", string="Salesperson")
    partial_payments = fields.One2many("partial.payment", "commission_id", string="Partial Payments", readonly=True, ondelete='cascade')
    settle_invoices = fields.One2many("account.invoice", "commission_id", string="Invoices")
    settle_invoices_count = fields.Integer("Settle Invoices No.", compute="compute_settle_invoices_count")
    state = fields.Selection(STATE_SEL, readonly=True, default='draft', copy=False, string="Status")

    # Workflow functions

    def compute_payments(self):
        """
        computes payments for invoices in this commission
        :return:
        """
        self.ensure_one()
        self.write(
            {'partial_payments': [(2, self.partial_payments.ids, False)]}
        )
        invoices = self.invoice_ids
        if not invoices:
            raise UserError(_("These options do not produce invoices"))
        for invoice in invoices:
            if invoice.payment_move_line_ids:
                payments = invoice._get_payments_vals()
                partial_pay = self.env["partial.payment"]
                for payment in payments:
                    vals = {
                        'payment_id': payment['account_payment_id'],
                        'partial_amount': payment['amount'],
                        'invoice_id': invoice.id,
                        'commission_id': self.id,
                    }
                    res = partial_pay.create(vals)
                    self.partial_payments += res

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.compute_payments()
                rec.state = 'confirm'

    def reset_draft(self):
        for rec in self:
            if rec.state not in ['draft', 'settle']:
                rec.state = 'draft'

    # ORM functions

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.commission') or '/'
        return super(SaleCommission, self).create(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if not rec.state == 'draft':
                raise UserError(_('In order to delete a commission, it must be draft.'))
        return super(SaleCommission, self).unlink()

    # Smart buttons
    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given commisison_ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_commission_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        bills = self.settle_invoices
        if len(bills) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(bills.ids) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = bills.id or False
        return result

# ##################################################################


class PartialPayment(models.Model):
    _name = "partial.payment"
    _description = "Sale Partial Payment"

    def _exclude_tax(self, amount):
        python_code = self.company_id.tax_exclusion
        try:
            _locals = locals()
            exec(python_code, globals(), _locals)
            return _locals.get('result', 0)
        except:
            raise UserError(_('Wrong python code defined for tax deduction'))

    def get_commission_percent(self):
        # if self.company_id.comiss_delay_days >= 0:
        #     days_diff = (self.payment_date - self.invoice_date).days
        #     delay_days = self.company_id.comiss_delay_days
        #     if days_diff <= delay_days:
        #         rate = self.company_id.commission
        #     else:
        #         rate = self.company_id.commission_part
        # else:
        rate = self.company_id.commission
        return rate

    @api.depends("partial_amount")
    def compute_commission(self):
        for rec in self:
            rate = rec.get_commission_percent()
            rec.rate = rate
            amount = rec.partial_amount

            commission_untax = amount * rate / 100
            commission_amount = rec._exclude_tax(commission_untax)
            commission_tax = commission_untax - commission_amount
            # assign to fields
            rec.commission_untax = commission_untax
            rec.commission_tax = commission_tax
            rec.commission_amount = commission_amount

    payment_id = fields.Many2one("account.payment", string="Payment")
    payment_date = fields.Date("Payment Date", related="payment_id.payment_date")
    partial_amount = fields.Float(string='Payment Amount', required=True)
    invoice_id = fields.Many2one("account.invoice", string="Invoice")
    partner_id = fields.Many2one("res.partner", related="invoice_id.partner_id")
    invoice_date = fields.Date("Invoice Date", related="invoice_id.date_invoice")
    commission_id = fields.Many2one("sale.commission")
    rate = fields.Float(string="Rate", compute="compute_commission")
    user_id = fields.Many2one("res.users", string="Salesperson", related="invoice_id.user_id")
    commission_untax = fields.Float(string='Before Tax', compute="compute_commission")
    commission_tax = fields.Float(string='Tax', compute="compute_commission")
    commission_amount = fields.Float(string='Commission Amount', compute="compute_commission")
    company_id = fields.Many2one(related="commission_id.company_id")


