#!/bin/bash
# Example usage script for update_notebooks_from_asciidoc.py

echo "================================================"
echo "Notebook Update Script - Example Usage"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "update_notebooks_from_asciidoc.py" ]; then
    echo "Error: update_notebooks_from_asciidoc.py not found"
    echo "Please run this from the repository root"
    exit 1
fi

# Show current state
echo "Current notebooks:"
echo "  1. ch08_agentic_rag/01_Agents_with_Function_Calling/building_agents_without_framework.ipynb"
echo "  2. ch08_agentic_rag/02_OpenAI_SDK/building_agents_with_openai_sdk.ipynb"
echo "  3. ch08_agentic_rag/04_Langgraph_agents/building_agents_using_langgraph.ipynb"
echo ""

# Run the update script
echo "Running update script..."
echo ""
python3 update_notebooks_from_asciidoc.py

# Check results
echo ""
echo "================================================"
echo "Update Complete!"
echo "================================================"
echo ""
echo "Check the following:"
echo "  ✓ Backup files created with timestamp"
echo "  ✓ notebook_update_report.txt for detailed results"
echo "  ✓ Git diff to see changes"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff ch08_agentic_rag/"
echo "  2. Test notebooks in Jupyter"
echo "  3. Commit if satisfied: git add . && git commit -m 'Update notebooks'"
echo ""
