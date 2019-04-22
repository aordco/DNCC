# -*- coding: utf-8 -*-
__author__ = 'Reem Eloeid'
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('team_id')
    def _onchange_team_id(self):
        self.warehouse_id = False
        team = self.team_id
        if team:
            warehouse = team.warehouse_id
            if not warehouse:
                raise ValidationError(_("Your sales team doesn't have a linked warehouse, "
                                        "please add warehouse in team form"))
            else:
                self.warehouse_id = warehouse

    @api.multi
    @api.constrains('warehouse_id')
    def _check_warehouse_id(self):
        warehouse = self.warehouse_id
        team = self.team_id
        if not team:
            raise ValidationError(_("You do not belong to a sales team"))
        if warehouse and warehouse != team.warehouse_id:
            raise ValidationError(_("You have the wrong warehouse"))