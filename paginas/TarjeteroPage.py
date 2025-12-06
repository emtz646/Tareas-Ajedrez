import customtkinter as ctk
import os
import chess
from logica.Diagrama import Diagrama
from logica.Tarjetero import Tarjetero
from logica.EjercicioTarjeta import EjercicioTarjeta

# ======================================================
# PÁGINA PARA TARJETERO
# ======================================================
class TarjeteroPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # --- Página principal ---
        self.grid_columnconfigure(0, weight=3) # Tablero
        self.grid_columnconfigure(1, weight=1) # Lista (tarjetero)
        self.grid_rowconfigure(0, weight=1)
        
        # Creamos diagrama
        font_path = os.path.join("paginas/fuentes/Zurich/ZURID___.TTF")
        self.renderer = Diagrama(font_path=font_path, square_size=50) 
        self.tarjetero = Tarjetero()
        
        # Ancho del tablero para usarlo como margen para la info.
        self.board_pixel_width = self.renderer.square_size * 8
        
        # Instancia de ejercicio
        self.juego = EjercicioTarjeta() 
        self.drag_start_sq = None
        
        # FEN para tablero vacío inicial
        self.EMPTY_FEN = "8/8/8/8/8/8/8/8 w - - 0 1"
        
        # --- INTERFAZ ---
        self._init_tarjeta_diagrama()  # Panel del tablero
        self._init_tarjetero() # Panel de lista y búsqueda
        
        # Cargar lista completa y mostrar tablero vacío inicial
        self.update_list() 
        self.show_empty_board()
     
        
    def _init_tarjeta_diagrama(self):
            """Crea el área del la tarjeta y con tablero y su información abajo"""
            self.tarjeta_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.tarjeta_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            
            # Título
            self.title_lbl = ctk.CTkLabel(self.tarjeta_frame, text="Tarjeta:", font=("Times New Roman", 28, "bold"))
            self.title_lbl.pack(pady=(0, 20))

            # Tablero
            self.board_display = ctk.CTkLabel(self.tarjeta_frame, text="")
            self.board_display.pack(pady=10)
            self.board_display.bind("<Button-1>", self.on_board_click)
            
            # Botón para comenzar ejercicio
            self.btn_start_ejercicio = ctk.CTkButton(
                self.tarjeta_frame, 
                text="▶ COMENZAR EJERCICIO", 
                fg_color="#B8662E", 
                hover_color="#875E43",
                height=40,
                font=("Times New Roman", 14, "bold"),
                state="disabled", # Se activa al elegir tarjeta
                command=self.inicia_logica_ejercicio
            )
            self.btn_start_ejercicio.pack(pady=10)

            # Información (Rating, Temas, etc)
            self.txt_info = ctk.CTkTextbox(
                self.tarjeta_frame,
                font=("Times New Roman", 16),
                height=150,
                width=self.board_pixel_width,
                fg_color="transparent",
                wrap="word",
                activate_scrollbars=True
            )
            self.txt_info.pack(pady=10)
            
            # Texto inicial
            self.txt_info.insert("0.0", "Selecciona una tarjeta:")
            self.txt_info.configure(state="disabled")


    def _init_tarjetero(self):
        """Crea el tarjetero: barra lateral derecha con buscador y lista"""
        self.tarjetero_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.tarjetero_frame.grid(row=0, column=1, sticky="nsew")

        # --- Header con botón para crear tarjetas ---
        header_frame = ctk.CTkFrame(self.tarjetero_frame, fg_color="transparent")
        header_frame.pack(pady=(15, 10), padx=10, fill="x")
        
        # Título
        lbl_titulo = ctk.CTkLabel(header_frame, text="Tarjetero", font=("Times New Roman", 28, "bold"))
        lbl_titulo.pack(side="left")
        
        # Botón "+" para crear
        self.btn_add = ctk.CTkButton(
            header_frame, 
            text="+", 
            width=30, 
            height=30, 
            fg_color="green", 
            hover_color="#2D582D",
            command=self.open_creator
        )
        self.btn_add.pack(side="right")
        
        # Filtro por calificación
        self.filter_stars_var = ctk.StringVar(value="Cualquier calificación")
        self.option_stars = ctk.CTkOptionMenu(
            self.tarjetero_frame,
            values=[
                "Todas las estrellas", 
                "★☆☆☆☆", 
                "★★☆☆☆", 
                "★★★☆☆", 
                "★★★★☆", 
                "★★★★★"],
            command=self.filter_list, 
            variable=self.filter_stars_var,
            width=180
        )
        self.option_stars.pack(padx=10, pady=(0, 10), anchor="w")
        
        # Buscador
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_list) # Detectar escritura
        self.entry_search = ctk.CTkEntry(
            self.tarjetero_frame, 
            placeholder_text="Buscar tema o título...",
            textvariable=self.search_var
        )
        self.entry_search.pack(fill="x", padx=10, pady=(0, 10))

        # Lista scrolleable 
        self.scroll_list = ctk.CTkScrollableFrame(self.tarjetero_frame, label_text="Tarjetas Disponibles", label_font=("Times New Roman", 15, "bold"))
        self.scroll_list.pack(expand=True, fill="both", padx=10, pady=5)

        # Botón random
        self.btn_random = ctk.CTkButton(
            self.tarjetero_frame, 
            text="Elegir al azar", 
            fg_color="#B8662E", 
            hover_color="#875E43",
            height=40,
            command=self.load_random_tarjeta
        )
        self.btn_random.pack(fill="x", padx=20, pady=20, side="bottom")
        



    # ==========================================
    # LÓGICA DE FILTRADO Y BÚSQUEDA
    # ==========================================
    def update_list(self, filtered_data=None):
        """
        Actualiza la lista (botones) del tarjetero.
        :param filtered_data: Lista filtrada de tarjetas. Si es None, muestra todass.
        """
        # Limpiar lista actual
        for widget in self.scroll_list.winfo_children():
            widget.destroy()

        # Obtener datos (todos o con filtros)
        data_source = filtered_data if filtered_data is not None else self.tarjetero.tarjetas

        if not data_source:
            ctk.CTkLabel(self.scroll_list, text="No hay coincidencias.").pack(pady=10)
            return

        # Crear botones
        for tarjeta in data_source:
            # Texto de botón: Título + Calificación + Elo
            title = tarjeta.get('Title', 'Sin Título')
            stars_count = int(tarjeta.get('Stars', 0))
            stars_str = self._get_star_string(stars_count)
            elo = tarjeta.get('Rating', '???')
            
            # Limitamos longitud del título en el botón 
            if len(title) > 35: title = title[:32] + "..."
            
            card_btn = ctk.CTkFrame(
                self.scroll_list, 
                fg_color=("gray85", "gray25"),
                corner_radius=6,
                border_width=1,
                border_color=("gray70", "gray35")
            )
            card_btn.pack(fill="x", pady=2, padx=5)
            
            # Grid interno del botón
            card_btn.grid_columnconfigure(0, weight=1) # Texto 
            card_btn.grid_columnconfigure(1, weight=0) #Estrellas (fijas a la derecha)

            # Título
            lbl_title = ctk.CTkLabel(
                card_btn, 
                text=title, 
                font=("Times New Roman", 13, "bold"), 
                anchor="w",
                text_color=("gray10", "gray90")
            )
            lbl_title.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=(5, 0))

            # Elo 
            lbl_elo = ctk.CTkLabel(
                card_btn, 
                text=f"Elo: {elo}", 
                font=("Times New Roman", 11), 
                text_color="#847D71", 
                anchor="w"
            )
            lbl_elo.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=(0, 5))

            # Estrellas (Derecha, centrado verticalmente ocupando las 2 filas)
            lbl_stars = ctk.CTkLabel(
                card_btn, 
                text=stars_str, 
                font=("Times New Roman", 16), 
                text_color="#F0E3CE"
            )
            lbl_stars.grid(row=0, column=1, rowspan=2, padx=10, sticky="e")
            
            callback = lambda event, p=tarjeta: self.load_tarjeta(p)
            hover_enter = lambda e, f=card_btn: f.configure(border_color="#F0E3CE") 
            hover_leave = lambda e, f=card_btn: f.configure(border_color=("gray70", "gray35"))
            
            for widget in [card_btn, lbl_title, lbl_elo, lbl_stars]:
                widget.bind("<Button-1>", callback)
                widget.configure(cursor="hand2")
                
                # Cambio de color al posicionar cursor
                widget.bind("<Enter>", hover_enter)
                widget.bind("<Leave>", hover_leave)


    def filter_list(self, *args):
        """Filtra la lista de acuerdo al texto del buscador"""
        search_text = self.search_var.get().lower()
        star_selection = self.filter_stars_var.get()
        
        # Convertir selección de estrellas a número (o None si son todas)
        target_stars = None
        if "★" in star_selection:
            target_stars = star_selection.count("★")

        filtered = []
        for p in self.tarjetero.tarjetas:
            # BMatch por búsqueda
            text_match = (search_text == "") or \
                         (search_text in p.get('Title', '').lower()) or \
                         (search_text in p.get('Themes', '').lower())
            
            # Match por calificación
            p_stars = int(p.get('Stars', 0))
            star_match = (target_stars is None) or (p_stars == target_stars)

            # Si cumple ambas condiciones, se agrega
            if text_match and star_match:
                filtered.append(p)

        self.update_list(filtered)


    def _get_star_string(self, count):
        """Helper para convertir un int (3) en string '★★★☆☆'"""
        try:
            n = int(count)
            n = max(0, min(n, 5))
            return "★" * n + "☆" * (5 - n)
        except:
            return "☆☆☆☆☆"




    # ==========================================
    # LOGICA CLICKS
    # ==========================================

    def get_square_from_coords(self, x, y):
        sq_size = self.renderer.square_size
        col = x // sq_size
        row = 7 - (y // sq_size)
        if 0 <= col <= 7 and 0 <= row <= 7: return chess.square(col, row)
        return None

    def on_board_click(self, event):
        """Maneja la selección y movimiento por clics"""
        if self.juego.status != "playing": return # Solo si el juego está activo
        
        clicked_sq = self.get_square_from_coords(event.x, event.y)
        if clicked_sq is None: return

        # CASO 1: Si no hay nada seleccionado -> Intentamos seleccionar
        if self.selected_sq is None:
            piece = self.juego.board.piece_at(clicked_sq)
            # Solo seleccionamos si hay pieza y es del color turno
            if piece and piece.color == self.juego.board.turn:
                self.selected_sq = clicked_sq
                self._update_board_image() 
            return

        # CASO 2: Ya hay algo seleccionado -> Intentamos mover o cambiar selección
        # Si se hace click en la misma pieza, deseleccionamos
        if clicked_sq == self.selected_sq:
            self.selected_sq = None
            self._update_board_image()
            return
            
        # Si se hace click en OTRA pieza suya, cambiamos la selección
        piece = self.juego.board.piece_at(clicked_sq)
        if piece and piece.color == self.juego.board.turn:
            self.selected_sq = clicked_sq
            self._update_board_image()
            return

        # Si clise hace clickca en una casilla vacía o enemiga, INTENTAMOS MOVER
        es_correcto, move = self.juego.intentar_movimiento(self.selected_sq, clicked_sq)
        
        # Limpiamos selección
        self.selected_sq = None 

        if es_correcto:
            self._update_board_image()
            if self.juego.status == "solved":
                self.ejercicio_completado()
            else:
                self.after(500, self.jugar_respuesta)
        elif move is not None:
            # Movimiento legal pero incorrecto para ejercicio
            self.handle_mistake()
        else:
            # Movimiento ilegal -> Deseleccionamos visualmente
            self._update_board_image()



    # ==========================================
    # LOGICA DE EJERCICIO
    # ==========================================
    def jugar_respuesta(self):
        """Pide al modelo que juegue respuesta"""
        if self.juego.jugar_respuesta():
            self._update_board_image()


    def handle_mistake(self):
        """Manejo visual del error"""
        # Mostrar Tache sobre la posición actual
        self._update_board_image(overlay='error')
        
        def show_correction():
            # Pedir al modelo corregir el estado interno
            self.juego.obtener_correccion()
            # Actualizar vista
            self._update_board_image()
            # Continuar juego si no se ha terminado
            if self.juego.status != "solved":
                self.after(800, self.jugar_respuesta)
            else:
                self.ejercicio_completado()

        self.after(1000, show_correction)


    def ejercicio_completado(self):
        self._update_board_image(overlay='ok')
        self.btn_start_ejercicio.configure(text="✔ COMPLETADO", fg_color="#D35400")
        
        self.txt_info.configure(state="normal")
        self.txt_info.insert("end", "\n\n★ ¡EJERCICIO RESUELTO!")
        self.txt_info.configure(state="disabled")
    
    
    def inicia_logica_ejercicio(self):
        """Juego se ejecuta al pulsar el botón"""
        if self.juego.iniciar_ejercicio():
            self._update_board_image()
            
            # Avisar en cuadro de texto si es turno del usuario
            self.txt_info.configure(state="normal")
            self.txt_info.insert("end", "\n\n¡TU TURNO!")
            self.txt_info.configure(state="disabled")
            
            # Desactivar botón y cambiar texto
            self.btn_start_ejercicio.configure(text="Juego en curso...", state="disabled", fg_color="#847D71")
        else:
            print("No se pudo iniciar el juego (tal vez no hay movimientos en la tarjeta)")
    
    
    
    # ==========================================
    # LÓGICA DE PÁGINA
    # ==========================================
    def load_tarjeta(self, puzzle_data):
        """Muestra la tarjeta seleccionada"""
        if not puzzle_data: return

        # Extraer datos
        fen = puzzle_data.get('FEN', self.EMPTY_FEN)
        title = puzzle_data.get('Title', 'Sin Título')
        desc = puzzle_data.get('Description', 'Sin descripción')
        rating = puzzle_data.get('Rating', '?')
        user = puzzle_data.get('User', '???')
        stars_count = int(puzzle_data.get('Stars', 0))
        stars_str = self._get_star_string(stars_count)
        moves = puzzle_data.get('Moves', '')
        
        # Inicializar lógica
        self.juego.load_ejercicio(fen, moves)
        
        # Limpiar selección al cambiar tarjeta
        self.selected_sq = None 
        
        # Genera diagrama
        self._update_board_image()
        
        # Muestra info.
        info_text = (
            f"Título: {title}\n"
            f"Calificación: {stars_str}\n"
            f"Elo: {rating}\n\n"
            f"Descripción:\n{desc}\n\n"
            f"Proporcionado por: {user}"
        )
        self.txt_info.configure(state="normal") # Habilitar para escribir
        self.txt_info.delete("0.0", "end")      # Borrar anterior
        self.txt_info.insert("0.0", info_text)  # Escribir nuevo
        self.txt_info.configure(state="disabled")
        
        # Habilitar botón
        self.btn_start_ejercicio.configure(state="normal", text="▶ COMENZAR EJERCICIO", fg_color="#B8662E")


    def _update_board_image(self, overlay=None):
        fen = self.juego.get_fen()
        pil_image = self.renderer.generate_FEM_diagram(fen, status_overlay=overlay,highlight_square=self.selected_sq)
        ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(self.board_pixel_width, self.board_pixel_width))
        self.board_display.configure(image=ctk_img)


    def show_empty_board(self):
        """Muestra un tablero vacío"""
        self.juego.load_ejercicio(self.EMPTY_FEN, "")
        self.selected_sq = None
        self._update_board_image()
        self.btn_start_ejercicio.configure(state="disabled", text="Selecciona Tarjeta", fg_color="#847D71")
        
        self.txt_info.configure(state="normal")
        self.txt_info.delete("0.0", "end")
        self.txt_info.insert("0.0", "Elige un ejercicio del tarjetero\n o busca por nombre o filtro.")
        self.txt_info.configure(state="disabled")
        
        
    def load_random_tarjeta(self):
        """Boton de selección aleatoria"""
        tarjeta = self.tarjetero.get_random_puzzle()
        self.load_tarjeta(tarjeta)
        
        
        
        
    # --- Abrir ventana de creación de tarjeta ---
    def open_creator(self):
        # Crear ventana emergente 
        self.window_crear = ctk.CTkToplevel(self)
        self.window_crear.title("Crear Nueva Tarjeta")
        self.window_crear.geometry("400x550")
        
        # Encimamos la ventana
        self.window_crear.attributes("-topmost", True)
        
        # Instanciar página dentro de la ventana
        page = CreadorTarjetaPage(self.window_crear, on_close_callback=self.al_guardar_tarjeta)
        page.pack(fill="both", expand=True)


    def al_guardar_tarjeta(self):
        """Cierra ventana al terminar de guardar"""
        # Cerrar ventana
        if hasattr(self, 'window_crear') and self.window_crear:
            self.window_crear.destroy()
            
        # Recargar base de datos del tarjetero desde el CSV
        self.tarjetero.load_database()
        
        # Limpiar filtros 
        trace_id = self.search_var.trace_vinfo()[0][1] 
        self.search_var.trace_vdelete("w", trace_id)
        
        self.search_var.set("") 
        self.filter_stars_var.set("Todas las estrellas")
        
        self.search_var.trace("w", self.filter_list)

        # Recargar lista en pantalla
        self.filter_list()







