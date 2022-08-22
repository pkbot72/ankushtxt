from telethon import events, Button
#from config import bot
from FastTelethonhelper import fast_upload
import os
import subprocess
import helper
from telethon.tl.types import DocumentAttributeVideo
import pyrogram
from pyrogram.types import User, Message
from pyrogram import Client, filters

import os
from telethon import TelegramClient
#API_ID = 14560088
#API_HASH = "74a2665339484da3eaaed5f4fe16da79"
#BOT_TOKEN = "5524381543:AAH-s7TDhvA_Ng2k9U5z9pvgiRPy5ChNve8"
#api_id = os.environ.get('API_ID')
#api_hash = os.environ.get('API_HASH')
#bot_token = os.environ.get('BOT_TOKEN')

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, sleep_threshold=120)

#bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

cancel = False

@bot.on_message(filters.command(["start"])& ~filters.edited)
async def account_login(bot: Client, event: Message):

    await event.reply("Hello!")

@bot.on_message(filters.command(["sthumb"])& ~filters.edited)
async def account_login(bot: Client, event: Message):

    x = await event.get_reply_message()
    thumb = await bot.download_media(x.photo)
    with open(thumb, "rb") as f:
        pic = f.read()
    with open("thumb.png", "wb") as f:
        f.write(pic)
    await event.reply("Set as default thumbnail")


@bot.on_message(filters.command(["cthumb"])& ~filters.edited)
async def account_login(bot: Client, event: Message):
    with open("thumb.png", "w") as f:
        f.write("")
    os.remove("thumb.png")
    await event.reply("cleared thumbnail")


@bot.on_message(filters.command(["vthumb"])& ~filters.edited)
async def account_login(bot: Client, event: Message):
    try:
        await event.reply("current default thumbnail", file="thumb.png")
    except:
        await event.reply("No default thumbnail set")



@bot.on_message(filters.command(["cancel"]))
async def cancel(_, m):
    editable = await m.reply_text("Canceling All process Plz wait")
    global cancel
    cancel = True
    await editable.edit("cancled")
    return


@bot.on_message(filters.command(["download"])& ~filters.edited)
async def account_login(bot: Client, event: Message):

    global cancel
    cancel = False
    try:
        arg = int(event.raw_text.split(" ")[1])
        arg -= 1
    except:
        arg = 0
    try:
        txt_file = await event.get_reply_message()
        x = await bot.download_media(txt_file)
        with open(x) as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split(":", 1))
        os.remove(x)
    except:
        await event.reply("Invalid file input.")
        os.remove(x)
        return
    for i in range(arg, len(links)):
        try:
            if cancel == True:
                await event.reply("Process canceled")
                return
            url = links[i][1]
            name = links[i][0].replace("\t", "")
            filename = f"{name[:60]}.mp4"
            r = await event.reply(f"`Downloading...\n{name[:60]}\n\nfile number: {i+1}`")
            caption =  f"`{name[:60]}\n\nfile number: {i+1}`"
            k = await helper.download_video(url, filename)
            filename = k
            res_file = await fast_upload(bot, filename, r)
            if not os.path.isfile("thumb.png"):
                subprocess.call(f'ffmpeg -i "{filename}" -ss 00:00:01 -vframes 1 "{filename}.jpg"', shell=True)
                thumbnail = f"{filename}.jpg"
            else:
                thumbnail = "thumb.png"
            dur = int(helper.duration(filename))
            try:
                await bot.send_message(
                    event.chat_id, 
                    caption, 
                    file=res_file, 
                    force_document=False, 
                    thumb=thumbnail, 
                    supports_streaming=True, 
                    attributes=[DocumentAttributeVideo(
                        duration=dur, 
                        w=1260, 
                        h=720, 
                        supports_streaming=True
                    )]
                )
            except:
                await bot.send_message(
                    event.chat_id,
                    "There was an error while uploading file as streamable so, now trying to upload as document."
                )
                await bot.send_message(
                    event.chat_id, 
                    caption, 
                    file=res_file, 
                    force_document=True,
                )
            os.remove(filename)
            os.remove(f"{filename}.jpg")
            await r.delete()

        
        except Exception as e:
            print(e)
            pass
          
          
