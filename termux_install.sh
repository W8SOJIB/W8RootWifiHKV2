#!/bin/bash

# W8Team WiFi Hacker - Termux Installation Script
# Author: W8Team/W8SOJIB
# Telegram: https://t.me/W8SOJIB
# Version: 2.0

clear
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              🛡️  W8Team WiFi Hacker Installer                 ║"
echo "║                    Advanced Auto System v2.0                  ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  Author: W8Team/W8SOJIB                                       ║"
echo "║  Telegram: https://t.me/W8SOJIB                               ║"
echo "║  Platform: Android Termux                                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if running in Termux
echo -e "${BLUE}[*]${NC} Checking Termux environment..."
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${RED}❌ ERROR: This script is designed for Termux only!${NC}"
    echo -e "${YELLOW}[!]${NC} Please install Termux from F-Droid and run this script inside Termux."
    exit 1
fi
echo -e "${GREEN}✅ Termux environment detected${NC}"

# Check Android version
echo -e "${BLUE}[*]${NC} Checking Android version..."
ANDROID_VERSION=$(getprop ro.build.version.release)
echo -e "${GREEN}✅ Android version: $ANDROID_VERSION${NC}"

# Check architecture
echo -e "${BLUE}[*]${NC} Checking device architecture..."
ARCH=$(uname -m)
echo -e "${GREEN}✅ Architecture: $ARCH${NC}"

echo ""
echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    INSTALLATION STARTING                     ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Update Termux packages
echo -e "${CYAN}[1/8]${NC} 📱 Updating Termux packages..."
if pkg update -y && pkg upgrade -y; then
    echo -e "${GREEN}✅ Termux packages updated successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Some packages may have failed to update (continuing...)${NC}"
fi

# Install core packages
echo -e "${CYAN}[2/8]${NC} 📦 Installing core packages..."
if pkg install -y python python-pip git iw root-repo; then
    echo -e "${GREEN}✅ Core packages installed${NC}"
else
    echo -e "${RED}❌ Failed to install core packages${NC}"
    exit 1
fi

# Install privilege escalation tools
echo -e "${CYAN}[3/8]${NC} 🔐 Installing privilege escalation tools..."
if pkg install -y tsu; then
    echo -e "${GREEN}✅ Root tools installed${NC}"
else
    echo -e "${YELLOW}⚠️  Some root tools failed to install${NC}"
fi

# Install WiFi hacking tools
echo -e "${CYAN}[4/8]${NC} 📡 Installing WiFi security tools..."
pkg install -y pixiewps wpa-supplicant hashcat aircrack-ng || echo -e "${YELLOW}⚠️  Some WiFi tools may not be available on this architecture${NC}"
echo -e "${GREEN}✅ WiFi tools installation completed${NC}"

# Install Python dependencies
echo -e "${CYAN}[5/8]${NC} 🐍 Installing Python dependencies..."
if pip install --upgrade pip; then
    echo -e "${GREEN}✅ Pip upgraded${NC}"
fi

if pip install pyfiglet psutil requests; then
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install Python dependencies${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${CYAN}[6/8]${NC} 📁 Creating project directories..."
mkdir -p ~/.OneShot/sessions
mkdir -p ~/.OneShot/pixiewps
mkdir -p reports
echo -e "${GREEN}✅ Directories created${NC}"

# Set permissions
echo -e "${CYAN}[7/8]${NC} 🔧 Setting up permissions..."
chmod +x oneshot.py 2>/dev/null || echo "Main script not found (will be available after git clone)"
echo -e "${GREEN}✅ Permissions configured${NC}"

# Final setup
echo -e "${CYAN}[8/8]${NC} ✨ Finalizing installation..."
echo -e "${GREEN}✅ Installation completed successfully!${NC}"

echo ""
echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    INSTALLATION COMPLETE                     ║${NC}"
echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}🎉 W8Team WiFi Hacker has been installed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 NEXT STEPS:${NC}"
echo -e "${YELLOW}1.${NC} Grant root permissions: ${CYAN}tsu${NC}"
echo -e "${YELLOW}2.${NC} Run the tool: ${CYAN}python oneshot.py${NC}"
echo -e "${YELLOW}3.${NC} Select menu option for automatic hacking"
echo -e "${YELLOW}4.${NC} Enjoy! 🚀"
echo ""

echo -e "${BLUE}⚡ QUICK START:${NC}"
echo -e "${CYAN}tsu && python oneshot.py${NC}"
echo ""

echo -e "${BLUE}🔧 REQUIREMENTS:${NC}"
echo -e "${YELLOW}•${NC} Root access (use 'tsu' command)"
echo -e "${YELLOW}•${NC} WiFi enabled on device"
echo -e "${YELLOW}•${NC} Location services enabled"
echo -e "${YELLOW}•${NC} Target WiFi networks nearby"
echo ""

echo -e "${BLUE}📱 SUPPORT & UPDATES:${NC}"
echo -e "${YELLOW}•${NC} Telegram Channel: ${CYAN}https://t.me/W8SOJIB${NC}"
echo -e "${YELLOW}•${NC} Get latest updates and support"
echo -e "${YELLOW}•${NC} Report bugs and request features"
echo ""

echo -e "${BLUE}⚖️  LEGAL REMINDER:${NC}"
echo -e "${RED}⚠️  Only use on networks you own or have permission to test${NC}"
echo -e "${RED}⚠️  Unauthorized WiFi hacking is illegal${NC}"
echo -e "${RED}⚠️  Educational and authorized testing only${NC}"
echo ""

echo -e "${GREEN}🛡️  Happy Ethical Hacking! 🛡️${NC}"
echo -e "${CYAN}Made with ❤️  by W8Team/W8SOJIB${NC}"
echo ""

# Offer to open Telegram
read -p "🔗 Open Telegram channel now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[*]${NC} Opening Telegram channel..."
    am start -a android.intent.action.VIEW -d "https://t.me/W8SOJIB" 2>/dev/null || \
    termux-open-url "https://t.me/W8SOJIB" 2>/dev/null || \
    echo -e "${YELLOW}[*]${NC} Please open: https://t.me/W8SOJIB"
fi

echo -e "${GREEN}Installation script completed! 🎉${NC}"
