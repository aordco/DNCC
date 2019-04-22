# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResDiscountSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    so_order_approval = fields.Boolean("Sale Discount Approval", default=lambda self: self.env.user.company_id.so_double_validation == 'two_step')

    so_double_validation = fields.Selection(related='company_id.so_double_validation',string="Levels of Approvals *", readonly=False)
    so_double_validation_limit = fields.Float(string="Discount limit requires approval in %",
                                              related='company_id.so_double_validation_limit', readonly=False)

    def set_values(self):
        super(ResDiscountSettings, self).set_values()
        self.so_double_validation = 'two_step' if self.so_order_approval else 'one_step'
