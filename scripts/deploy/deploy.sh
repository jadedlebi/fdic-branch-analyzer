#!/bin/bash

# FDIC Branch Analyzer Deployment Script
# This script automates the deployment process for GitHub Pages

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_NAME="fdic-branch-analyzer"
GITHUB_USER="jadedlebi"
BRANCH="main"
WEB_DIR="web"

echo -e "${BLUE}🚀 Starting FDIC Branch Analyzer Deployment${NC}"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Error: git is not installed${NC}"
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Checking current status...${NC}"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    echo -e "${YELLOW}   Consider committing them before deployment${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Deployment cancelled${NC}"
        exit 1
    fi
fi

# Check if web directory exists
if [ ! -d "$WEB_DIR" ]; then
    echo -e "${RED}❌ Error: $WEB_DIR directory not found${NC}"
    exit 1
fi

echo -e "${YELLOW}🔍 Validating web files...${NC}"

# Check for required files
required_files=("$WEB_DIR/index.html" "$WEB_DIR/css/style.css" "$WEB_DIR/js/app.js")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Error: Required file not found: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ All required files found${NC}"

# Check if remote repository exists
if ! git ls-remote --exit-code origin &> /dev/null; then
    echo -e "${RED}❌ Error: Remote repository not found${NC}"
    echo -e "${YELLOW}   Please add the remote repository:${NC}"
    echo -e "${YELLOW}   git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git${NC}"
    exit 1
fi

echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"

# Add all files
git add .

# Commit changes
if git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  No changes to commit${NC}"
else
    git commit -m "Deploy FDIC Branch Analyzer - $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}✅ Changes committed${NC}"
fi

# Push to GitHub
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
git push origin $BRANCH

echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"

# Wait for GitHub Pages to build
echo -e "${YELLOW}⏳ Waiting for GitHub Pages to build...${NC}"
echo -e "${YELLOW}   This may take a few minutes...${NC}"

# Check GitHub Pages status
echo -e "${BLUE}🔗 Your site will be available at:${NC}"
echo -e "${GREEN}   https://$GITHUB_USER.github.io/$REPO_NAME/${NC}"

echo -e "${BLUE}📋 Next steps:${NC}"
echo -e "${YELLOW}   1. Go to your repository settings${NC}"
echo -e "${YELLOW}   2. Navigate to Pages section${NC}"
echo -e "${YELLOW}   3. Set source to 'Deploy from a branch'${NC}"
echo -e "${YELLOW}   4. Select branch: $BRANCH${NC}"
echo -e "${YELLOW}   5. Select folder: /$WEB_DIR${NC}"
echo -e "${YELLOW}   6. Click Save${NC}"

echo -e "${GREEN}🎉 Deployment script completed successfully!${NC}"
echo -e "${BLUE}   Your site should be live in a few minutes.${NC}" 