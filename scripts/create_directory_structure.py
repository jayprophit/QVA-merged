#!/usr/bin/env python3
"""
Script to create the directory structure for the Quantum Virtual Assistant (QVA) project.
"""

import os
import sys

# Define the directory structure
directories = [
    'core',
    'core/ai',
    'core/quantum',
    'core/system',
    'core/interfaces',
    'core/config',
    'core/blockchain',
    'backend',
    'backend/api',
    'backend/database',
    'backend/services',
    'frontend',
    'frontend/web',
    'frontend/desktop',
    'frontend/mobile',
    'frontend/holographic',
    'quantum',
    'quantum/simulation',
    'quantum/algorithms',
    'quantum/processing',
    'ai',
    'ai/agents',
    'ai/models',
    'ai/training',
    'blockchain',
    'blockchain/contracts',
    'blockchain/nodes',
    'blockchain/wallet',
    'docs',
    'docs/architecture',
    'docs/api',
    'docs/development',
    'config',
    'scripts',
    'tests',
    'tests/unit',
    'tests/integration',
    'ui',
    'ui/components',
    'ui/assets',
    'ui/styles',
    'src',
    'shared',
    'shared/utils',
    'shared/models',
    'infrastructure',
    'infrastructure/deployment',
    'infrastructure/monitoring',
    'logs'
]

# Create the directories
base_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Creating directory structure in: {base_dir}")

for directory in directories:
    dir_path = os.path.join(base_dir, directory)
    try:
        os.makedirs(dir_path, exist_ok=True)
        # Create an empty __init__.py file in each directory to make it a proper Python package
        if directory.startswith('core') or directory.startswith('ai') or directory.startswith('backend') or \
           directory.startswith('quantum') or directory.startswith('shared') or directory.startswith('tests'):
            init_file = os.path.join(dir_path, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('"""' + directory.replace('/', '.') + ' package."""\n')
        print(f"Created: {directory}")
    except Exception as e:
        print(f"Error creating {directory}: {e}", file=sys.stderr)

print("Directory structure created successfully.")
