import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import chess
from logica.Diagrama import Diagrama

class GeneradorDiagramasPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1) # Diagrama 
        self.grid_columnconfigure(1, weight=0) # Creación
        self.grid_rowconfigure(0, weight=1)

        # Fuente
        font_path = os.path.join("paginas/fuentes/Zurich/ZURID___.TTF")
        
        self.renderer = Diagrama(font_path=font_path, square_size=80) # Creamos diagrama
        
        self.preview_size = 500
        self.generated_image = None # Imagen a generar
        self.current_filename = "diagrama" # Nombre por defecto para guardar imagen

        # --- INTERFAZ ---
        self._init_diagrama()  # Panel del tablero
        self._init_creador_diagrama() # Panel de lectura
        
        # Tablero vacío inicial
        self.mostrar_tablero_vacio()


    def _init_diagrama(self):
        """Crea el área del diagrama creado"""
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Título
        self.lbl_title = ctk.CTkLabel(self.left_frame, text="Vista de Diagrama", font=("Times New Roman", 24, "bold"))
        self.lbl_title.pack(pady=(0, 20))

        # Diagrama
        self.board_display = ctk.CTkLabel(self.left_frame, text="")
        self.board_display.pack(expand=True)


    def _init_creador_diagrama(self):
        """Crea el area de lectura de diagramas"""
        self.right_frame = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        
        self.right_frame.pack_propagate(False) 
        
        ctk.CTkLabel(self.right_frame, text="Creador de diagramas", font=("Times New Roman", 24, "bold")).pack(pady=20, padx=20)

        # Botón Cargar archivo
        self.btn_load = ctk.CTkButton(
            self.right_frame, 
            text="Cargar Archivo (.txt)", 
            height=50,
            font=("Times New Roman", 16),
            fg_color="#B8662E",
            hover_color="#875E43",
            command=self.cargar_archivo
        )
        self.btn_load.pack(pady=(20, 2), padx=20, fill="x")

        # Info
        self.lbl_info = ctk.CTkLabel(
            self.right_frame, 
            text="El archivo debe contener\nuna cadena FEN válida o texto\nvisual con fuente de ajedrez.", 
            text_color="#F0E3CE",
            font=("Times New Roman", 14),
            wraplength=280
        )
        self.lbl_info.pack(pady=(0, 10))

        # Cuadro de texto para ver/editar el contenido manualmente
        ctk.CTkLabel(self.right_frame, text="O escribe/edita el contenido aquí:", anchor="w", font=("Times New Roman", 16)).pack(pady=(20,5), padx=20, fill="x")
        self.txt_fen = ctk.CTkTextbox(self.right_frame, height=200,  wrap="word", font=("Times New Roman", 14))
        self.txt_fen.pack(pady=(0, 20), padx=20, fill="x")
        
        # Botón actualizar manual
        self.btn_refresh = ctk.CTkButton(
            self.right_frame,
            text="Generar desde Texto",
            fg_color="#847D71",
            hover_color="#56534D",
            font=("Times New Roman", 16),
            command=self.generar_desde_texto
        )
        self.btn_refresh.pack(pady=5, padx=20, fill="x")

        # Botón guardar imagen
        self.btn_save = ctk.CTkButton(
            self.right_frame, 
            text="Guardar como Imagen", 
            height=50,
            hover_color="#294A29",
            font=("Times New Roman", 16, "bold"),
            state="disabled",
            command=self.guardar_imagen
        )
        self.btn_save.pack(pady=40, padx=20, fill="x", side="bottom")



    # ==========================================
    # LÓGICA DE PROCESAMIENTO TXT
    # ==========================================
    def procesar_entrada(self, texto_entrada):
        """
        Intenta detectar el texto de entrada es un FEN estándar o un diagrama de texto
        """
        texto_entrada = texto_entrada.strip()
        
        # Si es FEN válido
        if len(texto_entrada.split()) == 6:
            try:
                chess.Board(texto_entrada) # Validar lógica de ajedrez
                # Si no da error, es un FEN válido
                self._generar_desde_fen(texto_entrada)
                return
            except ValueError:
                pass # FEN no válido
            
        # Si es texto por fuente TrueType
        try:
            self._generar_desde_raw(texto_entrada)
        except ValueError as e:
            # Si falla (ej: no tiene 64 caracteres), mostramos error
            self.lbl_info.configure(text="Error: Formato no reconocido.", text_color="red")
            messagebox.showwarning("Formato Desconocido", "El texto no parece un FEN válido ni un diagrama de fuente conocido.")
            
            
    def _generar_desde_fen(self, fen):
        """Usa el motor de ajedrez para interpretar"""
        try:
            self.generated_image = self.renderer.generate_FEM_diagram(fen)
            self._mostrar_imagen()
            self.lbl_info.configure(text="Formato detectado: FEN Estándar", text_color="#F0A327")
            
        except Exception as e:
            print(f"Error FEN: {e}")
            self.lbl_info.configure(text="Error al procesar FEN", text_color="red")


    def _generar_desde_raw(self, raw_text):
        """Usa el motor directo de caracteres (generate_raw)"""
        self.generated_image = self.renderer.generate_raw_diagram(raw_text)
        self._mostrar_imagen()
        self.lbl_info.configure(text="Formato detectado: Matriz TrueType", text_color="#F0A327")

    
    def _mostrar_imagen(self):
        """Actualiza la vista en la interfaz"""
        if self.generated_image is not None:
            preview_img = ctk.CTkImage(
                light_image=self.generated_image, 
                dark_image=self.generated_image, 
                size=(self.preview_size, self.preview_size)
            )
            self.board_display.configure(image=preview_img)
        self.btn_save.configure(state="normal", fg_color="green")




    # ==========================================
    # LÓGICA VISUAL
    # ==========================================
    def mostrar_tablero_vacio(self):
        """Muestra un tablero vacío al iniciar"""
        # Usamos FEN vacío para iniciar
        self._generar_desde_fen("8/8/8/8/8/8/8/8 w - - 0 1")
        self.btn_save.configure(state="disabled", fg_color="#847D71")
        self.lbl_info.configure(text="Elige un archivo con una cadena FEN válida o texto visual con fuente de ajedrez.", text_color="#F0E3CE")
        
        
    def cargar_archivo(self):
        """Abre explorador de archivos y lee el txt seleccionado"""
        
        # Usamos carpeta por defecto de diagramas
        # os.getcwd() obtiene la carpeta donde está tu main.py
        carpeta_defecto = os.path.join("resources/diagramas")
        # Si carpeta no existe, la creamos
        if not os.path.exists(carpeta_defecto):
            try:
                os.makedirs(carpeta_defecto)
            except OSError:
                carpeta_defecto = os.getcwd() # Si falla, usamos raíz
        
        # Abrimos explorador
        file_path = filedialog.askopenfilename(
            initialdir=carpeta_defecto,
            title="Seleccionar archivo de ajedrez",
            filetypes=[("Archivos de Texto (.txt)", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if not file_path: return

        # --- Copiar nombre de txt para usarlo para la imagen---
        nombre_base = os.path.basename(file_path) 
        nombre_sin_ext = os.path.splitext(nombre_base)[0] # Quitamis el ",txt" del nombre
        self.current_filename = nombre_sin_ext
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

                # Insertamos el texto en caja
                self.txt_fen.delete("0.0", "end")
                self.txt_fen.insert("0.0", content)
                # Generamos diagrama
                self.procesar_entrada(content)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")


    def generar_desde_texto(self):
        """Lee entrada del usuario en la caja de texto"""
        content = self.txt_fen.get("0.0", "end").strip()
        self.procesar_entrada(content)


    def guardar_imagen(self):
        """Exporta imagen generada a PNG/JPG"""
        if not self.generated_image: return

        # Sugerimos carpeta por defecto para imágenes generadas
        carpeta_guardado = os.path.join(os.getcwd(), "resources/diagramas/imagenes exportadas")
        # Si carpeta no existe, la creamos
        if not os.path.exists(carpeta_guardado):
            try: os.makedirs(carpeta_guardado)
            except: pass
            
        file_path = filedialog.asksaveasfilename(
            initialdir=carpeta_guardado,
            initialfile=self.current_filename,
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png"), ("Imagen JPG", "*.jpg")],
            title="Guardar Diagrama"
        )

        if file_path:
            try:
                self.generated_image.save(file_path)
                messagebox.showinfo(f"Imagen guardada en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen:\n{e}")