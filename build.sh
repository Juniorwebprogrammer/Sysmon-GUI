#!/bin/bash

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}Creating Debian control files...${NC}"

# 1. Create PRE-UNINSTALL SCRIPT
cat > plugin/DEBIAN/prerm << 'EOF'
#!/bin/bash
# Find the Python process running your APP, not the installer.
# Filter by the installation path which is unique.
PID=$(ps aux | grep "/usr/lib/sysmon-gui/main.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$PID" ]; then
    echo "Closing Sysmon GUI process (PID: $PID)..."
    kill -9 $PID
fi
exit 0
EOF

# 2. Create POST-UNINSTALL SCRIPT
cat > plugin/DEBIAN/postrm << 'EOF'
#!/bin/bash
# Refresh application databases
update-desktop-database /usr/share/applications 2>/dev/null || true
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true

# Notify system of file changes
touch /usr/share/applications
touch ~/.local/share/applications

echo "[sysmon] Cleanup complete and menu refreshed."
exit 0
EOF

# 3. POST-INSTALLATION SCRIPT
cat > plugin/DEBIAN/postinst << 'EOF'
#!/bin/bash
chmod +x /usr/bin/sysmon-gui
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database /usr/share/applications 2>/dev/null || true
# Force refresh on install too
touch /usr/share/applications
echo "[sysmon] Installed successfully."
exit 0
EOF

# 4. Set permissions (VITAL)
chmod 755 plugin/DEBIAN/prerm
chmod 755 plugin/DEBIAN/postrm
chmod 755 plugin/DEBIAN/postinst

# 5. Sync files
echo -e "${BLUE}Syncing files and building...${NC}"
mkdir -p plugin/usr/lib/sysmon-gui/app
cp app/*.py plugin/usr/lib/sysmon-gui/app/
cp main.py plugin/usr/lib/sysmon-gui/

# 6. Build
dpkg-deb --build plugin sysmon-gui_1.0.0_all.deb

# 7. Install
echo -e "${BLUE}Installing...${NC}"
sudo dpkg --configure -a
sudo dpkg -i sysmon-gui_1.0.0_all.deb
sudo apt-get install -f -y

echo -e "${GREEN}Process complete.${NC}"
