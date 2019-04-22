# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    location_ids = fields.Many2many("stock.location", string="Allowed Locations", domain=[('usage', '=', 'internal')],
                                    help="Only locations in this field can accessed by user")
