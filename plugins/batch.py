# # Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# # Licensed under the GNU General Public License v3.0.  
# # See LICENSE file in the repository root for full license text.

# import os, re, time, asyncio, json
# from pyrogram import Client, filters
# from pyrogram.types import Message
# from pyrogram.errors import UserNotParticipant, FloodWait, PeerIdInvalid, ChannelPrivate
# from config import API_ID, API_HASH, LOG_GROUP, STRING, FORCE_SUB, FREEMIUM_LIMIT, PREMIUM_LIMIT
# from utils.func import get_user_data, screenshot, thumbnail, get_video_metadata
# from utils.func import get_user_data_key, process_text_with_rules, is_premium_user, E
# from shared_client import app as X
# from plugins.settings import rename_file
# from plugins.start import subscribe as sub
# from utils.custom_filters import login_in_progress
# from utils.encrypt import dcs
# from typing import Dict, Any, Optional

# Y = None if not STRING else __import__('shared_client').userbot
# Z, P, UB, UC = {}, {}, {}, {}

# ACTIVE_USERS = {}
# ACTIVE_USERS_FILE = "active_users.json"

# def sanitize(filename):
#     return re.sub(r'[<>:"/\\|?*\']', '_', filename).strip(" .")[:255]

# def load_active_users():
#     try:
#         if os.path.exists(ACTIVE_USERS_FILE):
#             with open(ACTIVE_USERS_FILE, 'r') as f:
#                 return json.load(f)
#         return {}
#     except Exception:
#         return {}

# async def save_active_users_to_file():
#     try:
#         with open(ACTIVE_USERS_FILE, 'w') as f:
#             json.dump(ACTIVE_USERS, f)
#     except Exception as e:
#         print(f"Error saving active users: {e}")

# async def add_active_batch(user_id: int, batch_info: Dict[str, Any]):
#     ACTIVE_USERS[str(user_id)] = batch_info
#     await save_active_users_to_file()

# def is_user_active(user_id: int) -> bool:
#     return str(user_id) in ACTIVE_USERS

# async def update_batch_progress(user_id: int, current: int, success: int):
#     if str(user_id) in ACTIVE_USERS:
#         ACTIVE_USERS[str(user_id)]["current"] = current
#         ACTIVE_USERS[str(user_id)]["success"] = success
#         await save_active_users_to_file()

# async def request_batch_cancel(user_id: int):
#     if str(user_id) in ACTIVE_USERS:
#         ACTIVE_USERS[str(user_id)]["cancel_requested"] = True
#         await save_active_users_to_file()
#         return True
#     return False

# def should_cancel(user_id: int) -> bool:
#     user_str = str(user_id)
#     return user_str in ACTIVE_USERS and ACTIVE_USERS[user_str].get("cancel_requested", False)

# async def remove_active_batch(user_id: int):
#     if str(user_id) in ACTIVE_USERS:
#         del ACTIVE_USERS[str(user_id)]
#         await save_active_users_to_file()

# def get_batch_info(user_id: int) -> Optional[Dict[str, Any]]:
#     return ACTIVE_USERS.get(str(user_id))

# ACTIVE_USERS = load_active_users()

# async def upd_dlg(c):
#     try:
#         # Optimized limit to prevent timeouts
#         async for _ in c.get_dialogs(limit=2000): pass
#         return True
#     except Exception as e:
#         print(f'Failed to update dialogs: {e}')
#         return False

# # ==============================================================================
# #  SMART MESSAGE FETCHER (PUBLIC & PRIVATE)
# # ==============================================================================
# async def get_msg(c, u, i, d, lt):
#     try:
#         # ----------------------
#         # PUBLIC CHANNELS
#         # ----------------------
#         if lt == 'public':
#             # 1. Try with BOT Client (c) first (Fastest/Safest)
#             try:
#                 msg = await c.get_messages(i, d)
#                 if not getattr(msg, "empty", False):
#                     return msg
#             except Exception:
#                 pass

#             # 2. Try with USERBOT (u)
#             if u:
#                 try:
#                     msg = await u.get_messages(i, d)
#                     if not getattr(msg, "empty", False):
#                         return msg
#                 except Exception:
#                     pass

#                 # 3. Join and Retry (Userbot)
#                 try:
#                     # print(f"Joining public chat {i}...")
#                     await u.join_chat(i)
#                     await asyncio.sleep(2) # Wait for join to propagate
#                     msg = await u.get_messages(i, d)
#                     if not getattr(msg, "empty", False):
#                         return msg
#                 except Exception:
#                     pass

#             return None

#         # ----------------------
#         # PRIVATE CHANNELS
#         # ----------------------
#         else:
#             if u:
#                 # 1. ID Normalization
#                 try:
#                     chat_id = int(i)
#                     if str(chat_id).startswith("-100"):
#                         final_id = chat_id
#                     elif str(chat_id).startswith("-"):
#                         final_id = int(f"-100{str(chat_id)[1:]}")
#                     else:
#                         final_id = int(f"-100{chat_id}")
#                 except ValueError:
#                     print(f"Invalid ID format: {i}")
#                     return None

#                 # 2. Attempt Direct Fetch
#                 try:
#                     msg = await u.get_messages(final_id, d)
#                     if not getattr(msg, "empty", False):
#                         return msg
#                 except Exception:
#                     pass

#                 # 3. Attempt Cache Refresh via get_chat
#                 try:
#                     await u.get_chat(final_id)
#                     msg = await u.get_messages(final_id, d)
#                     if not getattr(msg, "empty", False):
#                         return msg
#                 except Exception:
#                     pass

#                 # 4. Attempt Dialog Scan (Limit 2000)
#                 try:
#                     found = False
#                     async for dialog in u.get_dialogs(limit=2000):
#                         if dialog.chat.id == final_id:
#                             found = True
#                             break 
                    
#                     if found:
#                         msg = await u.get_messages(final_id, d)
#                         if not getattr(msg, "empty", False):
#                             return msg
#                 except Exception:
#                     pass

