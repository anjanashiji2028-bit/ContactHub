#!/usr/bin/env bash
# ==============================================================================
# ContactHub - Module 2: Virtual Machine Automation Script (virsh / KVM)
# Automates VM lifecycle operations: start, stop, restart, status, list, info
# ==============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    cat << EOF
ContactHub VM Lifecycle Automation Utility
Usage: $(basename "$0") <COMMAND> [VM_NAME]

Commands:
  list              List all virtual machines and their current runtime state
  start <vm>        Power on / start the specified virtual machine
  stop <vm>         Gracefully shut down the specified virtual machine
  force-stop <vm>   Force power-off (hard reset) the specified virtual machine
  restart <vm>      Reboot the specified virtual machine
  status <vm>       Display running status of the specified virtual machine
  info <vm>         Display detailed domain hardware configuration (RAM, vCPU, OS)

Examples:
  $(basename "$0") list
  $(basename "$0") start ubuntu-contacthub
  $(basename "$0") status ubuntu-contacthub
  $(basename "$0") stop ubuntu-contacthub
EOF
}

# Check if virsh command is available
if ! command -v virsh &> /dev/null; then
    echo -e "${RED}[ERROR] 'virsh' utility was not found.${NC}"
    echo -e "${YELLOW}Please run './scripts/setup_kvm.sh' first to install KVM and libvirt.${NC}"
    exit 1
fi

COMMAND=${1:-}
VM_NAME=${2:-}

case "$COMMAND" in
    list)
        echo -e "${BLUE}[*] Fetching all registered virtual machines in libvirt...${NC}"
        virsh list --all
        ;;

    start)
        if [ -z "$VM_NAME" ]; then
            echo -e "${RED}[ERROR] VM name is required for 'start' command.${NC}"
            echo -e "Usage: $0 start <vm-name>"
            exit 1
        fi
        echo -e "${YELLOW}[*] Starting virtual machine: ${VM_NAME}...${NC}"
        virsh start "$VM_NAME"
        echo -e "${GREEN}[+] VM '${VM_NAME}' started successfully.${NC}"
        ;;

    stop)
        if [ -z "$VM_NAME" ]; then
            echo -e "${RED}[ERROR] VM name is required for 'stop' command.${NC}"
            echo -e "Usage: $0 stop <vm-name>"
            exit 1
        fi
        echo -e "${YELLOW}[*] Sending ACPI graceful shutdown signal to: ${VM_NAME}...${NC}"
        virsh shutdown "$VM_NAME"
        echo -e "${GREEN}[+] Shutdown signal transmitted to '${VM_NAME}'.${NC}"
        ;;

    force-stop)
        if [ -z "$VM_NAME" ]; then
            echo -e "${RED}[ERROR] VM name is required for 'force-stop' command.${NC}"
            exit 1
        fi
        echo -e "${RED}[*] Forcefully terminating virtual machine: ${VM_NAME}...${NC}"
        virsh destroy "$VM_NAME"
        echo -e "${YELLOW}[+] VM '${VM_NAME}' has been forcefully stopped.${NC}"
        ;;

    restart)
        if [ -z "$VM_NAME" ]; then
            echo -e "${RED}[ERROR] VM name is required for 'restart' command.${NC}"
            exit 1
        fi
        echo -e "${YELLOW}[*] Rebooting virtual machine: ${VM_NAME}...${NC}"
        virsh reboot "$VM_NAME"
        echo -e "${GREEN}[+] Reboot command sent to '${VM_NAME}'.${NC}"
        ;;

    status)
        if [ -z "$VM_NAME" ]; then
            echo -e "${RED}[ERROR] VM name is required for 'status' command.${NC}"
            exit 1
        fi
        STATE=$(virsh domstate "$VM_NAME" 2>/dev/null || echo "Unknown / Not found")
        echo -e "${BLUE}Virtual Machine:${NC} $VM_NAME"
        echo -e "${BLUE}Current State:  ${NC} $STATE"
        ;;

    info)
        if [ -z "$VM_NAME" ]; then
            echo -e "${RED}[ERROR] VM name is required for 'info' command.${NC}"
            exit 1
        fi
        echo -e "${BLUE}[*] Detailed domain specification for: ${VM_NAME}${NC}"
        virsh dominfo "$VM_NAME"
        ;;

    -h|--help|help|"")
        show_help
        exit 0
        ;;

    *)
        echo -e "${RED}[ERROR] Unknown command: '$COMMAND'${NC}\n"
        show_help
        exit 1
        ;;
esac
