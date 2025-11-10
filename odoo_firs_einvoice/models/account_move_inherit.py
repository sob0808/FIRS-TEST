from odoo import models, fields, _
from odoo.exceptions import UserError
import base64, qrcode, json, re, logging
from io import BytesIO
from datetime import datetime

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    firs_irn = fields.Char("FIRS IRN", copy=False)
    firs_status = fields.Selection([
        ('none','Not Submitted'),
        ('pending','Pending'),
        ('validated','Validated'),
        ('signed','Signed'),
        ('error','Error')
    ], default='none', copy=False)
    firs_response = fields.Text("FIRS Response", copy=False)
    firs_qr = fields.Binary("FIRS QR Code", copy=False)

    def _firs_get_tax_category_code(self, tax):
        """
        Map Odoo tax to FIRS tax category code.
        Returns a valid FIRS tax category code based on tax name/type.
        Defaults to STANDARD_VAT for VAT taxes.
        """
        if not tax:
            return 'STANDARD_VAT'  # Default fallback
        
        tax_name_upper = tax.name.upper()
        tax_amount = tax.amount
        
        # Map common tax patterns to FIRS categories
        # VAT taxes
        if 'VAT' in tax_name_upper or 'VALUE ADDED' in tax_name_upper:
            if tax_amount == 0:
                return 'ZERO_VAT'
            elif tax_amount < 7.5:  # Reduced rate (adjust threshold as needed)
                return 'REDUCED_VAT'
            else:
                return 'STANDARD_VAT'  # Default VAT (usually 7.5% in Nigeria)
        
        # GST taxes
        if 'GST' in tax_name_upper or 'GOODS AND SERVICES' in tax_name_upper:
            if tax_amount == 0:
                return 'ZERO_GST'
            elif tax_amount < 7.5:
                return 'REDUCED_GST'
            else:
                return 'STANDARD_GST'
        
        # Sales tax
        if 'SALES TAX' in tax_name_upper or 'SALES' in tax_name_upper:
            if 'LOCAL' in tax_name_upper or 'LGA' in tax_name_upper:
                return 'LOCAL_SALES_TAX'
            elif 'STATE' in tax_name_upper:
                return 'STATE_SALES_TAX'
            else:
                return 'LOCAL_SALES_TAX'  # Default to local
        
        # Excise taxes
        if 'ALCOHOL' in tax_name_upper:
            return 'ALCOHOL_EXCISE_TAX'
        if 'TOBACCO' in tax_name_upper:
            return 'TOBACCO_EXCISE_TAX'
        if 'FUEL' in tax_name_upper or 'PETROL' in tax_name_upper:
            return 'FUEL_EXCISE_TAX'
        
        # Income taxes
        if 'CORPORATE INCOME' in tax_name_upper or 'CIT' in tax_name_upper:
            return 'CORPORATE_INCOME_TAX'
        if 'PERSONAL INCOME' in tax_name_upper or 'PIT' in tax_name_upper:
            return 'PERSONAL_INCOME_TAX'
        
        # Other taxes
        if 'IMPORT' in tax_name_upper or 'CUSTOM' in tax_name_upper:
            return 'IMPORT_DUTY'
        if 'EXPORT' in tax_name_upper:
            return 'EXPORT_DUTY'
        if 'CARBON' in tax_name_upper:
            return 'CARBON_TAX'
        if 'PLASTIC' in tax_name_upper:
            return 'PLASTIC_TAX'
        if 'LUXURY' in tax_name_upper:
            return 'LUXURY_TAX'
        if 'SERVICE' in tax_name_upper:
            return 'SERVICE_TAX'
        if 'TOURISM' in tax_name_upper:
            return 'TOURISM_TAX'
        
        # Default: If it's a percentage tax, assume it's VAT
        # If zero rate, use ZERO_VAT, otherwise STANDARD_VAT
        if tax_amount == 0:
            return 'ZERO_VAT'
        else:
            return 'STANDARD_VAT'  # Default to standard VAT for Nigeria

    def _firs_get_party_address(self, partner, is_supplier=False):
        """Build postal address structure for a partner"""
        if not partner:
            return None
        
        # For supplier, street_name is mandatory
        if is_supplier and not partner.street:
            raise UserError(_('Supplier street address is required for FIRS e-Invoice. Please set street address on company partner.'))
        
        address = {}
        
        # street_name is mandatory for supplier
        if partner.street:
            address['street_name'] = partner.street
        elif is_supplier:
            # If supplier and no street, use a default or raise error
            address['street_name'] = 'Not Provided'  # Fallback, but should be validated above
        
        # city_name is typically required
        if partner.city:
            address['city_name'] = partner.city
        elif is_supplier:
            address['city_name'] = 'Not Provided'  # Fallback
        
        # postal_zone (zip code)
        if partner.zip:
            address['postal_zone'] = partner.zip
        
        # country is mandatory
        address['country'] = partner.country_id.code if partner.country_id else 'NG'
        
        # state (optional but recommended)
        if partner.state_id:
            # State code - you may need to map this to FIRS state codes
            # For now, using state name or code
            address['state'] = partner.state_id.code or str(partner.state_id.id) if partner.state_id.id else ''
        
        # LGA might need to be added as a custom field on partner
        
        return address if address else None

    def _firs_get_party(self, partner, is_supplier=False):
        """Build party structure (supplier or customer)"""
        if not partner:
            return None
        
        conf = self.env['ir.config_parameter'].sudo()
        party = {
            'party_name': partner.name or '',
        }
        
        # TIN is mandatory for both supplier and customer (per API requirements)
        if is_supplier:
            party['tin'] = partner.vat or conf.get_param('firs.tin') or ''
            if not party['tin']:
                raise UserError(_('Supplier TIN is required for FIRS e-Invoice. Please set VAT/TIN on company or partner.'))
        else:
            # Customer TIN is now mandatory per API
            party['tin'] = partner.vat or ''
            if not party['tin']:
                raise UserError(_('Customer TIN is required for FIRS e-Invoice. Please set VAT/TIN on customer partner.'))
        
        # Email is mandatory for both supplier and customer (per API requirements)
        if is_supplier:
            party['email'] = partner.email or self.company_id.email or ''
            if not party['email']:
                raise UserError(_('Supplier email is required for FIRS e-Invoice. Please set email on company.'))
        else:
            # Customer email is now mandatory per API
            party['email'] = partner.email or ''
            if not party['email']:
                raise UserError(_('Customer email is required for FIRS e-Invoice. Please set email on customer partner.'))
        
        if partner.comment:
            party['business_description'] = partner.comment[:500]  # Limit length
        
        # Postal address - mandatory for supplier
        postal_address = self._firs_get_party_address(partner, is_supplier=is_supplier)
        if is_supplier:
            # For supplier, postal_address is mandatory and must have street_name
            if not postal_address or not postal_address.get('street_name'):
                raise UserError(_('Supplier postal address with street name is required for FIRS e-Invoice. Please set street address on company partner.'))
            party['postal_address'] = postal_address
        elif postal_address:
            # For customer, postal_address is optional
            party['postal_address'] = postal_address
        
        return party

    def _firs_build_payload(self):
        """Build UBL-compliant payload for FIRS API"""
        self.ensure_one()
        
        if not self.invoice_date:
            raise UserError(_('Invoice date is required for FIRS e-Invoice'))
        
        conf = self.env['ir.config_parameter'].sudo()
        business_id = conf.get_param('firs.business_id')
        if not business_id:
            raise UserError(_('Business ID is required. Please configure it in FIRS settings.'))
        
        # Generate IRN if not exists - format: INVOICE_NUMBER-SERVICE_ID-YYYYMMDD
        # IRN must be: all uppercase, no spaces, only '-' special character allowed
        if not self.firs_irn:
            service_id = conf.get_param('firs.service_id')
            if not service_id:
                raise UserError(_('Service ID is required for IRN generation. Please configure it in FIRS settings.'))
            
            # Format invoice number: uppercase, alphanumeric only (remove special chars except allowed)
            invoice_number = self.name.upper()
            # Remove all special characters except alphanumeric
            invoice_number = re.sub(r'[^A-Z0-9]', '', invoice_number)
            if not invoice_number:
                raise UserError(_('Invoice number must contain at least one alphanumeric character.'))
            
            # Format date as YYYYMMDD (numeric only)
            date_str = self.invoice_date.strftime('%Y%m%d')
            
            # Service ID should be uppercase, alphanumeric, 8 characters
            service_id = service_id.upper().strip()
            service_id = re.sub(r'[^A-Z0-9]', '', service_id)
            if len(service_id) != 8:
                raise UserError(_('Service ID must be exactly 8 alphanumeric characters. Current: %s') % service_id)
            
            # Combine: INVOICE_NUMBER-SERVICE_ID-YYYYMMDD
            irn = f"{invoice_number}-{service_id}-{date_str}"
            # Save the generated IRN immediately
            if not self.firs_irn:
                self.write({'firs_irn': irn})
        else:
            irn = self.firs_irn
        
        # Build invoice lines
        invoice_lines = []
        for line in self.invoice_line_ids:
            if line.display_type in ('line_section', 'line_note'):
                continue
            
            # Calculate tax amounts
            tax_amount = 0
            tax_subtotal = []
            for tax in line.tax_ids:
                tax_amt = line.price_subtotal * (tax.amount / 100)
                tax_amount += tax_amt
                tax_category_code = self._firs_get_tax_category_code(tax)
                tax_subtotal.append({
                    'taxable_amount': float(line.price_subtotal),
                    'tax_amount': float(tax_amt),
                    'tax_category': {
                        'id': tax_category_code,  # Use FIRS tax category code
                        'percent': float(tax.amount)
                    }
                })
            
            # Build item name and description
            # Name is limited to 200 chars, description is mandatory and can be up to 500 chars
            item_name = (line.name[:200] if line.name else 'Item').strip()
            item_description = ''
            
            # Try to get description from line name (if longer than 200 chars, use remainder)
            if line.name and len(line.name) > 200:
                item_description = line.name[200:700].strip()  # Use chars 200-700 as description
            elif line.name:
                # If name is short, use it as description too
                item_description = line.name.strip()
            
            # If still no description, try product description
            if not item_description and line.product_id:
                if line.product_id.description_sale:
                    item_description = line.product_id.description_sale[:500].strip()
                elif line.product_id.description:
                    item_description = line.product_id.description[:500].strip()
            
            # Description is mandatory - ensure we have something
            if not item_description:
                item_description = item_name  # Fallback to name if no description available
            
            invoice_line = {
                'hsn_code': line.product_id.default_code or 'GENERAL',
                'product_category': line.product_id.categ_id.name if line.product_id.categ_id else 'General',
                'invoiced_quantity': float(line.quantity),
                'line_extension_amount': float(line.price_subtotal),
                'item': {
                    'name': item_name,
                    'description': item_description[:500]  # Mandatory field, limit to 500 chars
                },
                'price': {
                    'price_amount': float(line.price_unit),
                    'base_quantity': 1,
                    'price_unit': 'NGN per 1'
                }
            }
            
            # Add discount if any
            if line.discount:
                invoice_line['discount_rate'] = float(line.discount)
                invoice_line['discount_amount'] = float(line.price_subtotal * line.discount / 100)
            
            invoice_lines.append(invoice_line)
        
        # Calculate tax totals
        tax_total = []
        total_tax_amount = 0
        tax_subtotal_list = []
        
        for tax in self.invoice_line_ids.mapped('tax_ids'):
            taxable_amount = sum(line.price_subtotal for line in self.invoice_line_ids if tax in line.tax_ids)
            tax_amt = taxable_amount * (tax.amount / 100)
            total_tax_amount += tax_amt
            
            tax_category_code = self._firs_get_tax_category_code(tax)
            tax_subtotal_list.append({
                'taxable_amount': float(taxable_amount),
                'tax_amount': float(tax_amt),
                'tax_category': {
                    'id': tax_category_code,  # Use FIRS tax category code
                    'percent': float(tax.amount)
                }
            })
        
        if tax_subtotal_list:
            tax_total.append({
                'tax_amount': float(total_tax_amount),
                'tax_subtotal': tax_subtotal_list
            })
        
        # Build legal monetary total
        line_extension = sum(line.price_subtotal for line in self.invoice_line_ids)
        tax_exclusive = line_extension
        tax_inclusive = self.amount_total
        payable = self.amount_total
        
        legal_monetary_total = {
            'line_extension_amount': float(line_extension),
            'tax_exclusive_amount': float(tax_exclusive),
            'tax_inclusive_amount': float(tax_inclusive),
            'payable_amount': float(payable)
        }
        
        # Build payload
        payload = {
            'business_id': business_id,
            'irn': irn,
            'issue_date': self.invoice_date.strftime('%Y-%m-%d'),
            'invoice_type_code': '381',  # Standard invoice - adjust as needed
            'document_currency_code': self.currency_id.name or 'NGN',
            'tax_currency_code': self.currency_id.name or 'NGN',
            'accounting_supplier_party': self._firs_get_party(self.company_id.partner_id, is_supplier=True),
            'legal_monetary_total': legal_monetary_total,
            'invoice_line': invoice_lines
        }
        
        # Optional fields
        if self.invoice_date_due:
            payload['due_date'] = self.invoice_date_due.strftime('%Y-%m-%d')
        
        if self.invoice_date:
            issue_time = datetime.now().strftime('%H:%M:%S')
            payload['issue_time'] = issue_time
        
        payload['payment_status'] = 'PENDING'  # Default
        
        if self.narration:
            payload['note'] = self.narration[:500]
        
        # Customer party (mandatory per API - must have TIN and email)
        if not self.partner_id:
            raise UserError(_('Customer is required for FIRS e-Invoice. Please select a customer on the invoice.'))
        
        customer_party = self._firs_get_party(self.partner_id, is_supplier=False)
        if not customer_party:
            raise UserError(_('Failed to build customer party information. Please ensure customer has TIN and email.'))
        
        payload['accounting_customer_party'] = customer_party
        
        # Tax total (mandatory)
        # According to API docs, tax_total is an array
        # Each element should have tax_amount and tax_subtotal array
        if tax_total:
            payload['tax_total'] = tax_total
        else:
            # Even if no tax, we need an empty tax_total structure
            payload['tax_total'] = [{
                'tax_amount': 0.0,
                'tax_subtotal': []
            }]
        
        # Log the complete payload for debugging
        _logger.info('FIRS Payload Structure Check:')
        _logger.info('  - business_id: %s', payload.get('business_id'))
        _logger.info('  - irn: %s', payload.get('irn'))
        _logger.info('  - issue_date: %s', payload.get('issue_date'))
        _logger.info('  - invoice_type_code: %s', payload.get('invoice_type_code'))
        _logger.info('  - document_currency_code: %s', payload.get('document_currency_code'))
        _logger.info('  - tax_currency_code: %s', payload.get('tax_currency_code'))
        _logger.info('  - accounting_supplier_party: %s', 'Present' if payload.get('accounting_supplier_party') else 'MISSING')
        _logger.info('  - accounting_customer_party: %s', 'Present' if payload.get('accounting_customer_party') else 'Optional')
        _logger.info('  - legal_monetary_total: %s', 'Present' if payload.get('legal_monetary_total') else 'MISSING')
        _logger.info('  - tax_total: %s', 'Present' if payload.get('tax_total') else 'MISSING')
        _logger.info('  - invoice_line count: %s', len(payload.get('invoice_line', [])))
        
        return payload

    def _set_qr_from_text(self, text: str):
        img = qrcode.make(text)
        buf = BytesIO()
        img.save(buf, format='PNG')
        self.firs_qr = base64.b64encode(buf.getvalue())

    def action_firs_validate(self):
        """Validate invoice data before signing"""
        for move in self:
            if move.move_type != 'out_invoice':
                continue
            try:
                payload = move._firs_build_payload()
                # Ensure IRN is saved if it was just generated
                if payload.get('irn') and not move.firs_irn:
                    move.write({'firs_irn': payload.get('irn')})
                
                res = self.env['firs.client'].validate_invoice(payload)
                if res.get('success'):
                    data = res.get('data') or {}
                    response_text = json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
                    
                    # Update IRN if returned in response
                    irn = data.get('irn') or move.firs_irn or payload.get('irn')
                    if irn and not move.firs_irn:
                        move.write({'firs_irn': irn})
                    
                    move.write({
                        'firs_status': 'validated',
                        'firs_response': response_text
                    })
                    
                    # Post to chatter
                    move.message_post(
                        body=_('✅ FIRS Invoice Validated Successfully\n\nIRN: %s\n\nResponse: %s') % (
                            irn or 'N/A',
                            response_text[:500] + '...' if len(response_text) > 500 else response_text
                        ),
                        subject=_('FIRS Validation')
                    )
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS Validation'),
                            'message': _('Invoice validated successfully. IRN: %s') % (irn or 'Generated'),
                            'type': 'success',
                            'sticky': False,
                        },
                    }
                else:
                    error_msg = res.get('error', 'Unknown error')
                    move.write({
                        'firs_status': 'error',
                        'firs_response': error_msg
                    })
                    
                    # Post error to chatter
                    move.message_post(
                        body=_('❌ FIRS Validation Failed\n\nError: %s') % error_msg,
                        subject=_('FIRS Validation Error')
                    )
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS Validation Failed'),
                            'message': error_msg,
                            'type': 'danger',
                            'sticky': True,
                        },
                    }
            except Exception as e:
                error_str = str(e)
                move.write({
                    'firs_status': 'error',
                    'firs_response': error_str
                })
                
                # Post exception to chatter
                move.message_post(
                    body=_('❌ FIRS Validation Exception\n\nError: %s') % error_str,
                    subject=_('FIRS Validation Exception')
                )
                
                raise UserError(_('Validation error: %s') % error_str)

    def action_firs_sign(self):
        """Sign/submit invoice to FIRS"""
        for move in self:
            if move.move_type != 'out_invoice':
                continue
            try:
                move.write({'firs_status': 'pending'})
                payload = move._firs_build_payload()
                
                # Ensure IRN is saved if it was just generated
                if payload.get('irn') and not move.firs_irn:
                    move.write({'firs_irn': payload.get('irn')})
                
                res = self.env['firs.client'].sign_invoice(payload)
                if res.get('success'):
                    data = res.get('data') or {}
                    response_text = json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
                    
                    # Get IRN from response or use existing
                    irn = data.get('irn') or move.firs_irn or payload.get('irn')
                    qr_text = data.get('qr') or data.get('qr_code') or data.get('qrCode')
                    
                    # Update all fields
                    update_vals = {
                        'firs_status': 'signed',
                        'firs_response': response_text
                    }
                    
                    if irn:
                        update_vals['firs_irn'] = irn
                    
                    # Handle QR code - could be base64 image or text to encode
                    if qr_text:
                        # Check if it's already a base64 PNG image (PNG starts with iVBOR, JPEG with /9j/)
                        qr_str = str(qr_text).strip()
                        if qr_str.startswith('iVBOR') or qr_str.startswith('/9j/'):
                            # It's a base64 image - save directly
                            update_vals['firs_qr'] = qr_str
                        else:
                            # It's text (IRN or encrypted data), generate QR code from it
                            move._set_qr_from_text(qr_str)
                            # _set_qr_from_text already saves to firs_qr, so we don't need to add it to update_vals
                    
                    # Write all updates at once
                    move.write(update_vals)
                    
                    # Post success to chatter
                    chatter_body = _('✅ FIRS Invoice Signed Successfully\n\nIRN: %s\n\n') % (irn or 'N/A')
                    if qr_text:
                        chatter_body += _('QR Code: Generated\n\n')
                    chatter_body += _('Response: %s') % (response_text[:500] + '...' if len(response_text) > 500 else response_text)
                    
                    move.message_post(
                        body=chatter_body,
                        subject=_('FIRS Invoice Signed')
                    )
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS Signing'),
                            'message': _('Invoice signed successfully. IRN: %s') % (irn or 'N/A'),
                            'type': 'success',
                            'sticky': False,
                        },
                    }
                else:
                    error_msg = res.get('error', 'Unknown error')
                    move.write({
                        'firs_status': 'error',
                        'firs_response': error_msg
                    })
                    
                    # Post error to chatter
                    move.message_post(
                        body=_('❌ FIRS Signing Failed\n\nError: %s') % error_msg,
                        subject=_('FIRS Signing Error')
                    )
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS Signing Failed'),
                            'message': error_msg,
                            'type': 'danger',
                            'sticky': True,
                        },
                    }
            except Exception as e:
                error_str = str(e)
                move.write({
                    'firs_status': 'error',
                    'firs_response': error_str
                })
                
                # Post exception to chatter
                move.message_post(
                    body=_('❌ FIRS Signing Exception\n\nError: %s') % error_str,
                    subject=_('FIRS Signing Exception')
                )
                
                raise UserError(_('Signing error: %s') % error_str)

    def action_firs_confirm(self):
        """Confirm invoice status"""
        for move in self:
            if not move.firs_irn:
                raise UserError(_('IRN is required to confirm invoice. Please sign the invoice first.'))
            try:
                res = self.env['firs.client'].confirm_invoice(move.firs_irn)
                if res.get('success'):
                    data = res.get('data') or {}
                    move.write({'firs_response': json.dumps(data) if isinstance(data, dict) else str(data)})
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS Confirmation'),
                            'message': _('Invoice confirmed. Status: %s') % data.get('payment_status', 'N/A'),
                            'type': 'success',
                            'sticky': False,
                        },
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS Confirmation Failed'),
                            'message': res.get('error', 'Unknown error'),
                            'type': 'danger',
                            'sticky': True,
                        },
                    }
            except Exception as e:
                raise UserError(_('Confirmation error: %s') % str(e))

    def action_firs_validate_irn(self):
        """Validate IRN"""
        for move in self:
            if not move.firs_irn:
                raise UserError(_('IRN is required to validate. Please sign the invoice first.'))
            try:
                conf = self.env['ir.config_parameter'].sudo()
                business_id = conf.get_param('firs.business_id')
                if not business_id:
                    raise UserError(_('Business ID is required. Please configure it in FIRS settings.'))
                
                res = self.env['firs.client'].validate_irn(move.name, business_id, move.firs_irn)
                if res.get('success'):
                    data = res.get('data') or {}
                    move.write({'firs_response': json.dumps(data) if isinstance(data, dict) else str(data)})
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS IRN Validation'),
                            'message': _('IRN validated successfully.'),
                            'type': 'success',
                            'sticky': False,
                        },
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('FIRS IRN Validation Failed'),
                            'message': res.get('error', 'Unknown error'),
                            'type': 'danger',
                            'sticky': True,
                        },
                    }
            except Exception as e:
                raise UserError(_('IRN validation error: %s') % str(e))

    def action_firs_send(self):
        """Legacy method - validates then signs"""
        self.action_firs_validate()
        return self.action_firs_sign()

    def action_post(self):
        res = super().action_post()
        for move in self.filtered(lambda m: m.move_type == 'out_invoice'):
            try:
                move.action_firs_send()
            except Exception as e:
                move.message_post(body=f'FIRS submission exception: {e}')
                move.write({'firs_status': 'error', 'firs_response': str(e)})
        return res
