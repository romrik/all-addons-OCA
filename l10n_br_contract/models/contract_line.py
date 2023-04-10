# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ...l10n_br_fiscal.constants.fiscal import TAX_FRAMEWORK


class ContractLine(models.Model):
    _name = "contract.line"
    _inherit = [_name, "l10n_br_fiscal.document.line.mixin"]

    company_id = fields.Many2one(
        related="contract_id.company_id",
    )
    country_id = fields.Many2one(related="company_id.country_id", store=True)

    fiscal_tax_ids = fields.Many2many(
        comodel_name="l10n_br_fiscal.tax",
        relation="fiscal_contract_line_tax_rel",
        column1="document_id",
        column2="fiscal_tax_id",
        string="Fiscal Taxes",
    )

    tax_framework = fields.Selection(
        selection=TAX_FRAMEWORK,
        related="contract_id.company_id.tax_framework",
        string="Tax Framework",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="contract_id.partner_id",
        string="Partner",
    )

    ind_final = fields.Selection(related="contract_id.ind_final")

    @api.multi
    def _prepare_invoice_line(self, invoice_id=False, invoice_values=False):
        self.ensure_one()
        contract = self.contract_id
        if contract.contract_recalculate_taxes_before_invoice:
            self._onchange_fiscal_operation_id()
        values = super()._prepare_invoice_line(invoice_id, invoice_values)
        quantity = values.get("quantity")
        if values:
            values.update(self._prepare_br_fiscal_dict())
            values["quantity"] = quantity
            values["discount_value"] = (self.quantity * self.price_unit) * (
                self.discount / 100
            )
        return values
