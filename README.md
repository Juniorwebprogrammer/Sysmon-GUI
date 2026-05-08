# 🚀 Super Clipboard & Sysmon GUI

**Super Clipboard & Sysmon** es una herramienta de código abierto, ligera y elegante diseñada específicamente para entornos Linux (**Ubuntu, Mint y derivados**). Combina la monitorización estética de recursos en tiempo real con un gestor de portapapeles de alta productividad y una utilidad de mantenimiento única.

---

## ✨ Características Destacadas

### 📋 Gestión de Portapapeles
*   **Acceso Instantáneo:** Historial de elementos copiados con el atajo global `Alt + V`.
*   **Detección de Origen:** Identifica visualmente de qué aplicación viene cada texto (VS Code, Chrome, Terminal, etc.).
*   **Auto-Pegado:** Al seleccionar un elemento, se copia y pega automáticamente en tu ventana activa.

### 📊 Monitor de Sistema
*   **Gráficos Donut:** Visualización minimalista y animada de CPU, RAM y uso de Disco.
*   **Panel de Procesos:** Lista inteligente de los procesos con mayor consumo, optimizada para la legibilidad.
*   **Diseño Glassmorphism:** Interfaz moderna con transparencias que se integra perfectamente en escritorios Cinnamon y GNOME.

### 🧹 Modo Limpieza (Clean Mode)
*   **Bloqueo de Periféricos:** Desactiva temporalmente todos los teclados para permitir la limpieza física de tu hardware sin enviar comandos accidentales. ¡Ideal para dueños de gatos! 🐾

---

## 📸 Vista Previa
<img width="368" height="412" alt="Captura de pantalla de 2026-05-08 11-30-39" src="https://github.com/user-attachments/assets/3593644b-90da-4105-ac3a-f06d926cdc3d" />

<img width="550" height="500" alt="Captura de pantalla de 2026-05-08 11-32-26" src="https://github.com/user-attachments/assets/05abd76b-4c7a-415b-9440-9eb0ca08f83e" />
*Diseño Glassmorphism con integración total en el sistema.*

---

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com
cd super-clipboard-sysmon
```

### 2. Dependencias del sistema
Instala las librerías necesarias para la integración de hardware y la interfaz:
```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-psutil xdotool xinput
pip install pyperclip pynput
```

### 3. Instalación como App de Sistema
Utiliza el script de construcción para generar e instalar el paquete `.deb` automáticamente:
```bash
chmod +x build.sh
./build.sh
```

---

## ⌨️ Atajos de Teclado Maestros


| Acción | Atajo |
| :--- | :--- |
| **Abrir Historial** | `Alt + V` |
| **Cerrar Ventana** | `Esc` |
| **Navegar Lista** | `↑` / `↓` |
| **Pegar Selección** | `Enter` o `Click Izquierdo` |

---

## 📂 Arquitectura del Código
El proyecto está modularizado para facilitar el mantenimiento y las contribuciones:

-   `main.py`: Punto de entrada y gestión de **instancia única** mediante `Gtk.Application`.
-   `app/window.py`: Interfaz principal del monitor (gráficos y procesos).
-   `app/clipboard_ui.py`: Interfaz del historial con soporte para temas oscuros.
-   `app/clipboard_engine.py`: Motor de escucha de eventos y gestión de clips.
-   `app/utils.py`: Funciones de bajo nivel para el bloqueo de teclados mediante `xinput`.
-   `app/charts.py`: Renderizado de gráficos donuts mediante **Cairo Graphics**.

---

## ⚠️ Solución de Problemas
Si la instalación se interrumpe y obtienes un error de "estado grave de inconsistencia", ejecuta estos comandos para limpiar el sistema:
```bash
sudo rm -f /var/lib/dpkg/info/sysmon-gui.*
sudo dpkg --remove --force-all sysmon-gui
sudo dpkg --configure -a
```

---

## 🤝 Contribuciones
¡Las contribuciones hacen que la comunidad de Linux sea increíble! 
1. Haz un **Fork** del proyecto.
2. Crea tu rama: `git checkout -b feature/MejoraIncreible`.
3. Haz tus cambios y un commit: `git commit -m 'Añadida nueva métrica'`.
4. Haz push: `git push origin feature/MejoraIncreible`.
5. Abre un **Pull Request**.

## 📄 Licencia
Distribuido bajo la **Licencia MIT**. Consulta el archivo `LICENSE` para más información.

---
Desarrollado para la comunidad Linux. **¡Disfruta de un escritorio más productivo!**
