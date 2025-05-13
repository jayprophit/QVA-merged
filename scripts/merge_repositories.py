#!/usr/bin/env python3
"""
QVA Repository Merger

This script merges multiple QVA-related repositories into a single, streamlined codebase.
It copies relevant files from source repositories to the target structure,
avoiding duplicates and organizing files according to the integration plan.
"""

import os
import sys
import shutil
import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

# Configuration
SOURCE_REPOS = {
    'QVA': r'C:\Users\jpowe\CascadeProjects\QVA',
    'QVA_v1': r'C:\Users\jpowe\CascadeProjects\QVA-v1',
    'VM_VA_MAIA_QC': r'C:\Users\jpowe\CascadeProjects\VM-VA-MAIA-QC-Virtual-Machine-Virtual-assistant-Multiple-AI-Agents-Quantum-Computer',
    'QVA_MAIN': r'C:\Users\jpowe\CascadeProjects\QuantumVirtualAssistant'
}

TARGET_REPO = r'C:\Users\jpowe\CascadeProjects\QVA-merged'

# File patterns to skip
SKIP_PATTERNS = [
    r'\.git',
    r'\.github',
    r'\.vscode',
    r'\.pytest_cache',
    r'__pycache__',
    r'\.venv',
    r'node_modules',
    r'\.gradle',
    r'\.DS_Store',
    r'\.env$',  # Don't copy actual .env files, only .env.example
]

# Define directory mapping - where files should go in target
DIRECTORY_MAPPING = {
    # Core system files
    r'qva_orchestrator\.py': 'core',
    r'unified_system\.py': 'core',
    r'main-system\.py': 'core',
    r'system_initialization\.py': 'core',
    
    # Quantum files
    r'quantum_.*\.py': 'quantum',
    r'quantum[/\\].*': 'quantum',
    r'enhanced-quantum-core\.py': 'quantum',
    r'quantum_processor\.py': 'quantum/processing',
    
    # AI files
    r'ai_.*\.py': 'ai',
    r'ai[/\\].*': 'ai',
    r'.*ai-.*\.py': 'ai',
    r'unified-ai-agents\.py': 'ai/agents',
    
    # Backend files
    r'backend[/\\].*': 'backend',
    r'api\.py': 'backend/api',
    r'server\.py': 'backend',
    
    # Frontend files
    r'frontend[/\\].*': 'frontend',
    r'.*\.html$': 'frontend/web',
    r'.*\.css$': 'frontend/web',
    r'.*\.js$': 'frontend/web',
    r'.*\.tsx$': 'frontend/web',
    
    # Blockchain files
    r'blockchain[/\\].*': 'blockchain',
    r'.*blockchain.*\.py': 'blockchain',
    
    # Documentation
    r'.*\.md$': 'docs',
    r'docs[/\\].*': 'docs',
    
    # Config files
    r'config\..*': 'config',
    r'config[/\\].*': 'config',
    r'.*\.json$': 'config',
    r'.*\.yaml$': 'config',
    r'.*\.yml$': 'config',
    
    # Test files
    r'test_.*\.py': 'tests',
    r'tests[/\\].*': 'tests',
    
    # Scripts
    r'scripts[/\\].*': 'scripts',
    r'.*\.sh$': 'scripts',
    r'.*\.bat$': 'scripts',
    r'.*\.ps1$': 'scripts',
    
    # Default location for unmatched files
    'DEFAULT': 'src'
}

def should_skip_file(file_path: str) -> bool:
    """Check if a file should be skipped based on patterns."""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False

