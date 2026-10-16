#!/usr/bin/env bash
# ==============================================================================
# ContactHub - Module 2: Virtualization Tools Setup Script (Linux / KVM)
# Note: Native KVM virtualization requires a Linux operating system (e.g. Ubuntu).
# If running on Windows, execute this inside an Ubuntu VM or WSL2 with nested virt.
# ==============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================================${NC}"
echo -e "${BLUE} ContactHub - KVM / QEMU / libvirt Environment Setup         ${NC}"
echo -e "${BLUE}==============================================================${NC}"

# 1. Verify Root / Sudo Permissions
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}[!] This script requires administrative privileges. Running with sudo...${NC}"
    exec sudo bash "$0" "$@"
fi

# 2. Check Hardware Virtualization Extensions (Intel VT-x / AMD-V)
echo -e "\n${YELLOW}[*] Checking CPU hardware virtualization support...${NC}"
VIRT_COUNT=$(grep -E -c '(vmx|svm)' /proc/cpuinfo || true)

if [ "$VIRT_COUNT" -eq 0 ]; then
    echo -e "${RED}[ERROR] Hardware virtualization (VT-x / AMD-V) is NOT enabled in BIOS or supported by this CPU.${NC}"
    echo -e "${YELLOW}Troubleshooting: Enable Intel Virtualization Technology (VT-x) or AMD-V in your computer's BIOS/UEFI firmware.${NC}"
    exit 1
else
    echo -e "${GREEN}[+] Hardware virtualization support detected (${VIRT_COUNT} logical cores available).${NC}"
fi

# 3. Update Package Repositories
echo -e "\n${YELLOW}[*] Updating apt package index...${NC}"
apt-get update -y

# 4. Install KVM, QEMU, libvirt, and Management Utilities
echo -e "\n${YELLOW}[*] Installing KVM, QEMU, libvirt-daemon, and virt-manager...${NC}"
apt-get install -y --no-install-recommends \
    qemu-kvm \
    libvirt-daemon-system \
    libvirt-clients \
    bridge-utils \
    virtinst \
    virt-manager \
    cpu-checker

# 5. Verify KVM Acceleration
echo -e "\n${YELLOW}[*] Verifying KVM kernel acceleration status...${NC}"
if command -v kvm-ok &> /dev/null; then
    kvm-ok || true
fi

# 6. Enable and Start libvirtd Service
echo -e "\n${YELLOW}[*] Enabling and starting libvirtd daemon service...${NC}"
systemctl enable libvirtd
systemctl restart libvirtd

# 7. Add Non-Root User to libvirt and kvm Groups
REAL_USER=${SUDO_USER:-$USER}
if [ -n "$REAL_USER" ] && [ "$REAL_USER" != "root" ]; then
    echo -e "\n${YELLOW}[*] Granting user '${REAL_USER}' membership in kvm and libvirt groups...${NC}"
    usermod -aG libvirt "$REAL_USER"
    usermod -aG kvm "$REAL_USER"
fi

# 8. Test virsh connectivity
echo -e "\n${YELLOW}[*] Testing libvirt daemon connectivity via virsh...${NC}"
virsh list --all

echo -e "\n${GREEN}==============================================================${NC}"
echo -e "${GREEN} KVM and libvirt Virtualization Stack Configured Successfully! ${NC}"
echo -e "${GREEN} Use './scripts/manage_vm.sh' to control and automate guest VMs. ${NC}"
echo -e "${GREEN}==============================================================${NC}"
