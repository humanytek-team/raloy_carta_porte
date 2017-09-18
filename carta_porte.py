# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError

class RemisionLine(models.Model):
    _name = 'carta.porte.line'

    @api.onchange('remision_id')
    def _compute_remision(self):
        #SE BUSCA SI YA EXISTEN LINEAS CON LA REMISION SELECCIONADA (MAXIMO 2)
        res = self.search([['remision_id', '=', self.remision_id.id]])
        if len(res) < 2:
            unidades_producto = 0.0
            unidades_litros = 0.0
            unidades_cubicas = 0.0
            if self.remision_id.move_lines:
                for line in self.remision_id.move_lines:
                    unidades_producto += line.product_uom_qty
                    #unidades_litros += (line.product_uom_qty * line.product_id.uos_coeff)
                    unidades_cubicas += (line.product_uom_qty * line.product_id.volume)

            self.unidades_producto = unidades_producto
            self.unidades_litros = unidades_litros
            self.unidades_cubicas = unidades_cubicas
        else:
            raise ValidationError(_('La remision seleccionada ya contiene 2 embarques'))
            #raise Warning(_("Error!"), _('La remision seleccionada ya contiene 2 embarques'))




    name= fields.Integer(String='Id de linea de remision',required=True, invicible=True)
    remision_id = fields.Many2one('stock.picking', 'Remision', required=True, domain="[('state', '=', 'done'),('picking_type_id.code', '=', 'outgoing')]")
    ciudad = fields.Char(string='Ciudad')
    unidades_producto = fields.Float(string='Unidades producto', store=True)
    unidades_litros = fields.Float(string='Unidades litro', store=True)
    unidades_cubicas = fields.Float(string='Unidades cubicas', store=True)


class CartaPorte(models.Model):
    _name = 'carta.porte'
    _description = 'Carta porte'
    _inherit = ['mail.thread']

    ###########################################
    #METODOS ORM
    ###########################################

    @api.model    
    def create(self, values):
        #print 'values: ',values

        #DESCARTA LAS REMISIONES QUE YA ESTEN EN UN MAXIMO DE 2 EMBARQUES
        if 'remision_ids' in values:
            for remision in values['remision_ids']:
                res = self.env['carta.porte.line'].search([['remision_id', '=', remision[2]['remision_id'] ]])
                if len(res) >= 2:
                    picking = self.env['stock.picking'].search([['id','=',remision[2]['remision_id']]])
                    #raise Warning(_("Error!"), _('La remision ' + picking.name + ' ya contiene 2 embarques'))
                    raise ValidationError(_('La remision ' + picking.name + ' ya contiene 2 embarques'))
                    return False

        if values.get('name', 'New') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code('carta.porte') or 'New'
           
        record = super(CartaPorte, self).create(values)
        return record



    @api.multi
    def write(self, values):
        #print 'write'
        #DE EXISTIR ELIMINA LAS LINEAS QUE YA ESTEN EN 2 EMBARQUES EN SUBORDINADO_IDS
        if 'remision_ids' in values:
            for remision in values['remision_ids']:
                print 'remision: ',remision
                if remision[2]:
                    res = self.env['carta.porte.line'].search([['remision_id', '=', remision[2]['remision_id'] ]])
                    if len(res) >= 2:
                        picking = self.env['stock.picking'].search([['id','=',remision[2]['remision_id']]])
                        #raise Warning(_("Error!"), _('La remision ' + picking.name + ' ya contiene 2 embarques'))
                        raise ValidationError(_('La remision ' + picking.name + ' ya contiene 2 embarques'))
                        #print '-----'
                        return False

        return super(CartaPorte, self).write(values)

    ###########################################
    #METODOS DE CAMBIO DE ESTADO
    ###########################################
    @api.multi
    def action_block(self):
        self.state = 'bloqueado'
    

    @api.multi
    def action_unblock(self):
        self.state = 'abierto'


    # def _get_default_company(self):
    #     print '_get_default_company'
    #     company_id = self.penv['res.users']._get_company()
    #     return company_id

    #name = fields.Char('Carta Porte', required=True, readonly=True)
    name = fields.Char('Carta Porte', size=128, required=True, default=lambda self: _('New'), readonly=True)
    remision_ids = fields.One2many('carta.porte.line', 'name', 'Remisiones')
    #company_id = fields.Many2one('res.company', 'Compañia', required=True)

    transportista_id = fields.Many2one('res.partner', 'Transportista', required=True, domain="[('transportista', '=', True)]")
    destino = fields.Char(string='Destino')
    fecha_cierre = fields.Date(String='Fecha cierre', track_visibility='onchange', write=['raloy_carta_porte.carta_porte_admin'])

    rango_inicial = fields.Integer(string='Rango Inicial')
    rango_final = fields.Integer(string='Rango Final')
    costo_maniobra = fields.Float(string='Costo de maniobra')
    costo_entrega = fields.Float(string='Costo de energia')
    costo_flete = fields.Float(string='Costo de flete')
    costo_excedente = fields.Float(string='Costo excedente')
    costo_ucarga = fields.Float(string='Costo X unidad de carga')
    costo_total= fields.Float(string='Costo total')
    chofer = fields.Char(string='Chofer')
    tipo_transporte = fields.Char(string='Tipo de transporte')
    capacidad = fields.Char(string='Capacidad')
    tarifa = fields.Char(string='Tarifa')
    sellos = fields.Char(string='Sellos')
    carta_porte = fields.Char(string='Carta Porte')
    placas = fields.Char(string='Placas')
    tanque = fields.Char(string='Tanque')
    operador = fields.Char(string='Operador')
    monto_gasolina = fields.Float(string='Monto gasolina')
    kms = fields.Char(string='Kms')
    observaciones = fields.Text(string='Observaciones')
    certificado = fields.Boolean(string='Recibio certificado de calidad')
    documentos = fields.Boolean(string='Recibio documentos')
    state = fields.Selection([
        ('abierto','Abierto'),
        ('bloqueado','Bloqueado'),
        ],'Estado', default='abierto', readonly=True, track_visibility='onchange', help="Etapa")
