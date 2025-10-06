#!/usr/bin/env python3
"""
Automation Setup Script
======================

This script creates the organized folder structure for all automations.
"""

import os
import shutil

def create_automation_structure():
    """Create organized folder structure for all automations"""
    
    automations = [
        'document_processing',
        'workflow_builder', 
        'data_integration',
        'report_generator',
        'ai_assistant'
    ]
    
    subfolders = ['core', 'workflows', 'api', 'config']
    
    for automation in automations:
        automation_path = f"automations/{automation}"
        
        # Create main automation folder
        os.makedirs(automation_path, exist_ok=True)
        
        # Create subfolders
        for subfolder in subfolders:
            subfolder_path = f"{automation_path}/{subfolder}"
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Create __init__.py files
            init_file = f"{subfolder_path}/__init__.py"
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""\n{automation.replace("_", " ").title()} {subfolder.title()}\n"""\n')
        
        print(f"✅ Created structure for {automation}")

if __name__ == "__main__":
    create_automation_structure()
    print("🎉 All automation structures created!")