#                 return None
#             return None

#     except Exception as e:
#         print(f'Critical Error in get_msg: {e}')
#         return None

# # ==============================================================================
# #  ROBUST BOT STARTER (FIX FOR "ADD BOT FIRST" ERROR)
# # ==============================================================================
# async def get_ubot(uid):
#     # 1. Check Cache
#     if uid in UB:
#         return UB[uid]
    
#     # 2. Check Database
#     bt = await get_user_data_key(uid, "bot_token", None)
#     if not bt:
#         return None
    
#     # 3. Start Bot (With Auto-Cleanup)
#     try:
#         bot = Client(f"user_{uid}", bot_token=bt, api_id=API_ID, api_hash=API_HASH)
#         await bot.start()
#         UB[uid] = bot
#         return bot
#     except Exception as e:
#         # If session file is corrupted/locked, delete and retry ONCE
#         print(f"Error starting bot for {uid}: {e}. Retrying...")
#         try:
#             if os.path.exists(f"user_{uid}.session"):
#                 os.remove(f"user_{uid}.session")
            
#             bot = Client(f"user_{uid}", bot_token=bt, api_id=API_ID, api_hash=API_HASH)
#             await bot.start()
#             UB[uid] = bot
#             return bot
#         except Exception as e2:
#             print(f"Final Error starting bot for {uid}: {e2}")
#             return None

# async def get_uclient(uid):
#     ud = await get_user_data(uid)
#     ubot = UB.get(uid)
#     cl = UC.get(uid)
#     if cl: return cl
#     if not ud: return ubot if ubot else None
#     xxx = ud.get('session_string')
#     if xxx:
#         try:
#             ss = dcs(xxx)
#             gg = Client(f'{uid}_client', api_id=API_ID, api_hash=API_HASH, device_model="v3saver", session_string=ss)
#             await gg.start()
#             await upd_dlg(gg)
#             UC[uid] = gg
#             return gg
#         except Exception as e:
#             print(f'User client error: {e}')
#             return ubot if ubot else Y
#     return Y

# async def prog(c, t, C, h, m, st, ud_type):
#     global P
#     now = time.time()
#     p = c / t * 100
#     interval = 25 if ud_type == "Downloading" else 6
#     if m in P and (now - P[m]) < interval and p < 100:
#         return
#     P[m] = now
#     c_mb = c / (1024 * 1024)
#     t_mb = t / (1024 * 1024)
#     bar = '🟢' * int(p / 10) + '🔴' * (10 - int(p / 10))
#     speed = c / (now - st) / (1024 * 1024) if now > st else 0
#     eta = time.strftime('%M:%S', time.gmtime((t - c) / (speed * 1024 * 1024))) if speed > 0 else '00:00'
#     icon = "📥" if ud_type == "Downloading" else "📤"
#     try:
#         await C.edit_message_text(
#             h, m, 
#             f"**{icon} {ud_type}...**\n\n{bar}\n\n⚡**__Completed__**: {c_mb:.2f} MB / {t_mb:.2f} MB\n📊 **__Done__**: {p:.2f}%\n🚀 **__Speed__**: {speed:.2f} MB/s\n⏳ **__ETA__**: {eta}\n\n**__Powered by Team SPY__**"
#         )
#     except FloodWait as e:
#         await asyncio.sleep(e.value)
#     except Exception:
#         pass 
#     if p >= 100: P.pop(m, None)

# async def send_direct(c, m, tcid, ft=None, rtmid=None):
#     try:
#         if m.video:
#             await c.send_video(tcid, m.video.file_id, caption=ft, duration=m.video.duration, width=m.video.width, height=m.video.height, reply_to_message_id=rtmid)
#         elif m.video_note:
#             await c.send_video_note(tcid, m.video_note.file_id, reply_to_message_id=rtmid)
#         elif m.voice:
#             await c.send_voice(tcid, m.voice.file_id, reply_to_message_id=rtmid)
#         elif m.sticker:
#             await c.send_sticker(tcid, m.sticker.file_id, reply_to_message_id=rtmid)
#         elif m.audio:
#             await c.send_audio(tcid, m.audio.file_id, caption=ft, duration=m.audio.duration, performer=m.audio.performer, title=m.audio.title, reply_to_message_id=rtmid)
#         elif m.photo:
#             photo_id = m.photo.file_id if hasattr(m.photo, 'file_id') else m.photo[-1].file_id
#             await c.send_photo(tcid, photo_id, caption=ft, reply_to_message_id=rtmid)
#         elif m.document:
#             await c.send_document(tcid, m.document.file_id, caption=ft, file_name=m.document.file_name, reply_to_message_id=rtmid)
#         else:
#             return False
#         return True
#     except Exception as e:
#         print(f'Direct send error: {e}')
#         return False

# async def process_msg(c, u, m, d, lt, uid, i):
#     try:
#         cfg_chat = await get_user_data_key(d, 'chat_id', None)
#         tcid = d
#         rtmid = None
#         if cfg_chat:
#             if '/' in cfg_chat:
#                 parts = cfg_chat.split('/', 1)
#                 tcid = int(parts[0])
#                 rtmid = int(parts[1]) if len(parts) > 1 else None
#             else:
#                 tcid = int(cfg_chat)
        
#         if m.media:
#             orig_text = m.caption.markdown if m.caption else ''
#             proc_text = await process_text_with_rules(d, orig_text)
#             user_cap = await get_user_data_key(d, 'caption', '')
#             ft = f'{proc_text}\n\n{user_cap}' if proc_text and user_cap else user_cap if user_cap else proc_text
            
#             # PUBLIC CLONING LOGIC
#             if lt == 'public':
#                 sent = await send_direct(c, m, tcid, ft, rtmid)
#                 if sent:
#                     return 'Sent directly.'
            
#             st = time.time()
#             p = await c.send_message(d, 'Downloading...')

