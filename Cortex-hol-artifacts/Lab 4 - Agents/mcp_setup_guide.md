# MCP Development Environment Setup Guide

This guide documents the complete setup process for Python 3.10+ and Python MCP SDK 1.2.0+ on macOS.

## Prerequisites Check

Before starting, we verified the existing Python installations:

```bash
# Check default Python version
python --version
# Output: Python 3.9.6 (below requirement)

# Check python3 version  
python3 --version
# Output: Python 3.13.5 (exceeds requirement but not accessible via 'python')

# Check conda availability
conda --version
# Output: conda 23.7.4 (available for environment management)
```

## Step 1: Create Conda Environment with Python 3.10+

We created a dedicated conda environment to ensure clean Python 3.10+ installation:

```bash
# Create new conda environment with Python 3.11
conda create -n mcp-env python=3.11 -y
```

**Output highlights:**
- Environment created at: `/Users/aneel/anaconda3/envs/mcp-env`
- Python 3.11.13 installed
- Includes essential packages: pip, setuptools, wheel, etc.

## Step 2: Activate the Environment

```bash
# Activate the new environment
conda activate mcp-env
```

**Note:** The prompt should change to show `(mcp-env)` indicating the environment is active.

## Step 3: Resolve Python Alias Conflicts

Initially encountered an issue where `python` command was aliased to system Python:

```bash
# Check which Python is being used
which python
# Output: python: aliased to /usr/bin/python3

# Verify conda environment Python
/Users/aneel/anaconda3/envs/mcp-env/bin/python --version
# Output: Python 3.11.13 ✅

# Remove the conflicting alias
unalias python

# Verify Python now uses conda environment
python --version
# Output: Python 3.11.13 ✅
```

## Step 4: Install MCP SDK 1.2.0+

Install the Model Context Protocol SDK with proper version requirements:

```bash
# Install MCP SDK (quoted to avoid shell parsing issues)
pip install "mcp>=1.2.0"
```

**Installation details:**
- **MCP Version Installed:** 1.13.1 (exceeds 1.2.0+ requirement)
- **Key Dependencies Installed:**
  - `anyio>=4.5` - Async I/O support
  - `httpx>=0.27.1` - HTTP client
  - `httpx-sse>=0.4` - Server-sent events
  - `jsonschema>=4.20.0` - JSON schema validation
  - `pydantic>=2.11.0` - Data validation
  - `starlette>=0.27` - ASGI framework
  - `uvicorn>=0.31.1` - ASGI server

## Step 5: Verify Installation

### Check MCP Package Details
```bash
pip show mcp
```

**Expected output:**
```
Name: mcp
Version: 1.13.1
Summary: Model Context Protocol SDK
Home-page: https://modelcontextprotocol.io
Author: Anthropic, PBC.
License: MIT
```

### Test MCP Module Imports
```bash
# Verify core MCP modules can be imported
python -c "import mcp.client; import mcp.server; print('✅ MCP SDK 1.13.1 installed successfully!')"
```

**Expected output:**
```
✅ MCP SDK 1.13.1 installed successfully!
```

## Final Environment Verification

### Current Environment Status
```bash
# Check active conda environment
conda info --envs
# Should show: mcp-env *  /Users/aneel/anaconda3/envs/mcp-env

# Verify Python version
python --version
# Output: Python 3.11.13

# Verify MCP availability
python -c "import mcp; print('MCP SDK ready for development!')"
```

## Usage Instructions

### Daily Workflow

1. **Activate Environment:**
   ```bash
   conda activate mcp-env
   ```

2. **Verify Setup:**
   ```bash
   python -c "import mcp.client; import mcp.server; print('Ready!')"
   ```

3. **Develop with MCP:**
   ```python
   # Example MCP client usage
   import mcp.client
   
   # Your MCP development code here
   ```

4. **Deactivate When Done:**
   ```bash
   conda deactivate
   ```

### Environment Management

- **List environments:** `conda info --envs`
- **Remove environment:** `conda env remove -n mcp-env`
- **Update packages:** `pip install --upgrade mcp`

## Troubleshooting

### Common Issues & Solutions

1. **Python alias conflicts:**
   ```bash
   unalias python  # Remove conflicting aliases
   ```

2. **Environment not activating:**
   ```bash
   conda deactivate  # Ensure clean state
   conda activate mcp-env  # Re-activate
   ```

3. **Version requirements not met:**
   ```bash
   pip install --upgrade "mcp>=1.2.0"  # Force upgrade
   ```

4. **Import errors:**
   ```bash
   pip list | grep mcp  # Verify installation
   python -c "import sys; print(sys.path)"  # Check Python path
   ```

## Requirements Summary

✅ **Python 3.10+ Requirement:** SATISFIED  
- **Installed:** Python 3.11.13  
- **Location:** `/Users/aneel/anaconda3/envs/mcp-env`  

✅ **MCP SDK 1.2.0+ Requirement:** SATISFIED  
- **Installed:** MCP SDK 1.13.1  
- **Dependencies:** Complete with all required packages  

## Next Steps

Your environment is now ready for:
- MCP server development
- MCP client applications  
- Model Context Protocol integrations
- Testing and debugging MCP implementations

## Additional Resources

- **MCP Documentation:** https://modelcontextprotocol.io
- **MCP GitHub:** https://github.com/modelcontextprotocol
- **Conda Documentation:** https://docs.conda.io/
- **Python Virtual Environments:** https://docs.python.org/3/tutorial/venv.html

---

**Setup Date:** $(date)  
**Environment:** mcp-env  
**Python Version:** 3.11.13  
**MCP SDK Version:** 1.13.1  
**Status:** ✅ Ready for Development
