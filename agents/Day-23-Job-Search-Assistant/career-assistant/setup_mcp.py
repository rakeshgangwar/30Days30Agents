#!/usr/bin/env python3
"""
Setup script for MCP server dependencies and verification.
This script ensures that Node.js and the required MCP servers are available.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description="", check=True):
    """Run a shell command and return the result."""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   ❌ {e.stderr.strip()}")
        return None


def check_node_js():
    """Check if Node.js is installed."""
    print("\n📦 Checking Node.js installation...")
    result = run_command("node --version", "Checking Node.js version", check=False)
    
    if result and result.returncode == 0:
        print(f"   ✅ Node.js is installed: {result.stdout.strip()}")
        return True
    else:
        print("   ❌ Node.js is not installed or not in PATH")
        print("   📋 Please install Node.js from: https://nodejs.org/")
        return False


def check_npx():
    """Check if npx is available."""
    print("\n📦 Checking npx availability...")
    result = run_command("npx --version", "Checking npx version", check=False)
    
    if result and result.returncode == 0:
        print(f"   ✅ npx is available: {result.stdout.strip()}")
        return True
    else:
        print("   ❌ npx is not available")
        return False


def verify_mcp_servers():
    """Verify MCP servers can be installed."""
    print("\n🔧 Verifying MCP server packages...")
    
    # Check if Exa MCP server is available
    print("   📡 Testing Exa MCP server...")
    result = run_command(
        "npx -y exa-mcp-server --help", 
        "Testing Exa MCP server installation", 
        check=False
    )
    exa_available = result and result.returncode == 0
    
    # Check if Firecrawl MCP server is available
    print("   🕷️  Testing Firecrawl MCP server...")
    result = run_command(
        "npx -y firecrawl-mcp --help", 
        "Testing Firecrawl MCP server installation", 
        check=False
    )
    firecrawl_available = result and result.returncode == 0
    
    return exa_available, firecrawl_available


def check_environment_variables():
    """Check if required environment variables are set."""
    print("\n🔑 Checking environment variables...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("   ⚠️  .env file not found. Please copy env_example.txt to .env and add your API keys.")
        return False
    
    # Read .env file
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    required_vars = ['OPENAI_API_KEY', 'EXA_API_KEY', 'FIRECRAWL_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if var not in env_vars or not env_vars[var] or env_vars[var] == f'your_{var.lower()}_here':
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ Missing or placeholder values for: {', '.join(missing_vars)}")
        return False
    else:
        print("   ✅ All required environment variables are set")
        return True


def main():
    """Run the complete setup verification."""
    print("🚀 Career Assistant MCP Setup Verification")
    print("=" * 50)
    
    # Check prerequisites
    node_ok = check_node_js()
    npx_ok = check_npx()
    
    if not (node_ok and npx_ok):
        print("\n❌ Prerequisites missing. Please install Node.js first.")
        sys.exit(1)
    
    # Verify MCP servers
    exa_ok, firecrawl_ok = verify_mcp_servers()
    
    # Check environment
    env_ok = check_environment_variables()
    
    # Summary
    print("\n📋 Setup Summary:")
    print("=" * 30)
    print(f"   Node.js:           {'✅' if node_ok else '❌'}")
    print(f"   npx:               {'✅' if npx_ok else '❌'}")
    print(f"   Exa MCP Server:    {'✅' if exa_ok else '❌'}")
    print(f"   Firecrawl MCP:     {'✅' if firecrawl_ok else '❌'}")
    print(f"   Environment:       {'✅' if env_ok else '❌'}")
    
    if all([node_ok, npx_ok, exa_ok, firecrawl_ok, env_ok]):
        print("\n🎉 All systems ready! You can now run the career assistant.")
        print("   Run: python streamlined_cli.py")
    else:
        print("\n⚠️  Some issues found. Please address them before running the application.")
        if not env_ok:
            print("   • Copy env_example.txt to .env and add your API keys")
        if not (exa_ok and firecrawl_ok):
            print("   • MCP servers will be downloaded automatically when first used")


if __name__ == "__main__":
    main() 