#             video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'}
#             is_real_video = False
#             c_name = f"{time.time()}"

#             if m.video:
#                 is_real_video = True
#                 if m.video.file_name:
#                     _, ext = os.path.splitext(m.video.file_name)
#                     c_name = sanitize(f"{time.time()}{ext}")
#                 else:
#                     c_name = sanitize(f"{time.time()}.mp4")
#             elif m.document:
#                 if m.document.file_name:
#                     _, ext = os.path.splitext(m.document.file_name)
#                     if ext.lower() in video_extensions:
#                         is_real_video = True
#                     c_name = sanitize(f"{time.time()}{ext}")
#                 else:
#                     c_name = sanitize(f"{time.time()}.bin")
#             elif m.audio:
#                 if m.audio.file_name:
#                     _, ext = os.path.splitext(m.audio.file_name)
#                     c_name = sanitize(f"{time.time()}{ext}")
#                 else:
#                     c_name = sanitize(f"{time.time()}.mp3")
#             elif m.photo:
#                 c_name = sanitize(f"{time.time()}.jpg")
    
#             f = await u.download_media(
#                 m, 
#                 file_name=c_name, 
#                 progress=prog, 
#                 progress_args=(c, d, p.id, st, 'Downloading') 
#             )
            
#             if not f:
#                 await c.edit_message_text(d, p.id, 'Failed.')
#                 return 'Failed.'
            
#             if os.path.exists(f) and os.path.getsize(f) == 0:
#                 os.remove(f)
#                 await c.edit_message_text(d, p.id, 'Failed: 0KB File.')
#                 return 'Failed: Disk Full.'

#             if (
#                 (m.video and m.video.file_name) or
#                 (m.audio and m.audio.file_name) or
#                 (m.document and m.document.file_name)
#             ):
#                 f = await rename_file(f, d, p)
            
#             fsize = os.path.getsize(f) / (1024 * 1024 * 1024)
#             th = thumbnail(d)
#             generated_thumb = None

#             async def cleanup():
#                 if os.path.exists(f): os.remove(f)
#                 if generated_thumb and os.path.exists(generated_thumb): os.remove(generated_thumb)
#                 await c.delete_messages(d, p.id)

#             if fsize > 2 and Y:
#                 st = time.time()
#                 await upd_dlg(Y)
#                 try:
#                     dur, h, w = 0, 0, 0
#                     if is_real_video:
#                         try:
#                             mtd = await get_video_metadata(f)
#                             dur, h, w = mtd['duration'], mtd['width'], mtd['height']
#                             generated_thumb = await screenshot(f, dur, d)
#                             th = generated_thumb
#                         except Exception:
#                             pass

#                     upload_args = {'progress': prog, 'progress_args': (c, d, p.id, st, 'Uploading')} 

#                     if not is_real_video:
#                          sent = await Y.send_document(LOG_GROUP, f, thumb=th, caption=ft if m.caption else None,
#                                                     reply_to_message_id=rtmid, **upload_args)
#                     else:
#                         send_funcs = {'video': Y.send_video, 'video_note': Y.send_video_note, 
#                                     'voice': Y.send_voice, 'audio': Y.send_audio, 
#                                     'photo': Y.send_photo, 'document': Y.send_document}
                        
#                         for mtype, func in send_funcs.items():
#                             if f.lower().endswith(tuple(video_extensions)): mtype = 'video'
#                             if getattr(m, mtype, None):
#                                 sent = await func(LOG_GROUP, f, thumb=th if mtype == 'video' else None, 
#                                                 duration=dur if mtype == 'video' else None,
#                                                 height=h if mtype == 'video' else None,
#                                                 width=w if mtype == 'video' else None,
#                                                 caption=ft if m.caption and mtype not in ['video_note', 'voice'] else None, 
#                                                 reply_to_message_id=rtmid, **upload_args)
#                                 break
#                         else:
#                             sent = await Y.send_document(LOG_GROUP, f, thumb=th, caption=ft if m.caption else None,
#                                                         reply_to_message_id=rtmid, **upload_args)
                    
#                     await c.copy_message(d, LOG_GROUP, sent.id)
#                 except Exception as e:
#                     await c.edit_message_text(d, p.id, f'Error: {str(e)[:30]}')
#                     await cleanup()
#                     return 'Failed.'
                
#                 await cleanup()
#                 return 'Done (Large file).'
            
#             st = time.time()
#             try:
#                 uploaded = False
#                 upload_args = {'progress': prog, 'progress_args': (c, d, p.id, st, 'Uploading')} 

#                 if is_real_video and (m.video or (m.document and os.path.splitext(f)[1].lower() in video_extensions)):
#                     try:
#                         mtd = await get_video_metadata(f)
#                         dur, h, w = mtd['duration'], mtd['width'], mtd['height']
#                         generated_thumb = await screenshot(f, dur, d)
#                         th = generated_thumb
                        
#                         await c.send_video(tcid, video=f, caption=ft if m.caption else None, 
#                                         thumb=th, width=w, height=h, duration=dur, 
#                                         reply_to_message_id=rtmid, **upload_args)
#                         uploaded = True
#                     except Exception:
#                         uploaded = False

#                 if not uploaded:
#                     if m.video_note and is_real_video:
#                         await c.send_video_note(tcid, video_note=f, reply_to_message_id=rtmid, **upload_args)
#                     elif m.voice:
#                         await c.send_voice(tcid, f, reply_to_message_id=rtmid, **upload_args)
#                     elif m.sticker:
#                         await c.send_sticker(tcid, m.sticker.file_id, reply_to_message_id=rtmid)
#                     elif m.audio:
#                          await c.send_audio(tcid, audio=f, caption=ft if m.caption else None, 
#                                         thumb=th, reply_to_message_id=rtmid, **upload_args)
#                     elif m.photo:
#                         await c.send_photo(tcid, photo=f, caption=ft if m.caption else None, 
#                                         reply_to_message_id=rtmid, **upload_args)
#                     else:
#                         await c.send_document(tcid, document=f, caption=ft if m.caption else None, 
#                                             reply_to_message_id=rtmid, **upload_args)
#             except Exception as e:
#                 await c.edit_message_text(d, p.id, f'Error: {str(e)[:30]}')
#                 await cleanup()
#                 return 'Failed.'
            
