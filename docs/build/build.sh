#!/bin/bash

BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}Creating Debian control files...${NC}"

cat > plugin/DEBIAN/prerm << 'EOF'
#!/bin/bash
PID=$(ps aux | grep "/usr/lib/sysmon-gui/main.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "Closing Sysmon GUI process (PID: $PID)..."
    kill -9 $PID
fi
exit 0
EOF

cat > plugin/DEBIAN/postrm << 'EOF'
#!/bin/bash
update-desktop-database /usr/share/applications 2>/dev/null || true
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
touch /usr/share/applications
touch ~/.local/share/applications
echo "[sysmon] Cleanup complete and menu refreshed."
exit 0
EOF

cat > plugin/DEBIAN/postinst << 'EOF'
#!/bin/bash
chmod +x /usr/bin/sysmon-gui
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database /usr/share/applications 2>/dev/null || true
touch /usr/share/applications
echo "[sysmon] Installed successfully."
exit 0
EOF

chmod 755 plugin plugin/DEBIAN
chmod 755 plugin/DEBIAN/prerm
chmod 755 plugin/DEBIAN/postrm
chmod 755 plugin/DEBIAN/postinst

echo -e "${BLUE}Syncing files and building...${NC}"

# Copy the entire app/ tree preserving structure
cp -r app plugin/usr/lib/sysmon-gui/app
cp main.py plugin/usr/lib/sysmon-gui/

# Clean pycache
find plugin/usr/lib/sysmon-gui -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

dpkg-deb --build plugin sysmon-gui_1.0.1_all.deb

echo -e "${BLUE}Installing...${NC}"
sudo dpkg --configure -a
sudo dpkg -i sysmon-gui_1.0.1_all.deb
sudo apt-get install -f -y

echo -e "${GREEN}Process complete.${NC}"
