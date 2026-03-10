"""
Helper para hacer que los diccionarios de MySQL sean case-insensitive
Esto permite que el código funcione tanto en Windows como en Linux/Railway
"""

class CaseInsensitiveDict(dict):
    """Diccionario que permite acceso case-insensitive a las claves"""
    
    def __getitem__(self, key):
        # Primero intenta con la clave original
        if key in self.keys():
            return super().__getitem__(key)
        
        # Si no existe, busca case-insensitive
        for k in self.keys():
            if k.lower() == key.lower():
                return super().__getitem__(k)
        
        # Si no encuentra nada, retorna None en lugar de error
        return None
    
    def get(self, key, default=None):
        result = self.__getitem__(key)
        return result if result is not None else default

def make_case_insensitive(row):
    """Convierte un diccionario normal en uno case-insensitive"""
    if row is None:
        return None
    return CaseInsensitiveDict(row)

def make_list_case_insensitive(rows):
    """Convierte una lista de diccionarios en case-insensitive"""
    if not rows:
        return []
    return [make_case_insensitive(row) for row in rows]