#             await cleanup()
#             return 'Done.'
            
#         elif m.text:
#             await c.send_message(tcid, text=m.text.markdown, reply_to_message_id=rtmid)
#             return 'Sent.'
#     except Exception as e:
#         return f'Error: {str(e)[:50]}'
        
# @X.on_message(filters.command(['batch', 'single']))
# async def process_cmd(c, m):
#     uid = m.from_user.id
#     cmd = m.command[0]
    
#     if FREEMIUM_LIMIT == 0 and not await is_premium_user(uid):
#         await m.reply_text("This bot does not provide free servies, get subscription from OWNER")
#         return
    
#     if await sub(c, m) == 1: return
#     pro = await m.reply_text('Doing some checks hold on...')
    
#     if is_user_active(uid):
#         await pro.edit('You have an active task. Use /stop to cancel it.')
#         return
    
#     # DB Check + Smart Start
#     ubot = await get_ubot(uid)
    
#     # If still None after retry logic, it means critical failure (Invalid Token or Ban)
#     if not ubot:
#         await pro.edit('**Bot failed to start.**\nPossible reasons:\n1. Invalid Token (/setbot again)\n2. Telegram FloodWait (Try later)\n3. Account Banned')
#         return
    
#     Z[uid] = {'step': 'start' if cmd == 'batch' else 'start_single'}
#     await pro.edit(f'Send {"start link..." if cmd == "batch" else "link you to process"}.')

# @X.on_message(filters.command(['cancel', 'stop']))
# async def cancel_cmd(c, m):
#     uid = m.from_user.id
#     if is_user_active(uid):
#         if await request_batch_cancel(uid):
#             await m.reply_text('Cancellation requested. The current batch will stop after the current download completes.')
#         else:
#             await m.reply_text('Failed to request cancellation. Please try again.')
#     else:
#         await m.reply_text('No active batch process found.')

# @X.on_message(filters.text & filters.private & ~login_in_progress & ~filters.command([
#     'start', 'batch', 'cancel', 'login', 'logout', 'stop', 'set', 
#     'pay', 'redeem', 'gencode', 'single', 'generate', 'keyinfo', 'encrypt', 'decrypt', 'keys', 'setbot', 'rembot']))
# async def text_handler(c, m):
#     uid = m.from_user.id
#     if uid not in Z: return
#     s = Z[uid].get('step')
    
#     # DB Check + Smart Start
#     x = await get_ubot(uid)
#     if not x:
#         await m.reply_text('**Bot failed to start.**\nPossible reasons:\n1. Invalid Token (/setbot again)\n2. Telegram FloodWait (Try later)\n3. Account Banned')
#         return

#     if s == 'start':
#         L = m.text
#         i, d, lt = E(L)
#         if not i or not d:
#             await m.reply_text('Invalid link format.')
#             Z.pop(uid, None)
#             return
#         Z[uid].update({'step': 'count', 'cid': i, 'sid': d, 'lt': lt})
#         await m.reply_text('How many messages?')

#     elif s == 'start_single':
#         L = m.text
#         i, d, lt = E(L)
#         if not i or not d:
#             await m.reply_text('Invalid link format.')
#             Z.pop(uid, None)
#             return

#         Z[uid].update({'step': 'process_single', 'cid': i, 'sid': d, 'lt': lt})
#         i, s, lt = Z[uid]['cid'], Z[uid]['sid'], Z[uid]['lt']
#         pt = await m.reply_text('Processing...')
        
#         ubot = await get_ubot(uid)
        
#         uc = await get_uclient(uid)
#         if not uc:
#             await pt.edit('Cannot proceed without user client.')
#             Z.pop(uid, None)
#             return
            
#         if is_user_active(uid):
#             await pt.edit('Active task exists. Use /stop first.')
#             Z.pop(uid, None)
#             return

#         try:
#             msg = await get_msg(ubot, uc, i, s, lt)
#             if msg:
#                 res = await process_msg(ubot, uc, msg, str(m.chat.id), lt, uid, i)
#                 await pt.edit(f'1/1: {res}')
#             else:
#                 await pt.edit('Message not found')
#         except Exception as e:
#             await pt.edit(f'Error: {str(e)[:50]}')
#         finally:
#             Z.pop(uid, None)

#     elif s == 'count':
#         if not m.text.isdigit():
#             await m.reply_text('Enter valid number.')
#             return
        
#         count = int(m.text)
#         maxlimit = PREMIUM_LIMIT if await is_premium_user(uid) else FREEMIUM_LIMIT

#         if count > maxlimit:
#             await m.reply_text(f'Maximum limit is {maxlimit}.')
#             return

#         Z[uid].update({'step': 'process', 'did': str(m.chat.id), 'num': count})
#         i, s, n, lt = Z[uid]['cid'], Z[uid]['sid'], Z[uid]['num'], Z[uid]['lt']
#         success = 0

#         pt = await m.reply_text('Processing batch...')
#         uc = await get_uclient(uid)
#         ubot = await get_ubot(uid)
        
#         if not uc or not ubot:
#             await pt.edit('Missing client setup')
#             Z.pop(uid, None)
#             return
            
#         if is_user_active(uid):
#             await pt.edit('Active task exists')
#             Z.pop(uid, None)
#             return
        
#         await add_active_batch(uid, {
#             "total": n,
#             "current": 0,
#             "success": 0,
#             "cancel_requested": False,
#             "progress_message_id": pt.id
#             })
        
#         try:
#             for j in range(n):
                
#                 if should_cancel(uid):
#                     await pt.edit(f'Cancelled at {j}/{n}. Success: {success}')
#                     break
                
