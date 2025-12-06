import chess
import random
import csv
import os
import string

class Tarjetero:
    """Gestiona la lógica de un Tarjetero"""
    def __init__(self, db_path="resources/tarjetas/tarjetero.csv"):
        self.db_path = db_path
        self.tarjetas = []
        self.fieldnames = ['PuzzleId', 'FEN', 'Moves', 'Rating', 'Title', 'Themes', 'Description', 'Stars', 'User', 'GameURL']
        self.load_database()

        
    def load_database(self):
        """Carga el tarjetero CSV y actualiza la lista en memoria."""
        self.tarjetas = []
        if not os.path.exists(self.db_path):
            print(f"No se encontró {self.db_path}. Usando tarjeta genérica.")
            # Datos falsos de respaldo por si no hay archivo
            self.tarjetas = [
                {
                    'FEN': chess.STARTING_FEN, 
                    'Rating': '0', 
                    'Title': 'Posición Inicial'
                }
            ]
            return

        try:
            # Leemos el csv de lichess
            with open(self.db_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                    
                # Cargamos las tarjetas en una lista.
                for row in reader:
                    if row and row.get('FEN'): 
                        self.tarjetas.append(row)
                
        except Exception as e:
            print(f"Error al leer CSV: {e}")


    def get_random_puzzle(self, min_rating=0, max_rating=3000): 
        if not self.tarjetas: return None               
        return random.choice(self.tarjetas)
    
    
    def guardar_tarjeta(self, data_dict):
        """
        Guarda una tarjeta nueva y la anexa al tarjetero CSV.
        """
        archivo_nuevo = not os.path.exists(self.db_path)
        
        try:
            with open(self.db_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                
                # Si el archivo no existe, lo creamos
                if archivo_nuevo:
                    writer.writeheader()
                
                # Escribimos la nueva tarjeta
                writer.writerow(data_dict)
            
            # Recargamos la lista en memoria para que aparezca en el tarjetero
            self.load_database()
            return True
        except Exception as e:
            print(f"Error al guardar tarjeta: {e}")
            return False
        
    
    def generate_unique_id(self):
        """Genera un ID de 5 caracteres no existente en el tarjetero"""
        # Creamos un set con los IDs existentes para búsqueda rápida
        existing_ids = set(t.get('PuzzleId', '') for t in self.tarjetas)
        
        # Caracteres alfanuméricos
        chars = string.ascii_letters + string.digits
        
        while True:
            # Generar un ID aleatorio 
            new_id = ''.join(random.choices(chars, k=5))
            
            # Si no existe, lo retornamos. Si existe, intenta creando otro.
            if new_id not in existing_ids:
                return new_id