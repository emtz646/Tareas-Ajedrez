# ♟️ Chess Suite

**Chess Suite** es una app para escritorio de entrenamiento en ajedrez, con herramientas para el cálculo de Elo, tarjetero para guardar jugadas interesantes, poderlas estudiar y resolver, así como generación de diagramas como imagen para cualquier uso.

## Autor
**Nombre:** Martínez Mejía Eduardo
**Número de cuenta:** 320326727

## Ejecucuón

1.  **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Iniciar la aplicación:**

    ```bash
    python main.py
    ```

-----

## Estructura de Carpetas

```text
/CarpetadelProyecto
│
├── main.py                <-- Archivo de ejecución
├── requirements.txt       <-- Lista de dependencias Python
│
├── resources/             <-- Recursos gráficos y datos
│   └── diagramas/      
|       └── imagenes exportadas/
│   └── tarjetas/      
|       └── tarjetero.csv
│
├── paginas/
│   ├── AjedrezCiegoPage.py
│   ├── CalculadoraEloPage.py
│   ├── GeneradorDiagramasPage.py
│   ├── paginas/TarjeteroPage.py
│   └── fuentes/
│       └── Zurich/
│           └── ZURID___.TTF  <-- Fuente TrueType usada
│
└── logica/
    ├── AjedrezCiego.py
    ├── Diagrama.py
    ├── EjercicioTarjeta.py
    ├── Tarjetero.py
```