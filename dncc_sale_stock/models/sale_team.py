# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleTeam(models.Model):
    _inherit = "crm.team"

    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    location_id = fields.Many2one("stock.location", string="Location", domain=[('usage', '=', 'internal')])
    delivery_operation = fields.Many2one("stock.picking.type", "Delivery")