from cache.admins import admins
from driver.veez import call_py
from pyrogram import Client, filters
from driver.decorators import authorized_users_only
from driver.filters import command, other_filters
from driver.queues import QUEUE, clear_queue
from driver.utils import skip_current_song, skip_item
from config import BOT_USERNAME, GROUP_SUPPORT, IMG_3, UPDATES_CHANNEL
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


bttn = InlineKeyboardMarkup(
    [[InlineKeyboardButton("š Go Back", callback_data="cbmenu")]]
)


bcl = InlineKeyboardMarkup(
    [[InlineKeyboardButton("š Close ", callback_data="cls")]]
)


@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def update_admin(client, message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text(
        "ā** Bot dimulai ulang !**\nā ** Daftar admin ** telah ** diperbarui !**"
    )


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}", "vskip"]) & other_filters)
@authorized_users_only
async def skip(client, m: Message):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=" šØ Menu ", callback_data="cbmenu"
                ),
                InlineKeyboardButton(
                    text=" šØ Close ", callback_data="cls"
                ),
            ]
        ]
    )

    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("ā Daftar lagu tidak tersedia ")
        elif op == 1:
            await m.reply("ā __Daftar antrian__ **kosong.**\n\n**ā¢ Bot turun perlahan agar tidak terpeleset.**")
        elif op == 2:
            await m.reply("šļø **Antrian lagu telah dihapus**\n\n**ā¢ Bot turun perlahan agar tidak terpeleset.**")
        else:
            await m.reply_photo(
                photo=f"{IMG_3}",
                caption=f"ā­ **Antrian lagu di skip**\n\nš· **Name:** [{op[0]}]({op[1]})\nš­ **Chat:** `{chat_id}`\nš” **Status:** `Playing`\nš§ **Request by:** {m.from_user.mention()}",
                reply_markup=keyboard,
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "š **Antrian dihapus, biar gak penuh seperti hati.:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#{x}** - {hm}"
            await m.reply(OP)


@Client.on_message(
    command(["stop", f"stop@{BOT_USERNAME}", "end", f"end@{BOT_USERNAME}", "vstop"])
    & other_filters
)
@authorized_users_only
async def stop(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("ā Bot turun perlahan , biar ga kepleset.")
        except Exception as e:
            await m.reply(f"š« **error:**\n\n`{e}`")
    else:
        await m.reply("ā **tidak ada yang diputar**")


@Client.on_message(
    command(["pause", f"pause@{BOT_USERNAME}", "vpause"]) & other_filters
)
@authorized_users_only
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(
                "āø **Track paused.**\n\nā¢ **To resume the stream, use the**\nĀ» /resume command."
            )
        except Exception as e:
            await m.reply(f"š« **error:**\n\n`{e}`")
    else:
        await m.reply("ā **tidak ada yang diputar**")


@Client.on_message(
    command(["resume", f"resume@{BOT_USERNAME}", "vresume"]) & other_filters
)
@authorized_users_only
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(
                "ā¶ļø **Pemutaran dilanjutkan !.**\n\nā¢ **Jika ingin menghentikan lagu sementara , tekan pause**\nĀ» /pause command."
            )
        except Exception as e:
            await m.reply(f"š« **error:**\n\n`{e}`")
    else:
        await m.reply("ā **tidak ada yang diputar**")


@Client.on_message(
    command(["mute", f"mute@{BOT_USERNAME}", "vmute"]) & other_filters
)
@authorized_users_only
async def mute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await m.reply(
                "š **Bot dibisukan.**\n\nā¢ **Untuk membunyikan kembali, tekan**\nĀ» /unmute command."
            )
        except Exception as e:
            await m.reply(f"š« **error:**\n\n`{e}`")
    else:
        await m.reply("ā **tidak ada yang diputar**")


@Client.on_message(
    command(["unmute", f"unmute@{BOT_USERNAME}", "vunmute"]) & other_filters
)
@authorized_users_only
async def unmute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await m.reply(
                "š **Bot sudah tidak dibisukan.**\n\nā¢ **Untuk membisukan bot**\nĀ» /mute command."
            )
        except Exception as e:
            await m.reply(f"š« **error:**\n\n`{e}`")
    else:
        await m.reply("ā **tidak ada yang diputar**")


@Client.on_callback_query(filters.regex("cbpause"))
async def cbpause(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\nĀ» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("š”anda bukan admin ", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await query.edit_message_text(
                "āø Lagu di pause ", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"š« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("ā tidak menemukan lagu untuk diputar !", show_alert=True)


@Client.on_callback_query(filters.regex("cbresume"))
async def cbresume(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\nĀ» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("š”Anda bukan admin ! ", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await query.edit_message_text(
                "ā¶ļø Pemutaran dilanjutkan kembali !", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"š« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("ā tidak menemukan lagu untuk diputar !", show_alert=True)


@Client.on_callback_query(filters.regex("cbstop"))
async def cbstop(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("š”Anda anonymous admin !\n\nĀ» kembali ke akun anda untuk melanjutkan")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("š”Anda bukan admin !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await query.edit_message_text("ā **Bot turun secara perlahan**", reply_markup=bcl)
        except Exception as e:
            await query.edit_message_text(f"š« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("ā tidak menemukan lagu untuk diputar", show_alert=True)


@Client.on_callback_query(filters.regex("cbmute"))
async def cbmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("Anda anonymous admin !\n\nĀ» kembali ke akun utama anda.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("š”anda bukan admin ", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await query.edit_message_text(
                "š Bot telah dibisukan ! ", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"š« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("ā tidak menemukan lagu untuk diputar ", show_alert=True)


@Client.on_callback_query(filters.regex("cbunmute"))
async def cbunmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("anda anonymous admin !\n\nĀ» kembali ke akun utama untuk melanjutkan.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("š”anda bukan admin", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await query.edit_message_text(
                "š Bot dibunyikan kembali ", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"š« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("ā tidak ada lagu untuk diputar !", show_alert=True)


@Client.on_message(
    command(["volume", f"volume@{BOT_USERNAME}", "vol"]) & other_filters
)
@authorized_users_only
async def change_volume(client, m: Message):
    range = m.command[1]
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.change_volume_call(chat_id, volume=int(range))
            await m.reply(
                f"ā **volume set to** `{range}`%"
            )
        except Exception as e:
            await m.reply(f"š« **error:**\n\n`{e}`")
    else:
        await m.reply("ā **tidak ada yang diputar**")
