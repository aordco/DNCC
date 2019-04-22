# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockQuantityHistory(models.TransientModel):
    _inherit = "stock.quantity.history"

    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string="Warehouse"
    )

    location_id = fields.Many2one(
        comodel_name='stock.location',
        string="Location"


    )

    def open_table(self):
        if not self.env.context.get('valuation'):
            return super(StockQuantityHistory, self).open_table()
        location = self.location_id.id
        self.env['stock.move']._run_fifo_vacuum()

        if self.compute_at_date:
            tree_view_id = self.env.ref('stock_account.view_stock_product_tree2').id
            form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
            search_view_id = self.env.ref('stock_account.view_inventory_valuation_search').id
            # We pass `to_date` in the context so that `qty_available` will be computed across
            # moves until date.
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Inventory Valuation'),
                'res_model': 'product.product',
                'domain': "[('type', '=', 'product'), ('qty_available', '!=', 0)]",
                'context': dict(self.env.context, to_date=self.date, company_owned=True, create=False, edit=False,
                                location=location),
                'search_view_id': search_view_id
            }
            return action
        else:
            return self.env.ref('stock_account.product_valuation_action').read()[0]

