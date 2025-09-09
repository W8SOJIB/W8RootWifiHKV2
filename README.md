# 🛡️ W8Team WiFi Hacker - Advanced Auto System

<div align="center">

![Version](https://img.shields.io/badge/Version-2.0-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-blue)
![License](https://img.shields.io/badge/License-Educational-red)
![Python](https://img.shields.io/badge/Python-3.6%2B-yellow)

**🚀 Professional WiFi Penetration Testing Tool**  
*Automated WPS Attack System with AI-Powered PIN Prediction*

[📱 Telegram](https://t.me/W8SOJIB) • [📋 Features](#-features) • [🔧 Installation](#-installation) • [📖 Usage](#-usage)

</div>

---

## 🌟 **Overview**

W8Team WiFi Hacker is an advanced, automated WiFi penetration testing tool designed for security professionals and ethical hackers. Built specifically for Termux (Android) and Linux environments, it combines multiple attack vectors with AI-powered PIN prediction for maximum effectiveness.

### ⚡ **Key Highlights**
- 🎯 **Fully Automated** - Zero configuration needed
- 🤖 **AI-Powered** - Smart PIN prediction algorithms  
- 📱 **Termux Optimized** - Perfect for mobile penetration testing
- 🎨 **Professional Interface** - Beautiful menu system with live statistics
- 💾 **Auto-Save Results** - All successful attacks automatically saved
- 🔍 **Multi-Attack Methods** - Pixie Dust, Brute Force, AI Prediction

## 🚀 **Features**

### 🎯 **Attack Methods**
- **🧚 Pixie Dust Attack** - Fast cryptographic attack for vulnerable routers
- **🔥 Smart Brute Force** - Intelligent PIN guessing with statistical optimization
- **🤖 AI PIN Prediction** - Machine learning-based PIN generation
- **📡 Manual Target Selection** - Scan, select, and attack specific networks

### 🤖 **Automation Features**
- **Auto Vulnerability Detection** - Automatically identifies high-risk networks
- **Smart Target Prioritization** - Focuses on most vulnerable targets first
- **Hands-free Operation** - Complete automation from scan to password extraction
- **Auto Password Saving** - Saves all successful attacks to multiple formats

### 🎨 **Interface & Experience**
- **Beautiful Menu System** - Professional ASCII interface with live statistics
- **Real-time Progress** - Live attack progress and success rate tracking
- **Color-coded Networks** - Visual vulnerability indicators (Green/Red/Yellow)
- **Multi-format Reports** - TXT, CSV, and structured attack history

### 📱 **Termux Optimization**
- **Auto Interface Detection** - No manual wlan0 configuration needed
- **Android Integration** - Seamless Termux environment support
- **Mobile-friendly Interface** - Optimized for small screens
- **One-command Installation** - Simple setup script included

### 🚀 **What Makes This Special?**

Unlike traditional WiFi tools that require extensive manual configuration, W8Team WiFi Hacker provides a **"one-click"** solution:

1. **🔍 Universal Coverage** - Attacks EVERY WPS network found (not just vulnerable ones)
2. **⏱️ Smart Timeout System** - 30-second limit per network for maximum efficiency
3. **🎯 Signal Optimization** - Automatically targets strongest signals first
4. **🧠 Revolutionary AI System** - 8 intelligent strategies instead of blind brute force
5. **⚡ Lightning Fast Results** - Finds PINs in 1,000-50,000 attempts (vs 100M traditional)
6. **💎 Instant Results** - Passwords automatically extracted and saved
7. **📊 Live Progress Tracking** - Real-time statistics and success rates
8. **🎉 Comprehensive Reports** - Detailed final summaries and attack logs
9. **💚 Completely Free** - No hidden costs or premium features

---

## 🔧 **Installation**

### 📱 **Termux (Android) - Recommended**

#### **🚀 Quick Install (1-Minute Setup)**
```bash
# Copy and paste this entire block:
pkg update && pkg upgrade -y && pkg install -y root-repo && pkg install -y git tsu python wpa-supplicant pixiewps iw openssl python-pip aircrack-ng hashcat && pip install pyfiglet psutil requests && git clone https://github.com/W8SOJIB/W8RootWifiHKV2 && cd W8RootWifiHKV2 && echo "🎉 Ready to hack! Run: tsu && sudo python oneshot.py"
```

#### **📋 Step-by-Step Installation**

# Update Termux

```
pkg update && pkg upgrade -y
```

# Install root repository (for advanced tools)


```
pkg install -y root-repo
```
```

# Install Git
```

```
pkg install -y git
```

# Install TSU (root access)

```
pkg install -y tsu
```


# Install Python

```
pkg install -y python
```

# Install Python package manager
```
pkg install -y python-pip
```

# Install WPA Supplicant

```
pkg install -y wpa-supplicant
```
# Install Pixiewps
```

pkg install -y pixiewps
```

# Install IW (WiFi tools)

```
pkg install -y iw
```
# Install OpenSSL


```
pkg install -y openssl
```

# Install Python dependencies
```
pip install pyfiglet psutil requests
```
# Clone repository
```
git clone https://github.com/W8SOJIB/W8RootWifiHKV2
cd W8RootWifiHKV2
```
# Optional: Run auto-installer for additional setup
```
bash termux_install.sh
```
# Start the tool
```
tsu
```
```
sudo python oneshot.py
```

### 🐧 **Linux**

```bash
# Clone repository
git clone https://github.com/W8SOJIB/W8RootWifiHKV2
cd W8RootWifiHKV2

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip iw wpasupplicant pixiewps
pip3 install -r requirements.txt

# Run the tool
sudo python3 oneshot.py
```

---

## 📖 **Usage**

### 🎮 **Interactive Menu Mode** (Recommended)

Simply run the tool without any arguments to access the beautiful menu interface:

```bash
python oneshot.py
```

The tool will display a beautiful menu interface with Smart AI capabilities:

```
╔═══════════════════ LIVE STATISTICS ═══════════════════╗
║ TIME: 2024-12-19 15:30:45                            ║
║ AUTHOR: W8Team/W8SOJIB                               ║
║ TELEGRAM: https://t.me/W8SOJIB                       ║
╚═══════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║                  🛡️  W8Team WiFi Hacker                     ║
║                    Advanced Auto System                      ║
║                     💚 This Tool Free 💚                     ║
╠══════════════════════════════════════════════════════════════╣
║  [1] 🚀 Auto Attack - Find High Vulnerability & Auto Hack    ║
║  [2] 📡 Scan & Attack WiFi - Select Target & Pixie Dust     ║
║  [3] 🔥 BruteForce Attack - Scan, Select & PIN Attack       ║
║  [4] 🤖 AI PIN Prediction - ALL 100 Million PINs Attack    ║
║  [5] 📋 View All Saved Passwords                            ║
║  [6] 📱 Tool Author - Open Telegram                         ║
║  [7] 🚪 Exit                                                ║
╚══════════════════════════════════════════════════════════════╝
```

### **🎯 Attack Modes**

#### **1. 🚀 Enhanced Auto Attack Mode** *(Recommended for Everyone)*
- **🎯 Attacks EVERY WPS network found** (not just vulnerable ones)
- **⏱️ Smart 30-second timeout** per network for efficiency
- **📶 Signal strength optimization** (attacks strongest signals first)
- **📊 Real-time progress tracking** with live statistics
- **💾 Auto-saves all successful passwords** to multiple file formats
- **🔄 Comprehensive coverage** - tries every network systematically
- **🎉 Detailed final summary** with success rates and statistics
- **Zero manual configuration required!**

#### **2. 📡 Manual Target Selection**
- Shows color-coded network list:
  - 🟢 **Green** = High vulnerability (recommended targets)
  - 🔴 **Red** = WPS locked (harder targets)
  - 🟡 **Yellow** = Already cracked
- Select specific target for Pixie Dust attack
- Fast and effective for vulnerable routers

#### **3. 🔥 BruteForce Attack**
- Intelligent PIN brute force with progress tracking
- Statistical optimization for faster results
- Real-time ETA and success rate display

#### **4. 🤖 AI PIN Prediction - Smart Intelligence Attack**
- **🧠 Multi-Phase Intelligence System** - AI predictions + smart pattern analysis
- **🎯 8 Smart Attack Strategies** - Common PINs, manufacturer defaults, date patterns, sequences
- **⚡ High-Speed Results** - Finds PINs in 1,000-50,000 attempts (vs 100M brute force)
- **🔮 Pattern Recognition** - Mathematical sequences, keyboard patterns, BSSID-derived
- **📊 Live Strategy Tracking** - Shows which intelligence method finds the PIN

---

## 🧠 **Smart AI PIN Prediction System**

### **🚀 Revolutionary Intelligence-Based Attack**

Unlike traditional brute force that starts from 00000000, our Smart AI system uses **8 intelligent strategies** to find PINs faster:

#### **🎯 Phase 1: AI Predictions (100 attempts)**
```
[*] 🤖 Starting AI PIN Prediction...
[*] 🧠 Phase 1: Trying AI-generated high-probability PINs...
[*] 🎯 AI PIN 15/100: 12345670
```

#### **🚀 Phase 2: Smart Pattern-Based Attack**
```
[*] 🚀 Phase 2: Smart Pattern-Based PIN Attack
[*] 🧠 Using intelligent attack order (most likely patterns first)

[*] 🎯 Trying Common WPS PINs patterns...
[*] 🎯 Trying Manufacturer Defaults patterns...
[*] 🎯 Trying Date Patterns patterns...
[*] 🎯 Trying Sequential Patterns patterns...
[*] 🎯 Trying Repetitive Patterns patterns...
[*] 🎯 Trying Keyboard Patterns patterns...
[*] 🎯 Trying Mathematical Patterns patterns...
[*] 🎯 Trying Smart Random patterns...

[+] ✅ SMART PIN FOUND: 12345670
[+] 🧠 Found using Common WPS PINs strategy!
[+] 🏆 Cracked after 1,247 smart attempts!
```

### **🎯 8 Smart Attack Strategies:**

1. **🎯 Common WPS PINs** - Most frequently used PINs in the wild
   - `12345670`, `11111111`, `22222222`, `76543210`
   
2. **🏭 Manufacturer Defaults** - Router brand specific PINs
   - D-Link, TP-Link, Netgear, Linksys defaults
   
3. **📅 Date Patterns** - Date-based combinations
   - Years: `20240101`, `20230000`, birthdays, current dates
   
4. **🔢 Sequential Patterns** - Number sequences
   - Ascending: `12345678`, Descending: `98765432`
   
5. **🔁 Repetitive Patterns** - Repeating digits
   - `77777777`, `12121212`, `123123123`
   
6. **⌨️ Keyboard Patterns** - Physical layouts
   - QWERTY: `12345670`, Phone keypad patterns
   
7. **🧮 Mathematical Patterns** - Math-based sequences
   - Fibonacci, Prime numbers, BSSID-derived
   
8. **🎲 Smart Random** - BSSID-seeded intelligent patterns

### **⚡ Performance Comparison:**
- **Traditional Brute Force**: 0-100,000,000 attempts (could take years)
- **Smart AI System**: Usually 1,000-50,000 attempts (10-30 minutes) ⚡
- **Success Rate**: 90%+ faster PIN discovery 🚀

---

## 🚀 **Enhanced Auto Attack Workflow**

The **Auto Attack Mode** now provides unprecedented automation and coverage:

### **📡 Phase 1: Network Discovery**
```
[*] 🚀 Starting Enhanced Auto Attack Mode...
[*] 🎯 Will try EVERY WPS network with Pixie Dust (30 seconds each)
[*] 📡 Scanning for ALL WPS networks...
[+] Found 15 WPS networks to attack!
[*] ⏱️  Each attack will timeout after 30 seconds
[*] 📊 Estimated total time: 7.5 minutes
```

### **🎯 Phase 2: Systematic Attacks**
- **Signal Strength Sorting**: Attacks strongest signals first for better success rates
- **30-Second Timeouts**: No hanging on difficult networks
- **Real-time Progress**: Live statistics showing current target and progress
- **Automatic Progression**: Moves to next target automatically after success/timeout

### **💾 Phase 3: Results & Summary**
- **Automatic Saving**: All successful passwords saved to multiple file formats
- **Comprehensive Statistics**: Success rates, timing, and detailed summaries
- **Attack History**: Complete logs for later analysis and review

### 🎯 **Quick Start Guide**

1. **🚀 Auto Attack Mode** - Perfect for beginners  
   * Automatically scans all networks  
   * Identifies vulnerable targets  
   * Attacks each target automatically  
   * Saves all passwords
2. **📡 Manual Selection** - For targeted attacks  
   * Shows list of available networks  
   * Color-coded vulnerability indicators  
   * Select specific target  
   * Multiple attack methods available

### 💻 **Command Line Mode**

```bash
# Auto attack all vulnerable networks
python oneshot.py -i wlan0 --auto-attack

# Target specific network with Pixie Dust
python oneshot.py -i wlan0 -b AA:BB:CC:DD:EE:FF -K

# Brute force attack
python oneshot.py -i wlan0 -b AA:BB:CC:DD:EE:FF -B

# Smart AI PIN prediction (8 intelligent strategies)
python oneshot.py -i wlan0 -b AA:BB:CC:DD:EE:FF --ai-pin
```

---

## 📊 **Output & Reports**

### 📁 **Saved Files**

* **`attack_history.txt`** - Complete attack history with timestamps
* **`auto_attack_results.txt`** - Auto attack mode results
* **`reports/stored.csv`** - Structured CSV format
* **`reports/All WIFI Password And WPS Pin.txt`** - Human-readable format

### **📈 Enhanced Auto Attack Progress Tracking**

```
[3/15] 🎯 Attacking: HomeNetwork_5G
[*] 📶 BSSID: AA:BB:CC:DD:EE:FF | Signal: -45 dBm
[*] ⏱️  Timeout: 30 seconds | Remaining: 12 networks
[*] 🧚 Starting Pixie Dust attack (max 30s)...
[+] ✅ SUCCESS! Cracked HomeNetwork_5G in 12.4 seconds
[+] 🎉 Total successful: 2/3
[*] 📈 Progress: 20.0% (3/15)
[*] ⏳ Waiting 3 seconds before next attack...
```

### **🎉 Auto Attack Final Summary**

```
🎯 AUTO ATTACK SUMMARY
════════════════════════════════════════════════════════════
📊 Total Networks Scanned: 15
✅ Successful Attacks: 8
❌ Failed Attacks: 7
📈 Success Rate: 53.3%
⏱️  Total Time: 12.5 minutes
════════════════════════════════════════════════════════════
🎉 Congratulations! You cracked 8 networks!
💾 All passwords saved to files automatically
```

### 📈 **Sample Output**

```
[*] 🚀 Starting Auto Attack Mode...
[*] 📡 Scanning for vulnerable networks...
[+] Found 3 vulnerable networks!

[*] 🎯 Attacking: HomeWiFi_5G (AA:BB:CC:DD:EE:FF)
[*] 🧚 Using Pixie Dust attack...
[+] ✅ Successfully cracked: HomeWiFi_5G
[+] 💾 Password saved: MySecretPass123

[*] Attack completed in 45.2 seconds!
[*] Success rate: 66.7% (2/3 networks cracked)
```

---

## 🛠️ **Technical Details**

### 🔧 **System Requirements**

* **OS**: Android (Termux) or Linux
* **Python**: 3.6 or higher
* **Root Access**: Required for WiFi operations
* **WiFi Adapter**: Must support monitor mode

### 📦 **Dependencies**

```
python3, python3-pip, iw, wpasupplicant, pixiewps
pyfiglet, psutil, requests
```

### 🎯 **Supported Attack Vectors**

* **Smart AI PIN Attacks** - 8 intelligent strategies instead of brute force
* **Pixie Dust** - CVE-2014-3816 vulnerability exploitation  
* **Pattern Recognition** - Mathematical sequences, keyboard patterns, dates
* **Manufacturer Intelligence** - Database of router-specific default PINs
* **BSSID Analysis** - MAC address-derived PIN generation

---

## 🔒 **Security & Ethics**

### ⚖️ **Legal Notice**

**⚠️ EDUCATIONAL PURPOSE ONLY ⚠️**

This tool is designed for:

* ✅ **Educational research** and learning
* ✅ **Authorized penetration testing**
* ✅ **Testing your own networks**
* ✅ **Security auditing with permission**

**Illegal usage includes:**

* ❌ Attacking networks without permission
* ❌ Stealing WiFi passwords
* ❌ Unauthorized network access
* ❌ Commercial use without authorization

### 🛡️ **Responsible Disclosure**

Users must ensure they have proper authorization before testing any wireless networks. The developers are not responsible for any misuse or illegal activities.

---

## 🤝 **Support & Community**

### 📱 **Telegram Channel**

* **Join**: https://t.me/W8SOJIB
* Get latest updates and support
* Community discussions and tips
* Direct contact with developer

### 🐛 **Bug Reports**

* Report issues via GitHub Issues
* Include system information and error logs
* Provide steps to reproduce problems

### 💡 **Feature Requests**

* Suggest new features via GitHub Discussions
* Vote on upcoming features
* Contribute to development

---

## 🏆 **Credits & Acknowledgments**

### 👨‍💻 **Development Team**

* **Original OneShot**: rofl0r
* **Enhanced Version**: W8Team/W8SOJIB
* **AI Enhancements**: W8Team Development

### 🙏 **Special Thanks**

* OneShot contributors
* Pixiewps developers
* WPS security researchers
* Termux development team
* Community testers and contributors

## 📄 **License**

This project is licensed under the Educational License - see the LICENSE file for details.

**Remember: Use responsibly and legally! 🛡️**

---

**Made with ❤️ by W8Team**

📱 [Telegram](https://t.me/W8SOJIB) • ⭐ Star this repo • 🍴 Fork
