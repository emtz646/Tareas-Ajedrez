import customtkinter as ctk
import customtkinter as ctk

# ======================================================
# PÁGINA CALCULADORA DE ELO
# ======================================================
class CalculadoraEloPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Título
        self.grid_rowconfigure(1, weight=0) # Formulario
        self.grid_rowconfigure(2, weight=0) # Botón
        self.grid_rowconfigure(3, weight=1) # Resultado = Elo

        # Variables
        self.elo_propio_var = ctk.StringVar()
        self.elo_rival_var = ctk.StringVar()
        self.k_factor_var = ctk.StringVar(value="20")
        self.resultado_var = ctk.StringVar(value="Victoria (1.0)")

        # Validar entradas cada que se escribe en los campos
        self.elo_propio_var.trace("w", self.validar_boton)
        self.elo_rival_var.trace("w", self.validar_boton)

        self._init_calculadora()


    def _init_calculadora(self):
        # Título
        ctk.CTkLabel(
            self, 
            text="Calculadora de Elo FIDE", 
            font=("Times New Roman", 32, "bold")
        ).grid(row=0, column=0, pady=(40, 30))

        # --- Formulario ---
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=1, column=0)

        # Elo actual
        ctk.CTkLabel(form_frame, text="Tu Elo actual:", font=("Times New Roman", 16)).grid(row=0, column=0, padx=20, pady=15, sticky="e")
        self.entry_elo = ctk.CTkEntry(
            form_frame, 
            textvariable=self.elo_propio_var, 
            width=200
        )
        self.entry_elo.grid(row=0, column=1, padx=20, pady=15)

        # Elo oponente
        ctk.CTkLabel(form_frame, text="Elo del Oponente:", font=("Times New Roman", 16)).grid(row=1, column=0, padx=20, pady=15, sticky="e")
        self.entry_rival = ctk.CTkEntry(
            form_frame, 
            textvariable=self.elo_rival_var, 
            width=200
        )
        self.entry_rival.grid(row=1, column=1, padx=20, pady=15)

        # vFactor K
        # K=10 (Top), K=20 (Estándar), K=40 (Nuevos)
        ctk.CTkLabel(form_frame, text="Factor K (Desarrollo):", font=("Times New Roman", 16)).grid(row=2, column=0, padx=20, pady=15, sticky="e")
        self.combo_k = ctk.CTkOptionMenu(
            form_frame, 
            variable=self.k_factor_var, 
            values=["10", "20", "40"],
            width=200,
            fg_color="#B8662E", 
            button_color="#894B22",
            button_hover_color="#875E43",
        )
        self.combo_k.grid(row=2, column=1, padx=20, pady=15)

        # Resultado de partida
        ctk.CTkLabel(form_frame, text="Resultado de la partida:", font=("Times New Roman", 16)).grid(row=3, column=0, padx=20, pady=15, sticky="e")
        self.combo_res = ctk.CTkOptionMenu(
            form_frame, 
            variable=self.resultado_var, 
            values=["Victoria (1.0)", "Tablas (0.5)", "Derrota (0.0)"],
            width=200,
            fg_color="#B8662E", 
            button_color="#894B22",
            button_hover_color="#875E43",
        )
        self.combo_res.grid(row=3, column=1, padx=20, pady=15)

        # --- Botón Calcular ---
        self.btn_calcular = ctk.CTkButton(
            self, 
            text="Calcular variación", 
            fg_color="gray",
            state="disabled",
            height=50,
            width=250,
            font=("Times New Roman", 16, "bold"),
            command=self.calcular_elo
        )
        self.btn_calcular.grid(row=2, column=0, pady=40)

        # --- Resultados ---
        self.lbl_resultado = ctk.CTkLabel(
            self, 
            text="", 
            font=("Times New Roman", 20),
            justify="center"
        )
        self.lbl_resultado.grid(row=3, column=0, sticky="n")


    def validar_boton(self, *args):
        """Activa el botón solo si se han ingresado números en los campos"""
        elo1 = self.elo_propio_var.get()
        elo2 = self.elo_rival_var.get()
        
        # Verificar que se hayan ingresado números
        if elo1.isdigit() and elo2.isdigit():
            self.btn_calcular.configure(state="normal", fg_color="green", hover_color="#2D582D")
        else:
            self.btn_calcular.configure(state="disabled", fg_color="gray")


    def calcular_elo(self):
        try:
            # Obtener datos
            Ra = float(self.elo_propio_var.get()) # Rating A (Propio)
            Rb = float(self.elo_rival_var.get())  # Rating B (Rival)
            K = float(self.k_factor_var.get())    # Factor K
            
            res_txt = self.resultado_var.get()
            if "1.0" in res_txt: Sa = 1.0
            elif "0.5" in res_txt: Sa = 0.5
            else: Sa = 0.0

            # Calcular probabilidad esperada
            Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))

            # Calcular nuevo Elo
            variacion = K * (Sa - Ea)
            nuevo_elo = Ra + variacion

            # Mostrar nuevo Elo
            signo = "+" if variacion > 0 else ""
            color_res = "#2ECC71" if variacion >= 0 else "#E74C3C" # Verde o Rojo
            
            texto_final = (
                f"Probabilidad de victoria esperada: {Ea:.1%}\n\n"
                f"Variación:  {signo}{variacion:.1f}\n"
                f"NUEVO ELO:  {nuevo_elo:.1f}"
            )
            
            self.lbl_resultado.configure(text=texto_final, text_color=color_res)

        except ValueError:
            self.lbl_resultado.configure(text="Error en los datos ingresados", text_color="red")