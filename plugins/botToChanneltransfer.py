import asyncio
from pyrogram import Client, filters
from config import API_ID, API_HASH, STRING, OWNER_ID

# State dictionary to remember the user's request
# Format: {user_id: {"dest_chat": id, "start_msg_id": id}}
btc_states = {}

# --- STEP 1: User replies to a message with /botToChannel channel_id ---
@Client.on_message(filters.command("botToChannel") & filters.user(OWNER_ID))
async def ask_count(bot, message):
    # 1. Check if user replied to a message
    if not message.reply_to_message:
        await message.reply_text(
            "⚠️ **Incorrect Usage**\n\n"
            "1. Find the **first file** you want to send in our chat.\n"
            "2. **Reply** to that file with: `/botToChannel -100xxxxxxx`\n"
            "(Replace `-100xxxxxxx` with your Destination Channel ID)"
        )
        return

    # 2. Check if channel ID is provided
    try:
        dest_channel = int(message.command[1])
    except (IndexError, ValueError):
        await message.reply_text("❌ Please provide a valid Channel ID.\nExample: `/botToChannel -100123456789`")
        return

    # 3. Save the state (Destination and Starting ID)
    start_id = message.reply_to_message.id
    btc_states[message.from_user.id] = {
        "dest_chat": dest_channel,
        "start_msg_id": start_id
    }

    # 4. Ask for the quantity
    await message.reply_text(
        f"✅ **Starting Point Selected!** (Message ID: `{start_id}`)\n\n"
        "**How many files** do you want to transfer from here?\n"
        "_(Type a number, e.g., 10, 50, 100)_"
    )

# --- STEP 2: User sends the number ---
@Client.on_message(filters.user(OWNER_ID) & filters.regex(r"^\d+$"))
async def start_btc_transfer(bot, message):
    user_id = message.from_user.id
    
    # Check if this user has a pending request in OUR state list
    if user_id not in btc_states:
        return # Ignore random numbers if they didn't run /botToChannel

    state = btc_states[user_id]
    count = int(message.text)
    dest_chat = state["dest_chat"]
    start_id = state["start_msg_id"]
    
    # Clear state
    del btc_states[user_id]

    status_msg = await message.reply_text(f"🚀 **Processing /botToChannel...**\nTransfing {count} files to `{dest_chat}`\nStarting from ID: {start_id}")

    # Start the User Client (using STRING session)
    async with Client("btc_worker", api_id=API_ID, api_hash=API_HASH, session_string=STRING) as user_app:
        
        success = 0
        failed = 0
        
        # Get the bot's own username to read the correct chat
        bot_info = await bot.get_me()
        chat_target = bot_info.username 

        # Loop through the IDs sequentially
        for i in range(count):
            current_id = start_id + i 
            
            try:
                # Fetch the message
                msg = await user_app.get_messages(chat_target, current_id)
                
                # If message exists and has a file
                if msg and not msg.empty and (msg.document or msg.video or msg.photo or msg.audio):
                    # Copy to channel
                    await msg.copy(chat_id=dest_chat, caption=msg.caption)
                    success += 1
                    await asyncio.sleep(2) # Safety delay
                else:
                    pass

                # Update status every 10 files
                if i % 10 == 0:
                    await status_msg.edit_text(f"🔄 **Progress:** {i}/{count}\n✅ Copied: {success}")

            except Exception as e:
                print(f"Error on {current_id}: {e}")
                failed += 1
                await asyncio.sleep(2)

    await status_msg.edit_text(f"✅ **Task Completed!**\n\n🎯 Requested: {count}\n📂 Copied: {success}\n❌ Skipped/Failed: {failed}")