def get_file_hash(file_path: str) -> str:
    """Generate a hash of the file content."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_target_directory(file_path: str) -> str:
    """Determine target directory based on file path and patterns."""
    for pattern, directory in DIRECTORY_MAPPING.items():
        if re.search(pattern, file_path):
            return directory
    return DIRECTORY_MAPPING['DEFAULT']

def create_directory_structure() -> None:
    """Create the target directory structure."""
    directories = set(DIRECTORY_MAPPING.values())
    directories.add('logs')  # Add logs directory
    
    # Create each directory
    for directory in directories:
        dir_path = os.path.join(TARGET_REPO, directory)
        os.makedirs(dir_path, exist_ok=True)
        
        # Create __init__.py if it's a Python package
        if directory.startswith(('core', 'ai', 'backend', 'quantum', 'shared', 'tests')):
            init_file = os.path.join(dir_path, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""{directory} package."""\n')
        
        # Create subdirectories
        if directory == 'core':
            subdirs = ['ai', 'quantum', 'system', 'interfaces', 'config', 'blockchain']
        elif directory == 'backend':
            subdirs = ['api', 'database', 'services']
        elif directory == 'frontend':
            subdirs = ['web', 'desktop', 'mobile', 'holographic']
        elif directory == 'quantum':
            subdirs = ['simulation', 'algorithms', 'processing']
        elif directory == 'ai':
            subdirs = ['agents', 'models', 'training']
        elif directory == 'blockchain':
            subdirs = ['contracts', 'nodes', 'wallet']
        elif directory == 'docs':
            subdirs = ['architecture', 'api', 'development']
        elif directory == 'tests':
            subdirs = ['unit', 'integration']
        else:
            subdirs = []
            
        for subdir in subdirs:
            subdir_path = os.path.join(dir_path, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            
            # Create __init__.py for Python package subdirectories
            if directory.startswith(('core', 'ai', 'backend', 'quantum', 'shared', 'tests')):
                init_file = os.path.join(subdir_path, '__init__.py')
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f:
                        f.write(f'"""{directory}.{subdir} package."""\n')

def copy_file(src_path: str, target_dir: str, file_registry: Dict[str, str]) -> bool:
    """
    Copy file to target directory if it doesn't exist or is different.
    Returns True if file was copied, False otherwise.
    """
    # Get the file name from the source path
    file_name = os.path.basename(src_path)
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Build the target path
    target_path = os.path.join(target_dir, file_name)
    
    # Check if target file already exists
    if os.path.exists(target_path):
        # Compare file hashes
        src_hash = get_file_hash(src_path)
        target_hash = get_file_hash(target_path)
        
        if src_hash == target_hash:
            # Files are identical, skip
            return False
        else:
            # Files are different, check the registry
            if file_name in file_registry:
                # This file has been seen before
                existing_src = file_registry[file_name]
                
                # Check if we should replace
                if src_path.startswith(SOURCE_REPOS['QVA_MAIN']):
                    # Files from the main QVA repo take precedence
                    shutil.copy2(src_path, target_path)
                    file_registry[file_name] = src_path
                    return True
                else:
                    # Keep the existing file
                    return False
            else:
                # First encounter with this name but duplicated path
                # Use a unique name by adding a prefix
                repo_prefix = next((name for name, path in SOURCE_REPOS.items() 
                                   if src_path.startswith(path)), "UNKNOWN")
                new_name = f"{repo_prefix}_{file_name}"
                target_path = os.path.join(target_dir, new_name)
                shutil.copy2(src_path, target_path)
                file_registry[new_name] = src_path
                return True
    else:
        # Target file doesn't exist, copy it
        shutil.copy2(src_path, target_path)
        file_registry[file_name] = src_path
        return True

def process_repository(repo_path: str, file_registry: Dict[str, str]) -> int:
    """
    Process a single repository, copying files to target.
    Returns the number of files copied.
    """
    copied_count = 0
    
    for root, dirs, files in os.walk(repo_path):
        # Skip directories based on patterns
        dirs[:] = [d for d in dirs if not should_skip_file(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip files based on patterns
            if should_skip_file(file_path):
                continue
                
            # Determine target directory
            rel_path = os.path.relpath(file_path, repo_path)
            target_dir_name = find_target_directory(rel_path)
            target_dir = os.path.join(TARGET_REPO, target_dir_name)
            
            # Copy the file if needed
            if copy_file(file_path, target_dir, file_registry):
                copied_count += 1
                
    return copied_count

def main() -> None:
    """Main function to merge repositories."""
    print(f"Starting QVA repository merger...")
    
    # File registry to track copied files and avoid duplicates
    file_registry = {}
    
    # Create target directory structure
    print("Creating directory structure...")
    create_directory_structure()
    
    # Process each repository
    total_copied = 0
    for repo_name, repo_path in SOURCE_REPOS.items():
        print(f"Processing repository: {repo_name}...")
        if not os.path.exists(repo_path):
            print(f"WARNING: Repository path not found: {repo_path}")
            continue
            
        copied = process_repository(repo_path, file_registry)
        total_copied += copied
        print(f"Copied {copied} files from {repo_name}")
    
    # Create a report
    report = {
        "total_files_copied": total_copied,
        "repositories_processed": list(SOURCE_REPOS.keys()),
        "file_registry_size": len(file_registry),
        "target_repository": TARGET_REPO
    }
    
    with open(os.path.join(TARGET_REPO, "merger_report.json"), "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Merger complete! Copied {total_copied} files to {TARGET_REPO}")
    print(f"See merger_report.json for details")

if __name__ == "__main__":
    main()
