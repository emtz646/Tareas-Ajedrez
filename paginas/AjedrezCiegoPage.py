import customtkinter as ctk

# ======================================================
# PÁGINA PARA AJEDREZ A LA CIEGA
# ======================================================

class AjedrezCiegoPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Título
        self.title = ctk.CTkLabel(self, text="Ajedrez a la Ciega", font=("Times New Roman", 24, "bold"))
        self.title.pack(pady=20, padx=20)
        
        # Contenido
        self.status = ctk.CTkLabel(self, text="Esperando inicio...", text_color="gray")
        self.status.pack()
        
        ctk.CTkButton(self, text="Escuchar Movimiento (TTS)").pack(pady=20)