#                 await update_batch_progress(uid, j, success)
                
#                 mid = int(s) + j
                
#                 try:
#                     msg = await get_msg(ubot, uc, i, mid, lt)
#                     if msg:
#                         res = await process_msg(ubot, uc, msg, str(m.chat.id), lt, uid, i)
#                         if 'Done' in res or 'Copied' in res or 'Sent' in res:
#                             success += 1
#                     else:
#                         pass
#                 except Exception as e:
#                     try: await pt.edit(f'{j+1}/{n}: Error - {str(e)[:30]}')
#                     except: pass
                
#                 await asyncio.sleep(6) # Retained 6s delay
            
#             if j+1 == n:
#                 await m.reply_text(f'Batch Completed ✅ Success: {success}/{n}')
        
#         finally:
#             await remove_active_batch(uid)
#             Z.pop(uid, None)




















# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os, re, time, asyncio, json
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserNotParticipant, FloodWait, PeerIdInvalid, ChannelPrivate
from config import API_ID, API_HASH, LOG_GROUP, STRING, FORCE_SUB, FREEMIUM_LIMIT, PREMIUM_LIMIT
from utils.func import get_user_data, screenshot, thumbnail, get_video_metadata
from utils.func import get_user_data_key, process_text_with_rules, is_premium_user, E
from shared_client import app as X
from plugins.settings import rename_file
from plugins.start import subscribe as sub
from utils.custom_filters import login_in_progress
from utils.encrypt import dcs
from typing import Dict, Any, Optional

Y = None if not STRING else __import__('shared_client').userbot
Z, P, UB, UC = {}, {}, {}, {}

# Removed 'emp' cache as it was causing logic errors. 
# We will rely on direct try/except blocks.

ACTIVE_USERS = {}
ACTIVE_USERS_FILE = "active_users.json"

def sanitize(filename):
    return re.sub(r'[<>:"/\\|?*\']', '_', filename).strip(" .")[:255]

