#!/usr/bin/env python3
"""
Discord Login Helper
This script helps you login to Discord and get your token.
"""

import os
import sys
import webbrowser
import time

def main():
    print("🔐 Discord Login Helper")
    print("=" * 40)
    print()
    
    print("📋 This will help you login to Discord and get your token.")
    print()
    
    print("🎯 Step-by-Step Process:")
    print("1. Open Discord in your browser")
    print("2. Login with your username/password")
    print("3. Get your token automatically")
    print("4. Use it for the trading bot")
    print()
    
    # Get user credentials
    print("🔑 Enter your Discord credentials:")
    print("-" * 30)
    
    email = input("Discord Email: ").strip()
    if not email:
        print("❌ Email required!")
        return
    
    password = input("Discord Password: ").strip()
    if not password:
        print("❌ Password required!")
        return
    
    print("\n🌐 Opening Discord login page...")
    webbrowser.open("https://discord.com/login")
    
    print("\n📋 Instructions:")
    print("1. Discord login page opened in your browser")
    print("2. Login with your credentials:")
    print(f"   Email: {email}")
    print("   Password: [hidden]")
    print("3. After login, follow these steps:")
    print()
    print("🔧 To get your token:")
    print("1. Press F12 (Developer Tools)")
    print("2. Go to Console tab")
    print("3. Paste this code:")
    print()
    print("```javascript")
    print("window.webpackChunkdiscord_app.push([[Math.random()], {}, (req) => {for (const m of Object.keys(req.c).map((x) => req.c[x].exports).filter((x) => x)) {if (m.default && m.default.getToken !== undefined) {return copy(m.default.getToken())}if (m.getToken !== undefined) {return copy(m.getToken())}}}]); console.log('%cWorked!', 'font-size: 50px'); console.log(`%cYou now have your token in the clipboard!`, 'font-size: 16px')")
    print("```")
    print()
    print("4. Press Enter")
    print("5. Token will be copied to clipboard")
    print()
    
    print("🎯 After getting token:")
    print("1. Run: python simple_setup.py")
    print("2. Paste your token")
    print("3. Enter channel ID")
    print("4. Setup complete!")
    print()
    
    print("⏰ Waiting for you to login...")
    print("Press Enter when you have your token...")
    input()
    
    print("\n✅ Great! Now you can setup your bot:")
    print("1. Run: python simple_setup.py")
    print("2. Paste your token")
    print("3. Enter channel ID")
    print("4. Start trading!")

if __name__ == "__main__":
    main()
