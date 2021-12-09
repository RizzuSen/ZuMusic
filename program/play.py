import asyncio
import re

from youtube_search import YoutubeSearch
import converter
from youtube import youtube
from config import DURATION_LIMIT, que, SUDO_USERS
from cache.admins import admins as a
from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2, UPDATES_CHANNEL
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from pyrogram import Client
import aiofiles
import ffmpeg
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch

# plus
chat_id = None
DISABLED_GROUPS = []
useer = "NaN"


def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes or cb.from_user.id in SUDO_USERS:
            return await func(client, cb)
        await cb.answer("You ain't allowed!", show_alert=True)
        return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 30)
    draw.text((190, 550), f"Judul: {title}", (255, 255, 255), font=font)
    draw.text((190, 590), f"Durasi: {duration} Menit", (255, 255, 255), font=font)
    draw.text((190, 630), f"Dilihat: {views}", (255, 255, 255), font=font)
    draw.text(
        (190, 670),
        f"Request By: {requested_by}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(
    command("Maintainmode") & ~filters.edited & ~filters.bot & ~filters.private
)
@authorized_users_only
async def hfmm(_, message):
    global DISABLED_GROUPS
    try:
        user_id = message.from_user.id
    except:
        return
    if len(message.command) != 2:
        await message.reply_text(
            "I only recognize `/Maintainmode on` and /Maintainmode `off only`"
        )
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status in ["OFF", "Off", "off"]:
        lel = await message.reply("`Processing...`")
        if message.chat.id not in DISABLED_GROUPS:
            await lel.edit("This Chat is not In maintainence mode")
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"Maintainence Mode disabled In **{message.chat.title}** Chat"
        )

    elif status in ["ON", "On", "on"]:
        lel = await message.reply("`Processing...`")

        if message.chat.id in DISABLED_GROUPS:
            await lel.edit("maintainence mode  already active in This Chat")
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"Maintainence mode is now enabled in **{message.chat.title}** Chat"
        )
    else:
        await message.reply_text(
            "I only recognize `/Maintainmode on` and /Maintainmode `off only"
        )


@Client.on_callback_query(filters.regex(pattern=r"^(cls)$"))
@cb_admin_check
@authorized_users_only
async def m_cb(b, cb):
    global que
    qeue = que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    chat_id = cb.message.chat.id
    m_chat = cb.message.chat

    if type_ == "cls":
        await cb.answer("Closed menu")
        await cb.message.delete()


