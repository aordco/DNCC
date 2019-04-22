# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    user_ids = fields.Many2many("res.users", string="Responsible Users",
                                help="Only users in this field can access inventory picking")
