import chess
from PIL import Image, ImageDraw, ImageFont

class Diagrama:
    
    def __init__(self, font_path, square_size=65):
        self.square_size = square_size
        self.font_path = font_path
        self.font = None 
        
        # --- Estilo tipo libro/periódico ---
        self.paper_color = (220, 220, 220) # Gris claro 
        self.grain_intensity = 0.15
        
        # Ajuste para casillas blancas
        self.offset_light_x = 0  
        self.offset_light_y = int(square_size * 0.018) 
        
        # Ajustes para casillas negras 
        self.offset_dark_x = 0
        self.offset_dark_y = 0

        self._init_resources()
        self._init_mapping()
        
        
    def _init_resources(self):
        try:
            # Cargar fuente
            self.font = ImageFont.truetype(self.font_path, int(self.square_size))
        except IOError:
            print(f"Error: No se encontró la fuente en la dirección {self.font_path}")
            self.font = None
            
            
    def _init_mapping(self):
        """Crea el mapa de caracteres respectivo a la fuente de diagrama"""
        self.char_map = {
            # --- PIEZAS BLANCAS  ---
            chess.WHITE: {
                # Peón: Casilla Clara='P', Casilla Oscura=')'
                chess.PAWN:   {True: 'P', False: ')'},
                # Caballo: Casilla Clara='N', Casilla Oscura='H'
                chess.KNIGHT: {True: 'N', False: 'H'},
                # Alfil: Casilla Clara='B', Casilla Oscura='G'
                chess.BISHOP: {True: 'B', False: 'G'},
                # Torre: Casilla Clara='R', Casilla Oscura='$'
                chess.ROOK:   {True: 'R', False: '$'},
                # Reina: Casilla Clara='Q', Casilla Oscura='!'
                chess.QUEEN:  {True: 'Q', False: '!'},
                # Rey: Casilla Clara='K', Casilla Oscura='I'
                chess.KING:   {True: 'K', False: 'I'},
            },
            # --- PIEZAS NEGRAS ---
            chess.BLACK: {
                # Peón: Casilla Clara='p', Casilla Oscura='0' (Cero)
                chess.PAWN:   {True: 'p', False: '0'},
                # Caballo: Casilla Clara='n', Casilla Oscura='h'
                chess.KNIGHT: {True: 'n', False: 'h'},
                # Alfil: Casilla Clara='b', Casilla Oscura='g'
                chess.BISHOP: {True: 'b', False: 'g'},
                # Torre: Casilla Clara='r', Casilla Oscura='4'
                chess.ROOK:   {True: 'r', False: '4'},
                # Reina: Casilla Clara='q', Casilla Oscura='1' (Uno)
                chess.QUEEN:  {True: 'q', False: '1'},
                # Rey: Casilla Clara='k', Casilla Oscura='i'
                chess.KING:   {True: 'k', False: 'i'},
            }
        }
        # Caracteres para casillas vacías
        # w = blanca, d = negra
        self.empty_squares = {True: 'w', False: 'd'}
        
    
    
    def _apply_grain(self, base_image):
        """Genera granulado y lo fusiona con la imagen base"""
        if self.grain_intensity <= 0:
            return base_image
            
        # Generar capa de ruido gaussiano 
        noise = Image.effect_noise(base_image.size, 20).convert("RGB")
        
        # Mezclar imagen base con ruido
        return Image.blend(base_image, noise, self.grain_intensity)
    
    # Método por FEN
    def generate_FEM_diagram(self, fen, status_overlay=None, highlight_square=None):
        """"Recibe un FEN y devuelve diagrama como PIL Image"""
        board = chess.Board(fen)
        return self._render_FEN_grid(board, status_overlay, highlight_square)

    # --- Método directo por texto de fuente---
    def generate_raw_diagram(self, raw_text):
        """
        Dibuja directamente los caracteres del texto en el diagrama.
        """
        clean_text = "".join(raw_text.split()) # Limpiar texto
        if len(clean_text) != 64:
            raise ValueError(f"Se requieren exactamente 64 caracteres. Se encontraron {len(clean_text)}")

        return self._render_raw_grid(clean_text)
    
    
    
    # --- LOGICA DE DIBUJADO ---
    def _render_FEN_grid(self, board, status_overlay, highlight_square):
        # Convertimos estado de tablero lógico a una lista de caracteres para dibujar
        chars_to_draw = []

        for rank in range(7, -1, -1):
            for file in range(8):
                square = chess.square(file, rank)
                is_light = (rank + file) % 2 != 0 # Revisamos si es casilla blanca
                piece = board.piece_at(square)
                if piece:
                    char = self.char_map[piece.color][piece.piece_type][is_light]
                else:
                    char = self.empty_squares[is_light]
                chars_to_draw.append(char)
        
        return self._render_raw_grid("".join(chars_to_draw), status_overlay, highlight_square)
    
    
    def _render_raw_grid(self, char_string, status_overlay=None, highlight_square=None):
        """Toma 64 chars de texto y dibuja el diagrama correspondiente"""
        board_size = self.square_size * 8
        
        # Lienzo blanco inicial
        img = Image.new('RGB', (board_size, board_size), self.paper_color)
        img = self._apply_grain(img)
        draw = ImageDraw.Draw(img)

        if not self.font: return img

        for i, char in enumerate(char_string):
            # i va de 0 a 63 (De arriba a la izquierda hacia abajo a la derecha)
            col = i % 8
            row = i // 8
            
            x = col * self.square_size
            y = row * self.square_size
            
            # Corrección de posición visual
            # Si (row + col) es par -> Casilla blanca 
            is_light = (row + col) % 2 == 0

            center_x = x + (self.square_size / 2)
            center_y = y + (self.square_size / 2)
            
            final_x = center_x + (self.offset_light_x if is_light else self.offset_dark_x)
            final_y = center_y + (self.offset_light_y if is_light else self.offset_dark_y)

            # Dibujar resaltado de selección si existe
            visual_square = chess.square(col, 7-row)
            
            if highlight_square == visual_square:
                # Dibujar recuadro amarillo semitransparente
                 draw.rectangle([x+2, y+2, x+self.square_size-2, y+self.square_size-2], outline="#D4AC0D", width=4)

            draw.text((final_x, final_y), char, font=self.font, fill="black", anchor="mm")

        if status_overlay:
            self._draw_status(draw, board_size, status_overlay)
            
        return img


    
    def _draw_status(self, draw, size, status):
        """Dibuja un símbolo gigante semitransparente encima"""
        # Coordenadas del centro
        cx, cy = size / 2, size / 2
        radius = size / 4
        
        if status == 'error':
            # Cruz Roja 
            color = (255, 0, 0)
            w = 20 
            draw.line((cx-radius, cy-radius, cx+radius, cy+radius), fill=color, width=w)
            draw.line((cx-radius, cy+radius, cx+radius, cy-radius), fill=color, width=w)
            
        elif status == 'ok':
            # Palomita Verde
            color = (0, 200, 0)
            w = 20
            points = [
                (cx - radius, cy),
                (cx - radius/4, cy + radius/1.5),
                (cx + radius, cy - radius)
            ]
            draw.line(points, fill=color, width=w, joint="curve")
    