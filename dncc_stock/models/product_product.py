# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    trivial_valuation = fields.Float(string='Valuation (Trivial)', compute='_compute_trivial_valuation')

    def _compute_trivial_valuation(self):
        location = self._context.get('location')
        for product in self:
            loc_qty = product.get_theoretical_quantity(product.id, location)
            product.trivial_valuation = product.get_history_price(
                product.company_id.id, date=product._context.get('to_date')
            ) * loc_qty
