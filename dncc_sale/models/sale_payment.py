# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class SalePayment(models.Model):
    _name = "sale.payment"

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    name = fields.Char("Name", readonly=True, default="/")
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today,
                               required=True, copy=False)
    partner_id = fields.Many2one("res.partner", string="Customer",
                                 domain=[('customer', '=', True)], required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one(related="company_id.currency_id",
                                  string='Currency', readonly=False)
    payment_id = fields.Many2one("account.payment", string="Accounting payment")
    team_id = fields.Many2one('crm.team', string='Sales Team', default=_get_default_team, oldname='section_id')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get())
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('process', 'Processed')],
                             readonly=True, default='draft',
                             copy=False, string="Status")

    # Workflow functions

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'confirm'

    @api.multi
    def reset_draft(self):
        for rec in self:
            if not rec.payment_id:
                rec.state = 'draft'

    @api.multi
    def action_make_payment(self):
        action = self.env.ref('account.action_account_invoice_payment')
        result = action.read()[0]
        if not self.payment_id:
            result['context'] = {
                    'default_partner_id': self.partner_id.id,
                    'default_partner_type': 'customer',
                    'default_payment_type': 'inbound',
                    'default_amount': 8056,
                    'default_communication': self.name,
                    'default_payment_date': self.payment_date,
                    'sale_payment': True,
                    }
            res = self.env.ref('account.view_account_payment_invoice_form', False)
            result['views'] = [(res and res.id or False, 'form')]
        else:
            action = self.env.ref('account.action_account_payments')
            result = action.read()[0]
            result['context'] = {}
            res = self.env.ref('account.view_account_payment_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.payment_id.id
        return result


    # ORM functions

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.payment') or '/'
        return super(SalePayment, self).create(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if not rec.state == 'draft':
                raise UserError(_('In order to delete a payment, it must be draft.'))
        return super(SalePayment, self).unlink()
