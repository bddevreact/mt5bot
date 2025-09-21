#!/usr/bin/env python3
"""
Update .env file to disable internal strategies
"""

import os

def update_env_file():
    """Update .env file to disable internal strategies"""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update strategy settings
        updated_lines = []
        for line in lines:
            if line.startswith('ENABLE_RSI_STRATEGY='):
                updated_lines.append('ENABLE_RSI_STRATEGY=False\n')
            elif line.startswith('ENABLE_MA_STRATEGY='):
                updated_lines.append('ENABLE_MA_STRATEGY=False\n')
            elif line.startswith('ENABLE_BOLLINGER_STRATEGY='):
                updated_lines.append('ENABLE_BOLLINGER_STRATEGY=False\n')
            else:
                updated_lines.append(line)
        
        # Add Bollinger strategy if not present
        if not any(line.startswith('ENABLE_BOLLINGER_STRATEGY=') for line in lines):
            updated_lines.append('ENABLE_BOLLINGER_STRATEGY=False\n')
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
        
        print("✅ .env file updated successfully!")
        print("✅ All internal strategies disabled")
        print("✅ Bot will only execute Discord signals")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    update_env_file()