def load_active_users():
    try:
        if os.path.exists(ACTIVE_USERS_FILE):
            with open(ACTIVE_USERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

async def save_active_users_to_file():
    try:
        with open(ACTIVE_USERS_FILE, 'w') as f:
            json.dump(ACTIVE_USERS, f)
    except Exception as e:
        print(f"Error saving active users: {e}")

async def add_active_batch(user_id: int, batch_info: Dict[str, Any]):
    ACTIVE_USERS[str(user_id)] = batch_info
    await save_active_users_to_file()

def is_user_active(user_id: int) -> bool:
    return str(user_id) in ACTIVE_USERS

async def update_batch_progress(user_id: int, current: int, success: int):
    if str(user_id) in ACTIVE_USERS:
        ACTIVE_USERS[str(user_id)]["current"] = current
        ACTIVE_USERS[str(user_id)]["success"] = success
        await save_active_users_to_file()

async def request_batch_cancel(user_id: int):
    if str(user_id) in ACTIVE_USERS:
        ACTIVE_USERS[str(user_id)]["cancel_requested"] = True
        await save_active_users_to_file()
        return True
    return False

def should_cancel(user_id: int) -> bool:
    user_str = str(user_id)
    return user_str in ACTIVE_USERS and ACTIVE_USERS[user_str].get("cancel_requested", False)

async def remove_active_batch(user_id: int):
    if str(user_id) in ACTIVE_USERS:
        del ACTIVE_USERS[str(user_id)]
        await save_active_users_to_file()

def get_batch_info(user_id: int) -> Optional[Dict[str, Any]]:
    return ACTIVE_USERS.get(str(user_id))

ACTIVE_USERS = load_active_users()

async def upd_dlg(c):
    try:
        # Changed to limit=None to scan ALL dialogs (Unlimited) as requested
        # This fixes issues where the channel is buried deep in the list.
        async for _ in c.get_dialogs(limit=None): pass
        return True
    except Exception as e:
        print(f'Failed to update dialogs: {e}')
        return False

# ==============================================================================
#  SMART MESSAGE FETCHER (PUBLIC & PRIVATE)
# ==============================================================================
async def get_msg(c, u, i, d, lt):
    try:
        # ----------------------
        # PUBLIC CHANNELS
        # ----------------------
        if lt == 'public':
            # 1. Try with BOT Client (c) first (Fastest/Safest)
            try:
                msg = await c.get_messages(i, d)
                if not getattr(msg, "empty", False):
                    return msg
            except Exception:
                pass

            # 2. Try with USERBOT (u)
            if u:
                try:
                    msg = await u.get_messages(i, d)
                    if not getattr(msg, "empty", False):
                        return msg
                except Exception:
                    pass

                # 3. Join and Retry (Userbot)
                try:
                    # print(f"Joining public chat {i}...")
                    await u.join_chat(i)
                    await asyncio.sleep(2) # Wait for join to propagate
                    msg = await u.get_messages(i, d)
                    if not getattr(msg, "empty", False):
                        return msg
                except Exception:
                    pass

            return None

        # ----------------------
        # PRIVATE CHANNELS
        # ----------------------
        else:
            if u:
                # 1. ID Normalization
                try:
                    chat_id = int(i)
                    if str(chat_id).startswith("-100"):
                        final_id = chat_id
                    elif str(chat_id).startswith("-"):
                        final_id = int(f"-100{str(chat_id)[1:]}")
                    else:
                        final_id = int(f"-100{chat_id}")
                except ValueError:
                    print(f"Invalid ID format: {i}")
                    return None

                # 2. Attempt Direct Fetch
                try:
                    msg = await u.get_messages(final_id, d)
                    if not getattr(msg, "empty", False):
                        return msg
                except Exception:
                    pass

                # 3. Attempt Cache Refresh via get_chat
                try:
                    await u.get_chat(final_id)
                    msg = await u.get_messages(final_id, d)
                    if not getattr(msg, "empty", False):
                        return msg
                except Exception:
                    pass

                # 4. Attempt Dialog Scan (Limit=None for UNLIMITED scan)
                try:
                    print(f"Scanning ALL dialogs for {final_id}...")
                    found = False
                    # Changed limit to None to scan infinite/max chats
                    async for dialog in u.get_dialogs(limit=None):
                        if dialog.chat.id == final_id:
                            found = True
                            break 
                    
                    if found:
                        msg = await u.get_messages(final_id, d)
                        if not getattr(msg, "empty", False):
                            return msg
                except Exception:
                    pass

                return None
            return None

    except Exception as e:
        print(f'Critical Error in get_msg: {e}')
        return None

# ==============================================================================
#  ROBUST BOT STARTER (FIX FOR "ADD BOT FIRST" ERROR)
# ==============================================================================
async def get_ubot(uid):
    # 1. Check Cache
    if uid in UB:
        return UB[uid]
    
    # 2. Check Database
    bt = await get_user_data_key(uid, "bot_token", None)
    if not bt:
        return None
    
    # 3. Start Bot (With Auto-Cleanup)
    try:
        bot = Client(f"user_{uid}", bot_token=bt, api_id=API_ID, api_hash=API_HASH)
        await bot.start()
        UB[uid] = bot
        return bot
    except Exception as e:
        # If session file is corrupted/locked, delete and retry ONCE
        print(f"Error starting bot for {uid}: {e}. Retrying...")
        try:
            if os.path.exists(f"user_{uid}.session"):
                os.remove(f"user_{uid}.session")
            
            bot = Client(f"user_{uid}", bot_token=bt, api_id=API_ID, api_hash=API_HASH)
            await bot.start()
            UB[uid] = bot
            return bot
        except Exception as e2:
            print(f"Final Error starting bot for {uid}: {e2}")
            return None

async def get_uclient(uid):
    ud = await get_user_data(uid)
    ubot = UB.get(uid)
    cl = UC.get(uid)
    if cl: return cl
    if not ud: return ubot if ubot else None
    xxx = ud.get('session_string')
    if xxx:
        try:
            ss = dcs(xxx)
            gg = Client(f'{uid}_client', api_id=API_ID, api_hash=API_HASH, device_model="v3saver", session_string=ss)
            await gg.start()
            await upd_dlg(gg)
            UC[uid] = gg
            return gg
        except Exception as e:
            print(f'User client error: {e}')
            return ubot if ubot else Y
    return Y

async def prog(c, t, C, h, m, st, ud_type):
    global P
    now = time.time()
    p = c / t * 100
    interval = 25 if ud_type == "Downloading" else 6
    if m in P and (now - P[m]) < interval and p < 100:
        return
    P[m] = now
    c_mb = c / (1024 * 1024)
    t_mb = t / (1024 * 1024)
    bar = '🟢' * int(p / 10) + '🔴' * (10 - int(p / 10))
    speed = c / (now - st) / (1024 * 1024) if now > st else 0
    eta = time.strftime('%M:%S', time.gmtime((t - c) / (speed * 1024 * 1024))) if speed > 0 else '00:00'
    icon = "📥" if ud_type == "Downloading" else "📤"
    try:
        await C.edit_message_text(
            h, m, 
            f"**{icon} {ud_type}...**\n\n{bar}\n\n⚡**__Completed__**: {c_mb:.2f} MB / {t_mb:.2f} MB\n📊 **__Done__**: {p:.2f}%\n🚀 **__Speed__**: {speed:.2f} MB/s\n⏳ **__ETA__**: {eta}\n\n**__Powered by Team SPY__**"
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass 
    if p >= 100: P.pop(m, None)

async def send_direct(c, m, tcid, ft=None, rtmid=None):
    try:
        if m.video:
            await c.send_video(tcid, m.video.file_id, caption=ft, duration=m.video.duration, width=m.video.width, height=m.video.height, reply_to_message_id=rtmid)
        elif m.video_note:
            await c.send_video_note(tcid, m.video_note.file_id, reply_to_message_id=rtmid)
        elif m.voice:
            await c.send_voice(tcid, m.voice.file_id, reply_to_message_id=rtmid)
        elif m.sticker:
            await c.send_sticker(tcid, m.sticker.file_id, reply_to_message_id=rtmid)
        elif m.audio:
            await c.send_audio(tcid, m.audio.file_id, caption=ft, duration=m.audio.duration, performer=m.audio.performer, title=m.audio.title, reply_to_message_id=rtmid)
        elif m.photo:
            photo_id = m.photo.file_id if hasattr(m.photo, 'file_id') else m.photo[-1].file_id
            await c.send_photo(tcid, photo_id, caption=ft, reply_to_message_id=rtmid)
        elif m.document:
            await c.send_document(tcid, m.document.file_id, caption=ft, file_name=m.document.file_name, reply_to_message_id=rtmid)
        else:
            return False
        return True
    except Exception as e:
        print(f'Direct send error: {e}')
        return False

async def process_msg(c, u, m, d, lt, uid, i):
    try:
        cfg_chat = await get_user_data_key(d, 'chat_id', None)
        tcid = d
        rtmid = None
        if cfg_chat:
            if '/' in cfg_chat:
                parts = cfg_chat.split('/', 1)
                tcid = int(parts[0])
                rtmid = int(parts[1]) if len(parts) > 1 else None
            else:
                tcid = int(cfg_chat)
        
        if m.media:
            orig_text = m.caption.markdown if m.caption else ''
            proc_text = await process_text_with_rules(d, orig_text)
            user_cap = await get_user_data_key(d, 'caption', '')
            ft = f'{proc_text}\n\n{user_cap}' if proc_text and user_cap else user_cap if user_cap else proc_text
            
            # PUBLIC CLONING LOGIC
            if lt == 'public':
                sent = await send_direct(c, m, tcid, ft, rtmid)
                if sent:
                    return 'Sent directly.'
            
            st = time.time()
            p = await c.send_message(d, 'Downloading...')

            video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'}
            is_real_video = False
            c_name = f"{time.time()}"

            if m.video:
                is_real_video = True
                if m.video.file_name:
                    _, ext = os.path.splitext(m.video.file_name)
                    c_name = sanitize(f"{time.time()}{ext}")
                else:
                    c_name = sanitize(f"{time.time()}.mp4")
            elif m.document:
                if m.document.file_name:
                    _, ext = os.path.splitext(m.document.file_name)
                    if ext.lower() in video_extensions:
                        is_real_video = True
                    c_name = sanitize(f"{time.time()}{ext}")
                else:
                    c_name = sanitize(f"{time.time()}.bin")
            elif m.audio:
                if m.audio.file_name:
                    _, ext = os.path.splitext(m.audio.file_name)
                    c_name = sanitize(f"{time.time()}{ext}")
                else:
                    c_name = sanitize(f"{time.time()}.mp3")
            elif m.photo:
                c_name = sanitize(f"{time.time()}.jpg")
    
            f = await u.download_media(
                m, 
                file_name=c_name, 
                progress=prog, 
                progress_args=(c, d, p.id, st, 'Downloading') 
            )
            
            if not f:
                await c.edit_message_text(d, p.id, 'Failed.')
                return 'Failed.'
            
            if os.path.exists(f) and os.path.getsize(f) == 0:
                os.remove(f)
                await c.edit_message_text(d, p.id, 'Failed: 0KB File.')
                return 'Failed: Disk Full.'

            if (
                (m.video and m.video.file_name) or
                (m.audio and m.audio.file_name) or
                (m.document and m.document.file_name)
            ):
                f = await rename_file(f, d, p)
            
            fsize = os.path.getsize(f) / (1024 * 1024 * 1024)
            th = thumbnail(d)
            generated_thumb = None

            async def cleanup():
                if os.path.exists(f): os.remove(f)
                if generated_thumb and os.path.exists(generated_thumb): os.remove(generated_thumb)
                await c.delete_messages(d, p.id)

            if fsize > 2 and Y:
                st = time.time()
                await upd_dlg(Y)
                try:
                    dur, h, w = 0, 0, 0
                    if is_real_video:
                        try:
                            mtd = await get_video_metadata(f)
                            dur, h, w = mtd['duration'], mtd['width'], mtd['height']
                            generated_thumb = await screenshot(f, dur, d)
                            th = generated_thumb
                        except Exception:
                            pass

                    upload_args = {'progress': prog, 'progress_args': (c, d, p.id, st, 'Uploading')} 

                    if not is_real_video:
                         sent = await Y.send_document(LOG_GROUP, f, thumb=th, caption=ft if m.caption else None,
                                                    reply_to_message_id=rtmid, **upload_args)
                    else:
                        send_funcs = {'video': Y.send_video, 'video_note': Y.send_video_note, 
                                    'voice': Y.send_voice, 'audio': Y.send_audio, 
                                    'photo': Y.send_photo, 'document': Y.send_document}
                        
                        for mtype, func in send_funcs.items():
                            if f.lower().endswith(tuple(video_extensions)): mtype = 'video'
                            if getattr(m, mtype, None):
                                sent = await func(LOG_GROUP, f, thumb=th if mtype == 'video' else None, 
                                                duration=dur if mtype == 'video' else None,
                                                height=h if mtype == 'video' else None,
                                                width=w if mtype == 'video' else None,
                                                caption=ft if m.caption and mtype not in ['video_note', 'voice'] else None, 
                                                reply_to_message_id=rtmid, **upload_args)
                                break
                        else:
                            sent = await Y.send_document(LOG_GROUP, f, thumb=th, caption=ft if m.caption else None,
                                                        reply_to_message_id=rtmid, **upload_args)
                    
                    await c.copy_message(d, LOG_GROUP, sent.id)
                except Exception as e:
                    await c.edit_message_text(d, p.id, f'Error: {str(e)[:30]}')
                    await cleanup()
                    return 'Failed.'
                
                await cleanup()
                return 'Done (Large file).'
            
            st = time.time()
            try:
                uploaded = False
                upload_args = {'progress': prog, 'progress_args': (c, d, p.id, st, 'Uploading')} 

                if is_real_video and (m.video or (m.document and os.path.splitext(f)[1].lower() in video_extensions)):
                    try:
                        mtd = await get_video_metadata(f)
                        dur, h, w = mtd['duration'], mtd['width'], mtd['height']
                        generated_thumb = await screenshot(f, dur, d)
                        th = generated_thumb
                        
                        await c.send_video(tcid, video=f, caption=ft if m.caption else None, 
                                        thumb=th, width=w, height=h, duration=dur, 
                                        reply_to_message_id=rtmid, **upload_args)
                        uploaded = True
                    except Exception:
                        uploaded = False

                if not uploaded:
                    if m.video_note and is_real_video:
                        await c.send_video_note(tcid, video_note=f, reply_to_message_id=rtmid, **upload_args)
                    elif m.voice:
                        await c.send_voice(tcid, f, reply_to_message_id=rtmid, **upload_args)
                    elif m.sticker:
                        await c.send_sticker(tcid, m.sticker.file_id, reply_to_message_id=rtmid)
                    elif m.audio:
                         await c.send_audio(tcid, audio=f, caption=ft if m.caption else None, 
                                        thumb=th, reply_to_message_id=rtmid, **upload_args)
                    elif m.photo:
                        await c.send_photo(tcid, photo=f, caption=ft if m.caption else None, 
                                        reply_to_message_id=rtmid, **upload_args)
                    else:
                        await c.send_document(tcid, document=f, caption=ft if m.caption else None, 
                                            reply_to_message_id=rtmid, **upload_args)
            except Exception as e:
                await c.edit_message_text(d, p.id, f'Error: {str(e)[:30]}')
                await cleanup()
                return 'Failed.'
            
            await cleanup()
            return 'Done.'
            
        elif m.text:
            await c.send_message(tcid, text=m.text.markdown, reply_to_message_id=rtmid)
            return 'Sent.'
    except Exception as e:
        return f'Error: {str(e)[:50]}'
        
@X.on_message(filters.command(['batch', 'single']))
async def process_cmd(c, m):
    uid = m.from_user.id
    cmd = m.command[0]
    
    if FREEMIUM_LIMIT == 0 and not await is_premium_user(uid):
        await m.reply_text("This bot does not provide free servies, get subscription from OWNER")
        return
    
    if await sub(c, m) == 1: return
    pro = await m.reply_text('Doing some checks hold on...')
    
    if is_user_active(uid):
        await pro.edit('You have an active task. Use /stop to cancel it.')
        return
    
    # DB Check + Smart Start
    ubot = await get_ubot(uid)
    
    # If still None after retry logic, it means critical failure (Invalid Token or Ban)
    if not ubot:
        await pro.edit('**Bot failed to start.**\nPossible reasons:\n1. Invalid Token (/setbot again)\n2. Telegram FloodWait (Try later)\n3. Account Banned')
        return
    
    Z[uid] = {'step': 'start' if cmd == 'batch' else 'start_single'}
    await pro.edit(f'Send {"start link..." if cmd == "batch" else "link you to process"}.')

@X.on_message(filters.command(['cancel', 'stop']))
async def cancel_cmd(c, m):
    uid = m.from_user.id
    if is_user_active(uid):
        if await request_batch_cancel(uid):
            await m.reply_text('Cancellation requested. The current batch will stop after the current download completes.')
        else:
            await m.reply_text('Failed to request cancellation. Please try again.')
    else:
        await m.reply_text('No active batch process found.')

@X.on_message(filters.text & filters.private & ~login_in_progress & ~filters.command([
    'start', 'batch', 'cancel', 'login', 'logout', 'stop', 'set', 
    'pay', 'redeem', 'gencode', 'single', 'generate', 'keyinfo', 'encrypt', 'decrypt', 'keys', 'setbot', 'rembot']))
async def text_handler(c, m):
    uid = m.from_user.id
    if uid not in Z: return
    s = Z[uid].get('step')
    
    # DB Check + Smart Start
    x = await get_ubot(uid)
    if not x:
        await m.reply_text('**Bot failed to start.**\nPossible reasons:\n1. Invalid Token (/setbot again)\n2. Telegram FloodWait (Try later)\n3. Account Banned')
        return

    if s == 'start':
        L = m.text
        i, d, lt = E(L)
        if not i or not d:
            await m.reply_text('Invalid link format.')
            Z.pop(uid, None)
            return
        Z[uid].update({'step': 'count', 'cid': i, 'sid': d, 'lt': lt})
        await m.reply_text('How many messages?')

    elif s == 'start_single':
        L = m.text
        i, d, lt = E(L)
        if not i or not d:
            await m.reply_text('Invalid link format.')
            Z.pop(uid, None)
            return

        Z[uid].update({'step': 'process_single', 'cid': i, 'sid': d, 'lt': lt})
        i, s, lt = Z[uid]['cid'], Z[uid]['sid'], Z[uid]['lt']
        pt = await m.reply_text('Processing...')
        
        ubot = await get_ubot(uid)
        
        uc = await get_uclient(uid)
        if not uc:
            await pt.edit('Cannot proceed without user client.')
            Z.pop(uid, None)
            return
            
        if is_user_active(uid):
            await pt.edit('Active task exists. Use /stop first.')
            Z.pop(uid, None)
            return

        try:
            msg = await get_msg(ubot, uc, i, s, lt)
            if msg:
                res = await process_msg(ubot, uc, msg, str(m.chat.id), lt, uid, i)
                await pt.edit(f'1/1: {res}')
            else:
                await pt.edit('Message not found')
        except Exception as e:
            await pt.edit(f'Error: {str(e)[:50]}')
        finally:
            Z.pop(uid, None)

    elif s == 'count':
        if not m.text.isdigit():
            await m.reply_text('Enter valid number.')
            return
        
        count = int(m.text)
        maxlimit = PREMIUM_LIMIT if await is_premium_user(uid) else FREEMIUM_LIMIT

        if count > maxlimit:
            await m.reply_text(f'Maximum limit is {maxlimit}.')
            return

        Z[uid].update({'step': 'process', 'did': str(m.chat.id), 'num': count})
        i, s, n, lt = Z[uid]['cid'], Z[uid]['sid'], Z[uid]['num'], Z[uid]['lt']
        success = 0

        pt = await m.reply_text('Processing batch...')
        uc = await get_uclient(uid)
        ubot = await get_ubot(uid)
        
        if not uc or not ubot:
            await pt.edit('Missing client setup')
            Z.pop(uid, None)
            return
            
        if is_user_active(uid):
            await pt.edit('Active task exists')
            Z.pop(uid, None)
            return
        
        await add_active_batch(uid, {
            "total": n,
            "current": 0,
            "success": 0,
            "cancel_requested": False,
            "progress_message_id": pt.id
            })
        
        try:
            for j in range(n):
                
                if should_cancel(uid):
                    await pt.edit(f'Cancelled at {j}/{n}. Success: {success}')
                    break
                
                await update_batch_progress(uid, j, success)
                
                mid = int(s) + j
                
                try:
                    msg = await get_msg(ubot, uc, i, mid, lt)
                    if msg:
                        res = await process_msg(ubot, uc, msg, str(m.chat.id), lt, uid, i)
                        if 'Done' in res or 'Copied' in res or 'Sent' in res:
                            success += 1
                    else:
                        pass
                except Exception as e:
                    try: await pt.edit(f'{j+1}/{n}: Error - {str(e)[:30]}')
                    except: pass
                
                await asyncio.sleep(6) # Retained 6s delay
            
            if j+1 == n:
                await m.reply_text(f'Batch Completed ✅ Success: {success}/{n}')
        
        finally:
            await remove_active_batch(uid)
            Z.pop(uid, None)