@bot.on_message(filters.command(["upload"])& ~filters.edited)
async def account_login(bot: Client, event: Message):
    
    arg = event.raw_text.split(" ", maxsplit = 1)[1]
    arg = arg.split("|")
    if len(arg) == 1:
        file_name = arg[0].split("/")[-1]
        caption = ''
    elif len(arg) == 2:
        file_name = arg[1].strip()
        caption = arg[1].strip()
    else:
        file_name = arg[1].strip()
        caption = arg[2].strip()

    cmd = f'yt-dlp -F "{arg[0]}"'
    k = await helper.run(cmd)
    out = helper.parse_vid_info(str(k))
    print(out)
    buttons = []

    if 'unknown' in out[0][1]:
        r = await event.reply("downloading.")
        f = helper.old_download(arg[0], file_name)
        res_file = await fast_upload(bot, f, r)
        await bot.send_message(
            event.chat_id, 
            f"`{caption}`", 
            file=res_file, 
            force_document=True,
        )
        return

    for i in out:
        if 'youtu' in arg[0]:
            print(i[1])
            x = i[1].split()[0].split("x")[-1]
            buttons.append([Button.inline(i[1], data=f"id:bestvideo[height<={x}][ext=mp4]")])
        else:
            buttons.append([Button.inline(i[1], data=f"id:{i[0]}")])
    await bot.send_message(event.chat_id, f"`Name: {file_name}`\n`Caption: {caption}`\n`Url: {arg[0]}`", buttons=buttons)
    
@bot.on_message(filters.command(["txt"])& ~filters.edited)
async def account_login(bot: Client, event: Message):

    try:
        x = await event.get_reply_message()
        json_file = await bot.download_media(x)
        res, count = helper.parse_json_to_txt(json_file)
        await event.reply(f"{count} links detected." ,file=res)
        os.remove(json_file)
        os.remove(res)
    except Exception as e:
        print(e)
        await event.reply("Invalid Json file input.")

@bot.on_message(filters.command(["html"])& ~filters.edited)
async def account_login(bot: Client, event: Message):

    try:
        x = await event.get_reply_message()
        json_file = await bot.download_media(x)
        res, count = helper.parse_json_to_html(json_file)
        await event.reply(f"{count} links detected." ,file=res)
        os.remove(json_file)
        os.remove(res)
    except Exception:
        await event.reply("Invalid Json file input.")

@bot.on_message(events.CallbackQuery(pattern=b"id:"))
async def account_login(bot: Client, event: Message):
    r = await event.reply("Trying to download....")
    data = event.data.decode('utf-8')
    data = data.split(":")
    msg = await bot.get_messages(event.chat_id, ids=event.message_id)
    await msg.edit(buttons=None)
    msg = msg.raw_text.split("\n")
    file_name = msg[0].replace("Name: ", "")
    caption = msg[1].replace("Caption: ", "")
    url = msg[2].replace("Url: ", "") 
    vid_id = (data[1])
    filename = await helper.download_video(url, file_name, vid_id)
    res_file = await fast_upload(bot, filename, r)
    if not os.path.isfile("thumb.png"):
        subprocess.call(f'ffmpeg -i "{filename}" -ss 00:00:01 -vframes 1 "{filename}.jpg"', shell=True)
        thumbnail = f"{filename}.jpg"
    else:
        thumbnail = "thumb.png"
    try:
        dur = int(helper.duration(filename))
        await bot.send_message(
            event.chat_id, 
            f"{caption}", 
            file=res_file, 
            force_document=False, 
            thumb=thumbnail, 
            supports_streaming=True, 
            attributes=[DocumentAttributeVideo(
                duration=dur, 
                w=1260, 
                h=720, 
                supports_streaming=True
            )]
        )

    except:
        await bot.send_message(
            event.chat_id,
            "There was an error while uploading file as streamable so, now trying to upload as document."
        )
        await bot.send_message(
            event.chat_id, 
            f"`{caption}`", 
            file=res_file, 
            force_document=True,
        )

    os.remove(filename)
    os.remove(f"{filename}.jpg")

    await r.delete()   


bot.start()

bot.run_until_disconnected()

