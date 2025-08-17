#!/usr/bin/env python3
"""
Git Setup Script for SEP QP Pack Generator
Helps initialize Git repository and prepare for GitHub upload
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_git_installed():
    """Check if Git is installed"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_git_repository():
    """Set up Git repository"""
    print("🚀 Setting up Git repository for SEP QP Pack Generator")
    print("=" * 60)
    
    # Check if Git is installed
    if not check_git_installed():
        print("❌ Git is not installed. Please install Git first.")
        print("   Download from: https://git-scm.com/downloads")
        return False
    
    # Check if already a Git repository
    if os.path.exists(".git"):
        print("⚠️  This directory is already a Git repository")
        choice = input("Do you want to reinitialize? (y/N): ").strip().lower()
        if choice != 'y':
            print("Skipping Git initialization")
            return True
    
    # Initialize Git repository
    if not run_command("git init", "Initializing Git repository"):
        return False
    
    # Add all files
    if not run_command("git add .", "Adding all files to Git"):
        return False
    
    # Create initial commit
    if not run_command('git commit -m "Initial commit: SEP QP Pack Generator with real data integration"', "Creating initial commit"):
        return False
    
    print("\n✅ Git repository setup complete!")
    return True

def setup_github_remote():
    """Set up GitHub remote repository"""
    print("\n🌐 Setting up GitHub remote repository")
    print("=" * 60)
    
    # Get GitHub repository URL
    repo_url = input("Enter your GitHub repository URL (e.g., https://github.com/username/repo-name.git): ").strip()
    
    if not repo_url:
        print("❌ No repository URL provided. Skipping remote setup.")
        return False
    
    # Add remote origin
    if not run_command(f'git remote add origin {repo_url}', "Adding GitHub remote"):
        return False
    
    # Push to GitHub
    if not run_command("git branch -M main", "Setting main branch"):
        return False
    
    if not run_command("git push -u origin main", "Pushing to GitHub"):
        print("⚠️  Push failed. This might be normal if the repository doesn't exist yet.")
        print("   Please create the repository on GitHub first, then run:")
        print("   git push -u origin main")
        return False
    
    print("\n✅ GitHub remote setup complete!")
    return True

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎯 Next Steps:")
    print("=" * 60)
    print("1. Create a new repository on GitHub:")
    print("   - Go to https://github.com/new")
    print("   - Name it: sep-qp-generator")
    print("   - Make it public or private (your choice)")
    print("   - Don't initialize with README (we already have one)")
    
    print("\n2. If you haven't set up the remote yet, run:")
    print("   python setup_git.py")
    
    print("\n3. Or manually set up the remote:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/sep-qp-generator.git")
    print("   git push -u origin main")
    
    print("\n4. Test the system:")
    print("   python sep_qp_generator.py")
    
    print("\n5. Edit program requirements:")
    print("   python program_editor.py")

def main():
    """Main function"""
    print("🌱 SEP QP Pack Generator - Git Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    required_files = ["README.md", "sep_qp_generator.py", "sep_config.json"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please run this script from the project root directory")
        return
    
    # Setup Git repository
    if not setup_git_repository():
        print("❌ Failed to setup Git repository")
        return
    
    # Ask about GitHub remote
    setup_remote = input("\nDo you want to set up a GitHub remote repository now? (y/N): ").strip().lower()
    
    if setup_remote == 'y':
        setup_github_remote()
    
    # Show next steps
    show_next_steps()
    
    print("\n🎉 Setup complete! Your SEP QP Pack Generator is ready for GitHub!")

if __name__ == "__main__":
    main() 