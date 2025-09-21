#!/usr/bin/env python3
"""
Verify Discord Bot Setup
This script verifies all aspects of the Discord bot configuration.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
import discord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_discord_setup():
    """Verify Discord bot setup and permissions"""
    print("🔍 Verifying Discord Bot Setup")
    print("=" * 50)
    
    try:
        # Check configuration
        print("⚙️  Configuration Check:")
        print(f"   Discord Token: {'✅ Set' if Config.DISCORD_TOKEN else '❌ Not Set'}")
        print(f"   Channel ID: {Config.DISCORD_CHANNEL_ID}")
        print()
        
        if not Config.DISCORD_TOKEN:
            print("❌ Discord token not set!")
            return False
        
        # Create Discord client with basic intents only
        intents = discord.Intents.default()
        intents.message_content = False  # Don't require privileged intents
        client = discord.Client(intents=intents)
        
        @client.event
        async def on_ready():
            print(f"✅ Bot logged in as: {client.user}")
            print(f"✅ Bot ID: {client.user.id}")
            print()
            
            # Check if bot can access the channel
            try:
                channel = client.get_channel(int(Config.DISCORD_CHANNEL_ID))
                if channel:
                    print(f"✅ Channel found: #{channel.name}")
                    print(f"   Channel ID: {channel.id}")
                    print(f"   Channel Type: {channel.type}")
                    print(f"   Guild: {channel.guild.name if channel.guild else 'DM'}")
                    
                    # Check permissions
                    bot_member = channel.guild.get_member(client.user.id) if channel.guild else None
                    if bot_member:
                        permissions = channel.permissions_for(bot_member)
                        print(f"   Read Messages: {'✅' if permissions.read_messages else '❌'}")
                        print(f"   Send Messages: {'✅' if permissions.send_messages else '❌'}")
                        print(f"   Read Message History: {'✅' if permissions.read_message_history else '❌'}")
                        
                        if not permissions.read_messages:
                            print("❌ Bot cannot read messages in this channel!")
                            return
                        if not permissions.read_message_history:
                            print("❌ Bot cannot read message history!")
                            return
                    
                    print("✅ Bot has proper permissions")
                    
                    # Try to send a test message
                    try:
                        test_message = await channel.send("🤖 Discord bot is working! Send trading signals in this format:\n`BUY EUR_USD @ 1.1000 SL: 1.0950 TP: 1.1100`")
                        print("✅ Test message sent successfully")
                        print(f"   Message ID: {test_message.id}")
                    except Exception as e:
                        print(f"❌ Cannot send messages: {e}")
                    
                else:
                    print(f"❌ Channel not found! ID: {Config.DISCORD_CHANNEL_ID}")
                    print("   Possible issues:")
                    print("   - Channel ID is incorrect")
                    print("   - Bot is not in the server")
                    print("   - Channel is private and bot doesn't have access")
                    
            except Exception as e:
                print(f"❌ Error checking channel: {e}")
        
        @client.event
        async def on_message(message):
            if message.channel.id == int(Config.DISCORD_CHANNEL_ID) and not message.author.bot:
                print(f"📨 Message received from {message.author}: {message.content[:100]}...")
                print(f"   Message ID: {message.id}")
                print(f"   Channel: #{message.channel.name}")
                print(f"   Timestamp: {message.created_at}")
        
        print("🔄 Starting Discord bot...")
        print("📝 Send a test message to your Discord channel now!")
        print("   The bot will show if it receives your message")
        print("⏰ Bot will run for 30 seconds...")
        
        # Run bot for 30 seconds
        try:
            await asyncio.wait_for(client.start(Config.DISCORD_TOKEN), timeout=30.0)
        except asyncio.TimeoutError:
            print("\n⏰ 30 seconds elapsed. Stopping bot.")
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user.")
        
        await client.close()
        print("✅ Discord bot stopped successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Error verifying Discord setup: {e}")
        return False

def main():
    """Main function"""
    try:
        result = asyncio.run(verify_discord_setup())
        if result:
            print("\n🎉 Discord bot setup verification completed!")
        else:
            print("\n❌ Discord bot setup verification failed!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
