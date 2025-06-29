from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetFullChannelRequest
from utils import translate_with_libretranslate
import asyncio

# === CONFIGURATION ===
api_id = '--' # Telegram API ID
api_hash = '--' # Telegram API Hash
phone_number = '--'  # Your phone number with country code (e.g., +1234567890)
target_channel = "--"
chat_ids =   ['chat links']
                    
             # List of chat IDs to monitor for new messages

# === END OF CONFIGURATION ===

# Initialize the client
client = TelegramClient('session_name', api_id, api_hash)

async def get_channel_name(chat_id):
    # Get full channel info
    full_channel = await client(GetFullChannelRequest(channel=chat_id))
    
    # The channel object is in .chats[0]
    channel = full_channel.chats[0]
    
    # The title is the name of the channel
    return channel.title

async def main():
    # Connect and authorize if needed
    await client.start(phone_number)
    print("Client created and connected!")

    @client.on(events.NewMessage(chats=chat_ids))
    async def handler(event):
        sender = await event.get_sender()
        
        if sender is None:
            sender_name = 'Unknown'
        elif hasattr(sender, 'username') and sender.username:
            sender_name = sender.username
        elif hasattr(sender, 'first_name') and sender.first_name:
            sender_name = sender.first_name
        elif hasattr(sender, 'title') and sender.title:
            # This handles the case where the sender is a channel or group
            sender_name = sender.title
        else:
            sender_name = 'Unknown'
        
        channel_name = await get_channel_name(event.chat_id)
        message_text = event.text
        
        # Translate
        print(f"New message from {sender_name} in chat {channel_name}")
        result = translate_with_libretranslate(message_text)
        if result:
            detected_lang = result["detected_language"]
            confidence = result["confidence"]
            translation = result["translation"]

            # Final message to send to target channel
            final_message = (
                f"🌐 **New Translated Message**\n\n"
                f"**Original Channel:** {channel_name}\n"
                f"**Sender:** {sender_name}\n\n"
                f"**Detected Language:** {detected_lang} (confidence: {confidence:.2f})\n\n"
                f"**Original Message:**\n{message_text}\n\n"
                f"**Translated to English:**\n{translation}"
            )
            print("✅ Translation successful!")
            print(f"Detected language: {detected_lang} (confidence: {confidence:.2f})")
            # Send to the target channel
            await client.send_message(target_channel, final_message, parse_mode="markdown")
            print(f"✅ Sent translated message to {target_channel}.")
            
        else:
            print("❌ Failed to translate or detect language. Sending original message.")
            # If translation fails, send the original message
            final_message = (
                f"🌐 **New Translated Message**\n\n"
                f"**Original Channel:** {channel_name}\n"
                f"**Sender:** {sender_name}\n\n"
                f"**Original Message:**\n{message_text}\n\n"
            )
            # Send to the target channel
            await client.send_message(target_channel, final_message, parse_mode="markdown")
            print(f"✅ Sent message to {target_channel}.")
            
    print("Listening for new messages...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())