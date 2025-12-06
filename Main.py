import customtkinter as ctk
from paginas.AjedrezCiegoPage import *
from paginas.TarjeteroPage import *
from paginas.CalculadoraEloPage import * 
from paginas.GeneradorDiagramasPage import GeneradorDiagramasPage


class ChessTools(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración inicial de ventana en pantalla completa
        self.title("Chess Tools")
        self.after(0, lambda: self.state('zoomed'))
        
        # Configuración de apariencia 
        ctk.set_appearance_mode("dark") 

        # LAYOUT PRINCIPAL
        self.grid_columnconfigure(0, weight=0)  # Menú lateral
        self.grid_columnconfigure(1, weight=1) # Página
        self.grid_rowconfigure(0, weight=1) 
        
        # Inicialización de componentes
        self._init_sidebar()
        self._init_main_area()
        self._init_views()
        
        # Iniciamos con menú visible
        self.sidebar_visible = True
        self.show_view("elo")



    def _init_sidebar(self):
        """Crea menú lateral"""
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) 

        # Título del menú
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="♟️Menú", font=("Segoe UI Emoji", 20, "bold"))
        self.logo_label.grid(row=0, column=0, pady=(10, 10))

        # Botones de navegación de opciones
        self.btn_elo = self._create_nav_btn("Calculadora de Elo", 1, "elo")
        self.btn_diagramas = self._create_nav_btn("Creador de Diagramas", 2, "diagramas")
        self.btn_tarjetero = self._create_nav_btn("Tarjetero", 3, "tarjetero")
        #self.btn_ciego = self._create_nav_btn("Ajedrez Ciego", 4, "ciego")
                

    def _create_nav_btn(self, text, row, view_name):
        """Helper para crear botones del menú"""
        btn = ctk.CTkButton(
            self.sidebar_frame, 
            text=text, 
            font=("Times New Roman", 16),
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            anchor="w", 
            command=lambda: self.show_view(view_name)
        )
        btn.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        return btn



    def _init_main_area(self):
        """Crea área de contenido: Barra superior y contenedor de páginas"""
        # Contenedor principal 
        self.right_side_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_side_container.grid(row=0, column=1, sticky="nsew")
        
        self.right_side_container.grid_rowconfigure(1, weight=1)
        self.right_side_container.grid_columnconfigure(0, weight=1)

        # --- BARRA SUPERIOR ---
        self.top_bar = ctk.CTkFrame(self.right_side_container, height=40, corner_radius=0)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        
        # Botón Toggle para activar/desactivar menú
        self.btn_toggle = ctk.CTkButton(
            self.top_bar, 
            text="☰", 
            width=40, 
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            font=("Times New Roman", 20),
            command=self.toggle_sidebar
        )
        self.btn_toggle.pack(side="left", padx=10, pady=5)
        
        # Título de sección actual en barra superior
        self.lbl_current_section = ctk.CTkLabel(self.top_bar, text="Inicio", font=("Times New Roman", 16))
        self.lbl_current_section.pack(side="left", padx=10)

        # --- CONTENIDO DE PÁGINA ---
        self.content_area = ctk.CTkFrame(self.right_side_container, fg_color="transparent")
        self.content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        
    
    def _init_views(self):
        """Inicializa páginas posibles"""
        self.views = {
            "elo": CalculadoraEloPage(self.content_area),
            "diagramas": GeneradorDiagramasPage(self.content_area),
            "tarjetero": TarjeteroPage(self.content_area),
            #"ciego": AjedrezCiegoPage(self.content_area)
        }
    
    
    
    # ==========================
    # LÓGICA DE INTERACCIÓN
    # ==========================
    def toggle_sidebar(self):
        """Oculta/muestra menú lateral dependiendo de si está activo"""
        if self.sidebar_visible:
            self.sidebar_frame.grid_forget() # Oculta menú 
            self.sidebar_visible = False
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew") # Muestra menú
            self.sidebar_visible = True

    def show_view(self, view_name):
        """Cambia la página central"""
        # Oculta todas las páginas
        for view in self.views.values():
            view.pack_forget()
        
        # Muestra la página seleccionada
        self.views[view_name].pack(fill="both", expand=True)
        
        # Actualiza título de página
        titles = {"elo": "Calculadora Elo", "diagramas": "Creador de Diagramas", "tarjetero": "Tarjetero", "ciego": "Modo Ciego"}
        self.lbl_current_section.configure(text=titles.get(view_name, ""))
        

if __name__ == "__main__":
    app = ChessTools()
    app.mainloop()