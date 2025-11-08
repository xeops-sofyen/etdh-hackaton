#!/bin/bash

################################################################################
# Heimdall Sphinx Simulator - GCP Deployment Script
# Project: xeops-ai
# Region: europe-west1
################################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="xeops-ai"
REGION="europe-west1"
ZONE="europe-west1-b"
INSTANCE_NAME="heimdall-sphinx-simulator"
MACHINE_TYPE="n1-standard-4"
GPU_TYPE="nvidia-tesla-t4"
GPU_COUNT=1
BOOT_DISK_SIZE="50GB"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"

echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🚁 Heimdall Sphinx Simulator - GCP Deployment${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""
echo -e "${YELLOW}Project:${NC}  $PROJECT_ID"
echo -e "${YELLOW}Region:${NC}   $REGION"
echo -e "${YELLOW}Zone:${NC}     $ZONE"
echo -e "${YELLOW}Instance:${NC} $INSTANCE_NAME"
echo -e "${YELLOW}GPU:${NC}      $GPU_TYPE x $GPU_COUNT"
echo ""

# Check if user is authenticated
echo -e "${BLUE}[1/7]${NC} Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not authenticated. Please run: gcloud auth login${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Authenticated as: $(gcloud config get-value account)"

# Set project
echo -e "${BLUE}[2/7]${NC} Setting project and region..."
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE
echo -e "${GREEN}✓${NC} Configuration set"

# Enable required APIs
echo -e "${BLUE}[3/7]${NC} Enabling required APIs..."
gcloud services enable compute.googleapis.com --quiet
echo -e "${GREEN}✓${NC} APIs enabled"

# Check GPU quota
echo -e "${BLUE}[4/7]${NC} Checking GPU availability..."
echo -e "${YELLOW}Note:${NC} If this fails, you may need to request GPU quota increase at:"
echo -e "       https://console.cloud.google.com/iam-admin/quotas?project=$PROJECT_ID"

# Create firewall rules
echo -e "${BLUE}[5/7]${NC} Creating firewall rules..."

# Backend API (port 8000)
if ! gcloud compute firewall-rules describe heimdall-allow-backend &>/dev/null; then
    gcloud compute firewall-rules create heimdall-allow-backend \
        --direction=INGRESS \
        --priority=1000 \
        --network=default \
        --action=ALLOW \
        --rules=tcp:8000 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=heimdall-sphinx \
        --quiet
    echo -e "${GREEN}✓${NC} Created firewall rule: heimdall-allow-backend (port 8000)"
else
    echo -e "${YELLOW}↻${NC} Firewall rule heimdall-allow-backend already exists"
fi

# Monitor server (port 8001)
if ! gcloud compute firewall-rules describe heimdall-allow-monitor &>/dev/null; then
    gcloud compute firewall-rules create heimdall-allow-monitor \
        --direction=INGRESS \
        --priority=1000 \
        --network=default \
        --action=ALLOW \
        --rules=tcp:8001 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=heimdall-sphinx \
        --quiet
    echo -e "${GREEN}✓${NC} Created firewall rule: heimdall-allow-monitor (port 8001)"
else
    echo -e "${YELLOW}↻${NC} Firewall rule heimdall-allow-monitor already exists"
fi

# Sphinx ports (8383, 9100)
if ! gcloud compute firewall-rules describe heimdall-allow-sphinx &>/dev/null; then
    gcloud compute firewall-rules create heimdall-allow-sphinx \
        --direction=INGRESS \
        --priority=1000 \
        --network=default \
        --action=ALLOW \
        --rules=tcp:8383,udp:8383,tcp:9100 \
        --source-ranges=0.0.0.0/0 \
        --target-tags=heimdall-sphinx \
        --quiet
    echo -e "${GREEN}✓${NC} Created firewall rule: heimdall-allow-sphinx (ports 8383, 9100)"
else
    echo -e "${YELLOW}↻${NC} Firewall rule heimdall-allow-sphinx already exists"
fi

# Create VM instance
echo -e "${BLUE}[6/7]${NC} Creating GPU-enabled VM instance..."
echo -e "${YELLOW}Note:${NC} This may take 3-5 minutes..."

if gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  Instance $INSTANCE_NAME already exists!"
    read -p "Delete and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}↻${NC} Deleting existing instance..."
        gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE --quiet
    else
        echo -e "${RED}❌ Aborted${NC}"
        exit 1
    fi
fi

# Create instance with startup script
gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --accelerator=type=$GPU_TYPE,count=$GPU_COUNT \
    --image-family=$IMAGE_FAMILY \
    --image-project=$IMAGE_PROJECT \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --maintenance-policy=TERMINATE \
    --metadata=install-nvidia-driver=True \
    --tags=heimdall-sphinx,http-server,https-server \
    --scopes=cloud-platform \
    --quiet

echo -e "${GREEN}✓${NC} VM instance created successfully!"

# Wait for instance to be ready
echo -e "${BLUE}[7/7]${NC} Waiting for instance to be ready..."
sleep 30

# Get instance IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo ""
echo -e "${BLUE}================================================================================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${BLUE}================================================================================================${NC}"
echo ""
echo -e "${YELLOW}Instance Details:${NC}"
echo -e "  Name:        $INSTANCE_NAME"
echo -e "  Zone:        $ZONE"
echo -e "  External IP: ${GREEN}$EXTERNAL_IP${NC}"
echo -e "  Machine:     $MACHINE_TYPE"
echo -e "  GPU:         $GPU_TYPE x $GPU_COUNT"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "1. SSH into the instance (wait 2-3 minutes for NVIDIA drivers to install):"
echo -e "   ${GREEN}gcloud compute ssh $INSTANCE_NAME --zone=$ZONE${NC}"
echo ""
echo -e "2. Once SSH'd in, verify GPU is detected:"
echo -e "   ${GREEN}nvidia-smi${NC}"
echo ""
echo -e "3. Run the setup script:"
echo -e "   ${GREEN}curl -fsSL https://raw.githubusercontent.com/xeops-sofyen/etdh-hackaton/main/scripts/setup-sphinx-vm.sh | bash${NC}"
echo ""
echo -e "   ${YELLOW}OR manually follow the steps in:${NC}"
echo -e "   GCP_SPHINX_DEPLOYMENT.md (Step 4 onwards)"
echo ""
echo -e "${YELLOW}Access URLs (after setup):${NC}"
echo -e "  Backend API:    ${GREEN}http://$EXTERNAL_IP:8000${NC}"
echo -e "  Monitor:        ${GREEN}http://$EXTERNAL_IP:8001${NC}"
echo ""
echo -e "${YELLOW}Cost Estimate:${NC}"
echo -e "  ~€450-500/month (n1-standard-4 + Tesla T4 in europe-west1)"
echo ""
echo -e "${YELLOW}To stop the instance (to save costs):${NC}"
echo -e "  ${GREEN}gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE${NC}"
echo ""
echo -e "${YELLOW}To delete the instance:${NC}"
echo -e "  ${GREEN}gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE${NC}"
echo ""
echo -e "${BLUE}================================================================================================${NC}"