# play
@Client.on_message(
    command("play")
    & filters.group
    & ~filters.edited
    & ~filters.forwarded
    & ~filters.via_bot
)
async def play(_, message: Message):
    global que
    global useer
    if message.chat.id in DISABLED_GROUPS:
        await message.reply("**maintainence mode is on, ask admin to disable it!**")
        return
    lel = await message.reply("`🔄 𝐒𝐞𝐝𝐚𝐧𝐠 𝐦𝐞𝐦𝐩𝐫𝐨𝐬𝐞𝐬...`")

    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "@Stereo_Ast"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                await lel.edit(
                    "<b>Remember to add Assistant to your channel</b>",
                )
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Add me as admin of yor group first</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id,
                        "𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧 𝐭𝐞𝐥𝐚𝐡 𝐛𝐞𝐫𝐠𝐚𝐛𝐮𝐧𝐠 𝐝𝐢 𝐠𝐫𝐮𝐩 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐦𝐛𝐚𝐧𝐭𝐮 𝐦𝐞𝐦𝐮𝐭𝐚𝐫 𝐦𝐮𝐬𝐢𝐜 𝐝𝐢 𝐨𝐛𝐫𝐨𝐥𝐚𝐧 𝐬𝐮𝐚𝐫𝐚",
                    )
                    await lel.edit(
                        "<b>𝐀𝐬𝐬𝐢𝐬𝐭𝐚𝐧 𝐛𝐨𝐭 𝐬𝐮𝐝𝐚𝐡 𝐛𝐞𝐫𝐚𝐝𝐚 𝐝𝐢 𝐠𝐫𝐨𝐮𝐩 𝐢𝐧𝐢</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    await lel.edit(
                        f"<b>🛑 Flood Wait Error 🛑</b> \n\Hey {user.first_name}, assistant userbot couldn't join your group due to heavy join requests. Make sure userbot is not banned in group and try again later!"
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>Hey {user.first_name}, Asisten tidak ada dalam obrolan ini, suruh admin untuk mengirim perintah /play untuk pertama kali untuk menambahkannya.</i>"
        )
        return

    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ Video lebih dari {DURATION_LIMIT} menit tidak dapat di putar!"
            )

        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/a7adee6cf365d74734c5d.png"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✨ 𝐆𝐫𝐨𝐮𝐩𝐬", url="t.me/luciddreaams"),
                    InlineKeyboardButton("𝐂𝐡𝐚𝐧𝐧𝐞𝐥 ✨", url="t.me/infobotmusik"),
                ],
            ]
        )

        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )

    elif url:
        try:
            results = YoutubeSearch(url, max_results=1).to_dict()
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("✨ 𝐆𝐫𝐨𝐮𝐩𝐬", url="t.me/luciddreaams"),
                        InlineKeyboardButton("𝐂𝐡𝐚𝐧𝐧𝐞𝐥 ✨", url="t.me/infobotmusik"),
                    ],
                ]
           )

        except Exception as e:
            title = "NaN"
            thumb_name = "https://telegra.ph/file/a7adee6cf365d74734c5d.png"
            duration = "NaN"
            views = "NaN"
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="𝐘𝐨𝐮𝐭𝐮𝐛𝐞 🎬", url="https://youtube.com")]]
            )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ Videos longer than {DURATION_LIMIT} minutes aren't allowed to play!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))
    else:
        if len(message.command) < 2:
            return await lel.edit(
                "❎ 𝐋𝐚𝐠𝐮 𝐭𝐢𝐝𝐚𝐤 𝐝𝐢𝐭𝐞𝐦𝐮𝐤𝐚𝐧. 𝐂𝐨𝐛𝐚 𝐜𝐚𝐫𝐢 𝐝𝐞𝐧𝐠𝐚𝐧 𝐣𝐮𝐝𝐮𝐥 𝐥𝐚𝐠𝐮 𝐲𝐚𝐧𝐠 𝐥𝐞𝐛𝐢𝐡 𝐣𝐞𝐥𝐚𝐬\n𝐂𝐨𝐧𝐭𝐨𝐡 » `/play Jentaka`\n\n𝐂𝐡𝐚𝐧𝐧𝐞𝐥 : @infobotmusik"
            )
        await lel.edit("**🔎 𝐒𝐞𝐝𝐚𝐧𝐠 𝐦𝐞𝐧𝐜𝐚𝐫𝐢 𝐥𝐚𝐠𝐮...**")
        query = message.text.split(None, 1)[1]
        # print(query)
        await lel.edit("**🎵 𝐌𝐞𝐧𝐠𝐡𝐮𝐛𝐮𝐧𝐠𝐤𝐚𝐧 𝐤𝐞 𝐯𝐜𝐠...**")
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print results
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            url_suffix = results[0]["url_suffix"]
            views = results[0]["views"]
            durl = url
            durl = durl.replace("youtube", "youtubepp")

            secmul, dur, dur_arr = 1, 0, duration.split(":")
            for i in range(len(dur_arr) - 1, -1, -1):
                dur += int(dur_arr[i]) * secmul
                secmul *= 60

        except Exception as e:
            await lel.edit(
                "❎ 𝐋𝐚𝐠𝐮 𝐭𝐢𝐝𝐚𝐤 𝐝𝐢𝐭𝐞𝐦𝐮𝐤𝐚𝐧. 𝐂𝐨𝐛𝐚 𝐜𝐚𝐫𝐢 𝐝𝐞𝐧𝐠𝐚𝐧 𝐣𝐮𝐝𝐮𝐥 𝐥𝐚𝐠𝐮 𝐲𝐚𝐧𝐠 𝐥𝐞𝐛𝐢𝐡 𝐣𝐞𝐥𝐚𝐬..𝐂𝐨𝐧𝐭𝐨𝐡 » `/play Jentaka`"
            )
            print(str(e))
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✨ 𝐆𝐫𝐨𝐮𝐩𝐬", url="t.me/luciddreaams"),
                    InlineKeyboardButton("𝐂𝐡𝐚𝐧𝐧𝐞𝐥 ✨", url="t.me/infobotmusik"),
                ],
            ]
        )

        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ Video lebih dari {DURATION_LIMIT} menit, tidak dapat di putar!"
            )
            return
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await converter.convert(youtube.download(url))

    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
            photo="final.png",
            caption="**💿 𝐉𝐮𝐝𝐮𝐥 :** {}\n**⏳ 𝐃𝐮𝐫𝐚𝐬𝐢 :** {} `𝐌𝐞𝐧𝐢𝐭`\n**🎧 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐛𝐲 :** {}\n**🌟 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 :** `Stereo Project`\n\n**🔢 𝐒𝐞𝐝𝐚𝐧𝐠 𝐚𝐧𝐭𝐫𝐢 𝐝𝐢 𝐩𝐨𝐬𝐢𝐬𝐢 𝐤𝐞 » `{}`...**".format(
                title,
                duration,
                message.from_user.mention(),
                position,
            ),
            reply_markup=keyboard,
        )
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption="**💿 𝐉𝐮𝐝𝐮𝐥 :** {}\n**⏳ 𝐃𝐮𝐫𝐚𝐬𝐢 :** {} `𝐌𝐞𝐧𝐢𝐭`\n**🎧 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐛𝐲 :** {}\n**🌟 𝐏𝐨𝐰𝐞𝐫𝐞𝐝 𝐛𝐲 :** `Stereo Project`\n\n**🎵 𝘚𝘦𝘥𝘢𝘯𝘨 𝘮𝘦𝘮𝘶𝘵𝘢𝘳 𝘮𝘶𝘴𝘪𝘤 𝘥𝘪 `{}`...**".format(
                title, duration, message.from_user.mention(), message.chat.title
            ),
        )

    os.remove("final.png")
    return await lel.delete()
