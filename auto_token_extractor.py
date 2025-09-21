#!/usr/bin/env python3
"""
Automatic Discord Token Extractor
This script helps you automatically extract your Discord user token.
"""

import os
import sys
import json
import subprocess
import webbrowser
from datetime import datetime

def main():
    print("🔑 Automatic Discord Token Extractor")
    print("=" * 50)
    print()
    
    print("📋 This will help you get your Discord user token automatically.")
    print()
    
    print("🚀 Method 1: Browser Extension (Recommended)")
    print("-" * 40)
    print("1. Install 'Discord Token Extractor' browser extension")
    print("2. Login to Discord in your browser")
    print("3. Click the extension icon")
    print("4. Copy your token")
    print()
    
    print("🌐 Method 2: Browser Console")
    print("-" * 40)
    print("1. Open Discord in your web browser")
    print("2. Press F12 (Developer Tools)")
    print("3. Go to Console tab")
    print("4. Paste this code and press Enter:")
    print()
    print("```javascript")
    print("window.webpackChunkdiscord_app.push([[Math.random()], {}, (req) => {for (const m of Object.keys(req.c).map((x) => req.c[x].exports).filter((x) => x)) {if (m.default && m.default.getToken !== undefined) {return copy(m.default.getToken())}if (m.getToken !== undefined) {return copy(m.getToken())}}}]); console.log('%cWorked!', 'font-size: 50px'); console.log(`%cYou now have your token in the clipboard!`, 'font-size: 16px')")
    print("```")
    print()
    
    print("🔍 Method 3: Network Tab")
    print("-" * 40)
    print("1. Open Discord in your web browser")
    print("2. Press F12 (Developer Tools)")
    print("3. Go to Network tab")
    print("4. Send any message in Discord")
    print("5. Find request to 'discord.com/api'")
    print("6. Look for 'authorization' header")
    print("7. Copy the token value")
    print()
    
    print("📱 Method 4: Mobile App (Alternative)")
    print("-" * 40)
    print("1. Use Discord mobile app")
    print("2. Some mobile apps show token in settings")
    print("3. Check app settings for 'Token' or 'API Key'")
    print()
    
    # Ask user which method they want to try
    print("🎯 Which method would you like to try?")
    print("1. Browser Console (Easiest)")
    print("2. Network Tab")
    print("3. I'll do it manually")
    print("4. Open Discord in browser")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🌐 Opening Discord in your browser...")
        webbrowser.open("https://discord.com/app")
        print("\n📋 Instructions:")
        print("1. Login to Discord")
        print("2. Press F12")
        print("3. Go to Console tab")
        print("4. Paste the JavaScript code above")
        print("5. Press Enter")
        print("6. Token will be copied to clipboard")
        
    elif choice == "2":
        print("\n🌐 Opening Discord in your browser...")
        webbrowser.open("https://discord.com/app")
        print("\n📋 Instructions:")
        print("1. Login to Discord")
        print("2. Press F12")
        print("3. Go to Network tab")
        print("4. Send any message")
        print("5. Find 'discord.com/api' request")
        print("6. Look for 'authorization' header")
        print("7. Copy the token value")
        
    elif choice == "3":
        print("\n📋 Manual Method:")
        print("1. Open Discord in web browser")
        print("2. Press F12")
        print("3. Go to Application tab")
        print("4. Local Storage → discord.com")
        print("5. Find 'token' key")
        print("6. Copy the value")
        
    elif choice == "4":
        print("\n🌐 Opening Discord in your browser...")
        webbrowser.open("https://discord.com/app")
        print("\n✅ Discord opened in your browser!")
        print("Now follow any of the methods above to get your token.")
        
    else:
        print("❌ Invalid choice!")
        return
    
    print("\n" + "="*50)
    print("🔧 After getting your token:")
    print("1. Run: python simple_setup.py")
    print("2. Paste your token")
    print("3. Enter channel ID")
    print("4. Setup complete!")
    print()
    print("⚠️  Remember:")
    print("- Never share your token")
    print("- Keep it secure")
    print("- Use only for personal trading")

if __name__ == "__main__":
    main()
