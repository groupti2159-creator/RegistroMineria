"""
Módulo de Workflow para Desvios SSOMA
Maneja la lógica de transiciones de estado y validaciones
"""

from extensions import mysql
from utils.helpers import sp_exec, sp_one
from datetime import datetime


class EstadoWorkflow:
    """Clase para manejar el flujo de estados de registros"""
    
    # Estados válidos
    PENDIENTE = 'Pendiente'
    ASIGNADO = 'Asignado'
    EN_PROCESO = 'En Proceso'
    ENVIADO = 'Enviado'
    EN_REVISION = 'En Revision'
    CULMINADO = 'Culminado'
    RECHAZADO = 'Rechazado'
    CERRADO = 'Cerrado'
    ATRASADO = 'Atrasado'
    
    ESTADOS_VALIDOS = [
        PENDIENTE, ASIGNADO, EN_PROCESO, ENVIADO, 
        EN_REVISION, CULMINADO, RECHAZADO, CERRADO, ATRASADO
    ]
    
    @staticmethod
    def validar_transicion(idregistro, estado_nuevo, usuario_rol_id):
        """
        Valida si la transición de estado es permitida
        
        Args:
            idregistro: ID del registro
            estado_nuevo: Estado destino
            usuario_rol_id: ID del usuario que hace el cambio
            
        Returns:
            dict: {'valido': bool, 'mensaje': str}
        """
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                CALL sp_validar_transicion_estado(%s, %s, @valido, @mensaje)
            """, (idregistro, estado_nuevo))
            
            cur.execute("SELECT @valido AS valido, @mensaje AS mensaje")
            resultado = cur.fetchone()
            cur.close()
            
            return {
                'valido': resultado['valido'] if resultado else False,
                'mensaje': resultado['mensaje'] if resultado else 'Error desconocido'
            }
        except Exception as e:
            return {
                'valido': False,
                'mensaje': f'Error al validar transición: {str(e)}'
            }
    
    @staticmethod
    def cambiar_estado(idregistro, estado_nuevo, usuario_rol_id, comentario=''):
        """
        Cambia el estado de un registro con auditoría
        
        Args:
            idregistro: ID del registro
            estado_nuevo: Estado destino
            usuario_rol_id: ID del usuario que hace el cambio
            comentario: Comentario opcional del cambio
            
        Returns:
            dict: {'exito': bool, 'mensaje': str}
        """
        try:
            # Validar primero
            validacion = EstadoWorkflow.validar_transicion(idregistro, estado_nuevo, usuario_rol_id)
            if not validacion['valido']:
                return {
                    'exito': False,
                    'mensaje': validacion['mensaje']
                }
            
            # Cambiar estado
            cur = mysql.connection.cursor()
            cur.execute("""
                CALL sp_cambiar_estado_registro(%s, %s, %s, %s, @exito, @mensaje)
            """, (idregistro, estado_nuevo, usuario_rol_id, comentario))
            
            cur.execute("SELECT @exito AS exito, @mensaje AS mensaje")
            resultado = cur.fetchone()
            mysql.connection.commit()
            cur.close()
            
            return {
                'exito': resultado['exito'] if resultado else False,
                'mensaje': resultado['mensaje'] if resultado else 'Error desconocido'
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al cambiar estado: {str(e)}'
            }
    
    @staticmethod
    def cambiar_estado_automatico(idregistro, evento):
        """
        Cambia el estado automáticamente según un evento
        
        Args:
            idregistro: ID del registro
            evento: Tipo de evento ('supervisor_sube_imagenes', 'admin_aprueba_imagenes', etc.)
            
        Returns:
            dict: {'exito': bool, 'mensaje': str}
        """
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                CALL sp_cambiar_estado_automatico(%s, %s, @exito, @mensaje)
            """, (idregistro, evento))
            
            cur.execute("SELECT @exito AS exito, @mensaje AS mensaje")
            resultado = cur.fetchone()
            mysql.connection.commit()
            cur.close()
            
            return {
                'exito': resultado['exito'] if resultado else False,
                'mensaje': resultado['mensaje'] if resultado else 'Sin cambios'
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al cambiar estado automáticamente: {str(e)}'
            }
    
    @staticmethod
    def obtener_estado_actual(idregistro):
        """
        Obtiene el estado actual de un registro
        
        Args:
            idregistro: ID del registro
            
        Returns:
            str: Nombre del estado actual
        """
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT e.estado 
                FROM tbl_registro r
                JOIN tbl_estado e ON r.idestado = e.idestado
                WHERE r.idregistro = %s
            """, (idregistro,))
            resultado = cur.fetchone()
            cur.close()
            
            return resultado['estado'] if resultado else None
        except Exception as e:
            print(f"Error al obtener estado: {str(e)}")
            return None
    
    @staticmethod
    def obtener_transiciones_permitidas(idregistro):
        """
        Obtiene las transiciones de estado permitidas desde el estado actual
        
        Args:
            idregistro: ID del registro
            
        Returns:
            list: Lista de estados destino permitidos
        """
        try:
            estado_actual = EstadoWorkflow.obtener_estado_actual(idregistro)
            if not estado_actual:
                return []
            
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT estado_destino 
                FROM tbl_transiciones_estado 
                WHERE estado_origen = %s AND activo = TRUE
                ORDER BY estado_destino
            """, (estado_actual,))
            
            resultados = cur.fetchall()
            cur.close()
            
            return [r['estado_destino'] for r in resultados]
        except Exception as e:
            print(f"Error al obtener transiciones: {str(e)}")
            return []
    
    @staticmethod
    def obtener_historial_cambios(idregistro):
        """
        Obtiene el historial de cambios de estado de un registro
        
        Args:
            idregistro: ID del registro
            
        Returns:
            list: Lista de cambios de estado
        """
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    idauditoria,
                    estado_anterior,
                    estado_nuevo,
                    comentario,
                    fecha_cambio,
                    usuario_cambio
                FROM vw_historial_cambios_estado
                WHERE idregistro = %s
                ORDER BY fecha_cambio DESC
            """, (idregistro,))
            
            resultados = cur.fetchall()
            cur.close()
            
            return resultados if resultados else []
        except Exception as e:
            print(f"Error al obtener historial: {str(e)}")
            return []
    
    @staticmethod
    def validar_requisitos_estado(idregistro, estado_destino):
        """
        Valida que el registro cumpla con los requisitos del estado destino
        
        Args:
            idregistro: ID del registro
            estado_destino: Estado destino
            
        Returns:
            dict: {'cumple': bool, 'requisitos_faltantes': list}
        """
        try:
            cur = mysql.connection.cursor()
            
            # Obtener requisitos del estado
            cur.execute("""
                SELECT 
                    requiere_imagenes_aprobadas,
                    requiere_responsable,
                    requiere_ccta,
                    requiere_descripcion,
                    requiere_accion,
                    min_imagenes
                FROM tbl_validaciones_estado
                WHERE estado = %s
            """, (estado_destino,))
            
            requisitos = cur.fetchone()
            if not requisitos:
                cur.close()
                return {'cumple': True, 'requisitos_faltantes': []}
            
            # Obtener datos del registro
            cur.execute("""
                SELECT 
                    idpersonalresponsable,
                    idcctaresponsable,
                    descripcion,
                    accion
                FROM tbl_registro
                WHERE idregistro = %s
            """, (idregistro,))
            
            registro = cur.fetchone()
            
            # Contar imágenes
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN idestadoimagen = 2 THEN 1 ELSE 0 END) AS aprobadas,
                    SUM(CASE WHEN idestadoimagen = 1 THEN 1 ELSE 0 END) AS pendientes,
                    COUNT(*) AS total
                FROM tbl_imagenregistro
                WHERE idregistro = %s
            """, (idregistro,))
            
            imagenes = cur.fetchone()
            cur.close()
            
            requisitos_faltantes = []
            
            # Validar cada requisito
            if requisitos['requiere_imagenes_aprobadas'] and (not imagenes or imagenes['aprobadas'] == 0):
                requisitos_faltantes.append('Se requiere al menos 1 imagen aprobada')
            
            if requisitos['requiere_responsable'] and not registro['idpersonalresponsable']:
                requisitos_faltantes.append('Se requiere asignar un responsable')
            
            if requisitos['requiere_ccta'] and not registro['idcctaresponsable']:
                requisitos_faltantes.append('Se requiere asignar un CCTA responsable')
            
            if requisitos['requiere_descripcion'] and not registro['descripcion']:
                requisitos_faltantes.append('Se requiere una descripción del incidente')
            
            if requisitos['requiere_accion'] and not registro['accion']:
                requisitos_faltantes.append('Se requiere describir la acción realizada')
            
            if requisitos['min_imagenes'] > 0 and (not imagenes or imagenes['total'] < requisitos['min_imagenes']):
                requisitos_faltantes.append(f'Se requieren al menos {requisitos["min_imagenes"]} imagen(es)')
            
            return {
                'cumple': len(requisitos_faltantes) == 0,
                'requisitos_faltantes': requisitos_faltantes
            }
        except Exception as e:
            print(f"Error al validar requisitos: {str(e)}")
            return {'cumple': False, 'requisitos_faltantes': [f'Error: {str(e)}']}
    
    @staticmethod
    def obtener_estado_registro_completo(idregistro):
        """
        Obtiene información completa del estado actual del registro
        
        Args:
            idregistro: ID del registro
            
        Returns:
            dict: Información completa del estado
        """
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    idregistro,
                    codigo,
                    estado,
                    estado_anterior,
                    fecha_cambio_estado,
                    imagenes_aprobadas,
                    imagenes_pendientes,
                    imagenes_rechazadas
                FROM vw_estado_registro
                WHERE idregistro = %s
            """, (idregistro,))
            
            resultado = cur.fetchone()
            cur.close()
            
            if resultado:
                # Obtener transiciones permitidas
                transiciones = EstadoWorkflow.obtener_transiciones_permitidas(idregistro)
                resultado['transiciones_permitidas'] = transiciones
            
            return resultado if resultado else None
        except Exception as e:
            print(f"Error al obtener estado completo: {str(e)}")
            return None


class EventosWorkflow:
    """Clase para manejar eventos que disparan cambios de estado"""
    
    @staticmethod
    def supervisor_sube_imagenes(idregistro, usuario_rol_id):
        """
        Evento: Supervisor sube imágenes de levantamiento
        Cambio automático: ENVIADO → EN REVISIÓN
        """
        return EstadoWorkflow.cambiar_estado_automatico(
            idregistro, 
            'supervisor_sube_imagenes'
        )
    
    @staticmethod
    def admin_aprueba_imagenes(idregistro, usuario_rol_id):
        """
        Evento: Admin aprueba imágenes
        Cambio automático: EN REVISIÓN → CULMINADO
        """
        return EstadoWorkflow.cambiar_estado_automatico(
            idregistro,
            'admin_aprueba_imagenes'
        )
    
    @staticmethod
    def admin_rechaza_imagenes(idregistro, usuario_rol_id):
        """
        Evento: Admin rechaza imágenes
        Cambio automático: EN REVISIÓN → RECHAZADO
        """
        return EstadoWorkflow.cambiar_estado_automatico(
            idregistro,
            'admin_rechaza_imagenes'
        )
    
    @staticmethod
    def crear_registro(idregistro, usuario_rol_id):
        """
        Evento: Se crea un nuevo registro
        Estado inicial: PENDIENTE (ya se asigna en sp_crearregistro)
        """
        pass
    
    @staticmethod
    def eliminar_registro(idregistro):
        """
        Evento: Se elimina un registro
        Limpia auditoría y cambios de estado
        """
        try:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM tbl_auditoria_estado WHERE idregistro = %s", (idregistro,))
            mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error al limpiar auditoría: {str(e)}")
            return False