# ==========================
# CLASE VENTANA DE CREACIÓN 
# ==========================
class CreadorTarjetaPage(ctk.CTkFrame):
    def __init__(self, master, on_close_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.tarjetero = Tarjetero()
        self.on_close_callback = on_close_callback # Cerramos página al terminar

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        # Título
        ctk.CTkLabel(self, text="Crear Nueva Tarjeta", font=("Times New Roman", 24, "bold")).grid(row=0, column=0, pady=10)

        # Frame scrolleable para el formulario de tarjeta
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.scroll.grid_columnconfigure(0, weight=1)

        # --- FORMULARIO ---
        # Título de tarjeta
        self.crear_label("Título de la tarjeta:")
        self.entry_title = ctk.CTkEntry(self.scroll, placeholder_text="Ej: Mate en 2")
        self.entry_title.pack(fill="x", pady=(0, 10))

        # FEN (posición inicial)
        self.crear_label("FEN (Posición Inicial):")
        self.entry_fen = ctk.CTkEntry(self.scroll)
        self.entry_fen.pack(fill="x", pady=(0, 10))
        self.entry_fen.insert(0, "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1") # Default

        # Movimientos (solución)
        self.crear_label("Movimientos Solución (UCI separados por espacio):")
        self.crear_label("Ejemplo: e2e4 e7e5 g1f3", size=12, color="#847D71")
        self.entry_moves = ctk.CTkEntry(self.scroll, placeholder_text="e2e4 ...")
        self.entry_moves.pack(fill="x", pady=(0, 10))

        # Rating y Estrellas
        row_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 10))
        
        # Rating
        col1 = ctk.CTkFrame(row_frame, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(col1, text="Elo Estimado:", anchor="w").pack(fill="x")
        self.entry_rating = ctk.CTkEntry(col1, placeholder_text="1500")
        self.entry_rating.pack(fill="x")

        # Estrellas
        col2 = ctk.CTkFrame(row_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(col2, text="Calificación:", anchor="w").pack(fill="x")
        self.option_stars = ctk.CTkOptionMenu(col2, values=["1", "2", "3", "4", "5"])
        self.option_stars.pack(fill="x")
        
        # --- Temas y Usuario ---
        row_2 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row_2.pack(fill="x", pady=(0, 10))

        # Temas
        col4 = ctk.CTkFrame(row_2, fg_color="transparent")
        col4.pack(side="left", fill="x", expand=True, padx=(5,0))
        ctk.CTkLabel(col4, text="Temas (Tags):", anchor="w").pack(fill="x")
        self.entry_themes = ctk.CTkEntry(col4, placeholder_text="None")
        self.entry_themes.pack(fill="x")

        # Usuario
        col3 = ctk.CTkFrame(row_2, fg_color="transparent")
        col3.pack(side="left", fill="x", expand=True, padx=(0,5))
        ctk.CTkLabel(col3, text="Usuario / Creador:", anchor="w").pack(fill="x")
        self.entry_user = ctk.CTkEntry(col3, placeholder_text="Unknown")
        self.entry_user.pack(fill="x")

        # Descripción
        self.crear_label("Descripción:")
        self.txt_desc = ctk.CTkTextbox(self.scroll, height=80)
        self.txt_desc.pack(fill="x", pady=(0, 10))
        
        
        # BOTÓN DE GUARDADO
        self.btn_save = ctk.CTkButton(
            self, 
            text="GUARDAR", 
            fg_color="#B8662E", 
            hover_color="#875E43",
            height=50, 
            font=("Arial", 16, "bold"),
            command=self.guardar
        )
        self.btn_save.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        # Mensaje de estado
        self.lbl_status = ctk.CTkLabel(self, text="", text_color="green")
        self.lbl_status.grid(row=3, column=0, pady=(0, 5))


    def crear_label(self, text, size=12, color=None):
        ctk.CTkLabel(self.scroll, text=text, font=("Times New Roman", 12), anchor="w").pack(fill="x")

    def guardar(self):
        # Generar un ID aleatorio 
        puzzle_id = self.tarjetero.generate_unique_id()
        
        # --- Valores por defecto ---
        user_val = self.entry_user.get().strip()
        if not user_val: user_val = "Unknown"

        themes_val = self.entry_themes.get().strip()
        if not themes_val: themes_val = "None"
        
        rating_val = self.entry_rating.get().strip()
        if not rating_val: rating_val = "1500"
        
        # Recolectar datos ingresados
        data = {
            'PuzzleId': puzzle_id,
            'FEN': self.entry_fen.get().strip(),
            'Moves': self.entry_moves.get().strip(),
            'Rating': rating_val,
            'Title': self.entry_title.get().strip(),
            'Themes': themes_val,
            'Description': self.txt_desc.get("0.0", "end").strip(),
            'Stars': self.option_stars.get(),
            'User': user_val,
            'GameURL': ''  # Siempre en blanco pues no es descargado
        }

        # Validar si están los campos obligatorios
        if not data['Title'] or not data['Moves']:
            self.lbl_status.configure(text="Error: Título y Movimientos son obligatorios", text_color="red")
            return

        # Guardar en archivo
        success = self.tarjetero.guardar_tarjeta(data)

        if success:
            self.lbl_status.configure(text="Tarjeta guardada correctamente!", text_color="green")
            # Ejecutar callback para cerrar ventana y actualizar tarjetero
            if self.on_close_callback:
                self.on_close_callback()
                
        else:
            self.lbl_status.configure(text="Error al escribir en el archivo CSV", text_color="red")