from odoo import api, models


class CommissionReport(models.AbstractModel):
    _name = 'report.dncc_sale.report_sale_commission'

    def get_user_details(self, docs):
        details = []
        commission_lines = docs.partial_payments
        for user in commission_lines.mapped("user_id"):
            user_details = commission_lines.filtered(lambda x: x.user_id == user)
            vals = {
                'name': user.name,
                'total': sum(user_details.mapped("commission_amount")),
                'lines': user_details
            }
            details.append(vals)
        return details

    @api.model
    def _get_report_values(self, docids, data=None):
        report_name = 'dncc_sale.report_sale_commission'
        report = self.env['ir.actions.report']._get_report_from_name(report_name)
        docs = self.env[report.model].browse(docids)
        details = self.get_user_details(docs)
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'user_details': details,
            'format_float': self.env['ir.qweb.field.float'].value_to_html,
        }
