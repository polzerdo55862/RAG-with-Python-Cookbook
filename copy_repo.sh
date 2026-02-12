#!/bin/bash

# Script to create a local copy of the RAG-with-Python-Cookbook repository
# Usage: ./copy_repo.sh NEW_REPO_NAME [--keep-git-history]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to display usage
usage() {
    echo "Usage: $0 NEW_REPO_NAME [--keep-git-history]"
    echo ""
    echo "Arguments:"
    echo "  NEW_REPO_NAME       Name for the new repository copy"
    echo "  --keep-git-history  Optional flag to preserve git history (default: create fresh history)"
    echo ""
    echo "Example:"
    echo "  $0 My-RAG-Cookbook"
    echo "  $0 My-RAG-Cookbook --keep-git-history"
    exit 1
}

# Check if repository name is provided
if [ $# -lt 1 ]; then
    print_error "Repository name is required!"
    usage
fi

NEW_REPO_NAME="$1"

# Check if help is requested
if [ "$NEW_REPO_NAME" == "--help" ] || [ "$NEW_REPO_NAME" == "-h" ]; then
    usage
fi

KEEP_GIT_HISTORY=false

# Check for optional flag
if [ $# -eq 2 ] && [ "$2" == "--keep-git-history" ]; then
    KEEP_GIT_HISTORY=true
fi

# Get the current directory (where the script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
NEW_REPO_PATH="$PARENT_DIR/$NEW_REPO_NAME"

print_info "Starting repository copy process..."
print_info "Source: $SCRIPT_DIR"
print_info "Destination: $NEW_REPO_PATH"

# Check if destination already exists
if [ -d "$NEW_REPO_PATH" ]; then
    print_error "Directory '$NEW_REPO_PATH' already exists!"
    print_error "Please choose a different name or remove the existing directory."
    exit 1
fi

# Create a copy of the repository
print_info "Copying repository files..."
cp -r "$SCRIPT_DIR" "$NEW_REPO_PATH"

# Navigate to the new repository
cd "$NEW_REPO_PATH"

if [ "$KEEP_GIT_HISTORY" = false ]; then
    print_info "Creating fresh git history..."
    
    # Remove existing git directory
    rm -rf .git
    
    # Initialize new git repository
    git init
    
    # Set default branch to main
    # Try git branch -M (rename existing branch), fallback to checkout -b (create new), ignore errors
    git branch -M main 2>/dev/null || git checkout -b main 2>/dev/null || true
    
    # Create .gitignore if it doesn't exist
    if [ ! -f .gitignore ]; then
        print_warning ".gitignore not found, creating a basic one..."
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Jupyter Notebook
.ipynb_checkpoints

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data files (optional - uncomment if you don't want to track large datasets)
# *.csv
# *.parquet
# *.h5
EOF
    fi
    
    # Stage all files
    git add .
    
    # Create initial commit (check if git user is configured)
    if git config user.email > /dev/null 2>&1; then
        git commit -m "Initial commit: Copy of RAG-with-Python-Cookbook"
        print_success "Fresh git repository initialized with initial commit."
    else
        print_warning "Git user not configured. Files are staged but not committed."
        print_info "To complete the setup, run:"
        echo "     git config user.email 'you@example.com'"
        echo "     git config user.name 'Your Name'"
        echo "     git commit -m 'Initial commit: Copy of RAG-with-Python-Cookbook'"
    fi
else
    print_info "Keeping original git history..."
    
    # Remove the original remote
    git remote remove origin 2>/dev/null || print_warning "No origin remote to remove."
    
    print_success "Original git history preserved."
fi

print_success "Repository copied successfully to: $NEW_REPO_PATH"
echo ""
print_info "Next steps:"
echo "  1. Navigate to the new repository:"
echo "     cd $NEW_REPO_PATH"
echo ""
echo "  2. Update README.md with your repository information:"
echo "     - Change the title"
echo "     - Update GitHub URLs"
echo "     - Modify the description"
echo ""
echo "  3. (Optional) Create a new repository on GitHub and link it:"
echo "     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "  4. Review and update dependencies in each chapter directory"
echo ""
print_info "For more detailed instructions, see CLONING_GUIDE.md"
