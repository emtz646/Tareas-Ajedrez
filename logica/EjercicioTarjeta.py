import chess

class EjercicioTarjeta:
    def __init__(self):
        self.board = chess.Board()
        self.solution_moves = []  # Lista de movimientos esperados
        self.move_index = 0       # Índice actual en la lista de movimientos solución
        self.status = "idle"      # idle, playing, solved, failed


    def load_ejercicio(self, fen, moves_str):
        """
        Carga datos de tarjeta y configura ejercicio en preview.
        """
        self.board = chess.Board(fen)
        self.solution_moves = moves_str.split() if moves_str else []
        self.move_index = 0
        self.status = "preview"
        

    def iniciar_ejercicio(self):
        """
        Inicia ejercicio de tarjeta y realiza el movimiento del oponente.
        """
        self.status = "playing"
        
        # Ejecutamos primer movimiento (del oponente)
        if len(self.solution_moves) > 0:
            first_move_str = self.solution_moves[0]
            try:
                move = chess.Move.from_uci(first_move_str)
                self.board.push(move)
                self.move_index = 1 # Cambio de turno al usuario
                return True # Indica que el ejercicio inició correctamente
            except:
                print("Error movimiento inicial")
                return False
        return False

    def intentar_movimiento(self, start_sq, end_sq):
        """
        Valida si el movimiento del usuario es legal y correcto a la tarjeta.
        Return: (es_correcto: bool, move_obj: chess.Move o None)
        """
        
        # Si no está en estado "playing", no se puede mover nadaS
        if self.status != "playing":
            return False, None

        # Crear objeto movimiento
        move = chess.Move(start_sq, end_sq)
        
        # Detectar promoción
        piece = self.board.piece_at(start_sq)
        if piece and piece.piece_type == chess.PAWN:
            if (chess.square_rank(end_sq) == 7 and self.board.turn == chess.WHITE) or \
               (chess.square_rank(end_sq) == 0 and self.board.turn == chess.BLACK):
                move.promotion = chess.QUEEN

        # Verificar si jugada es legal
        if move not in self.board.legal_moves:
            return False, None

        # Verificar si jugada es solución
        if self.move_index < len(self.solution_moves):
            expected_uci = self.solution_moves[self.move_index]
            
            if move.uci() == expected_uci:
                # Si es correcta, se aplica el movimiento
                self.board.push(move)
                self.move_index += 1
                
                if self.move_index >= len(self.solution_moves):
                    self.status = "solved"
                
                return True, move
            else:
                self.status = "failed"
                return False, move
        
        return False, None


    def jugar_respuesta(self):
        """Juega el siguiente movimiento del rival (computadora) si existe"""
        if self.move_index < len(self.solution_moves):
            next_move_uci = self.solution_moves[self.move_index]
            move = chess.Move.from_uci(next_move_uci)
            self.board.push(move)
            self.move_index += 1
            return True
        return False

    def obtener_correccion(self):
        """Realiza el movimiento correcto en el tablero (si el usuario falla)"""
        if self.move_index < len(self.solution_moves):
            correct_uci = self.solution_moves[self.move_index]
            move = chess.Move.from_uci(correct_uci)
            self.board.push(move)
            self.move_index += 1
            
            # Verifica si con esta corrección ya acabó el ejercicio
            if self.move_index >= len(self.solution_moves):
                self.status = "solved"
            
            return move
        return None

    def get_fen(self):
        return self.board.fen()