# Super Clipboard & Sysmon GUI

**Super Clipboard & Sysmon** is an open-source, lightweight, and elegant tool designed specifically for Linux environments (**Ubuntu, Mint and derivatives**). It combines aesthetic real-time resource monitoring with a high-productivity clipboard manager and a unique maintenance utility.

---

## ✨ Key Features

### Clipboard Management
*   **Instant Access:** History of copied items with the `Alt + V` global shortcut.
*   **Origin Detection:** Visually identifies which application each text came from (VS Code, Chrome, Terminal, etc.).
*   **Auto-Paste:** When selecting an item, it automatically copies and pastes it into your active window.

### System Monitor
*   **Donut Charts:** Minimalist animated visualization of CPU, RAM, and Disk usage.
*   **Process Panel:** Intelligent list of the most resource-hungry processes, optimized for readability.
*   **Glassmorphism Design:** Modern interface with transparency that integrates seamlessly on Cinnamon and GNOME desktops.

### Clean Mode
*   **Peripheral Lock:** Temporarily disables all keyboards to allow physical cleaning of your hardware without sending accidental commands. Perfect for cat owners! 🐾

---

## 📸 Screenshot preview
<img width="368" height="412" alt="Captura de pantalla de 2026-05-08 11-30-39" src="https://github.com/user-attachments/assets/3593644b-90da-4105-ac3a-f06d926cdc3d" />

<img width="550" height="500" alt="Captura de pantalla de 2026-05-08 11-32-26" src="https://github.com/user-attachments/assets/05abd76b-4c7a-415b-9440-9eb0ca08f83e" />
*Diseño Glassmorphism con integración total en el sistema.*

---

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com
cd super-clipboard-sysmon
```

### 2. System dependencies
Install the required libraries for hardware integration and the GUI:
```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-psutil xdotool xinput
pip install pyperclip pynput
```

### 3. Install as a System App
Use the build script to generate and install the `.deb` package automatically:
```bash
chmod +x build.sh
./build.sh
```

---

## Master Keyboard Shortcuts

| Action | Shortcut |
| :--- | :--- |
| **Open History** | `Alt + V` |
| **Close Window** | `Esc` |
| **Navigate List** | `↑` / `↓` |
| **Paste Selection** | `Enter` or `Left Click` |

---

## Code Architecture
The project is modularized for easy maintenance and contributions:

-   `main.py`: Entry point and **single instance** management via `Gtk.Application`.
-   `app/window.py`: Main monitor interface (charts and processes).
-   `app/clipboard_ui.py`: History interface with dark theme support.
-   `app/clipboard_engine.py`: Event listener and clip management engine.
-   `app/utils.py`: Low-level keyboard locking functions via `xinput`.
-   `app/charts.py`: Donut chart rendering using **Cairo Graphics**.

---

## Troubleshooting
If installation is interrupted and you get a "serious inconsistency" error, run these commands to clean the system:
```bash
sudo rm -f /var/lib/dpkg/info/sysmon-gui.*
sudo dpkg --remove --force-all sysmon-gui
sudo dpkg --configure -a
```

---

## Contributing
Contributions make the Linux community awesome!
1. **Fork** the project.
2. Create your branch: `git checkout -b feature/AwesomeImprovement`.
3. Make your changes and commit: `git commit -m 'Add new metric'`.
4. Push: `git push origin feature/AwesomeImprovement`.
5. Open a **Pull Request**.

## License
Distributed under the **MIT License**. See the `LICENSE` file for more information.

---
Built for the Linux community. **Enjoy a more productive desktop!**
