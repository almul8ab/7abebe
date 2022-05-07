from pyrogram import Client, errors
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from youtubesearchpython import VideosSearch
from config import BOT_USERNAME, UPDATES_CHANNEL

buttons = [
    [
        InlineKeyboardButton('🧩 قناة البوت', url=f'https://t.me/{UPDATES_CHANNEL}'),
        InlineKeyboardButton('🎧 تشغيل موسيقي', url=f'https://t.me/{BOT_USERNAME}'),
    ],
    [
        InlineKeyboardButton('➕ اضف البوت لمجموعتك ➕', url=f'https://t.me/{BOT_USERNAME}?startgroup=true')
    ]
    ]

@Client.on_inline_query()
async def inline(client: Client, query: InlineQuery):
    answers = []
    search_query = query.query.lower().strip().rstrip()

    if query.query == "inline_ass_by_ahmedyad":
        answers.append(
            InlineQueryResultArticle(
                title="ahmedyad200",
                input_message_content=InputTextMessageContent(f"<b>اهلا انا الحساب المساعد لي بوت تشغيل الموسيقي\nتم اضافتك الي جهات الاتصال يمكنك اضافتي الي اي مجموعة</b>"),
                reply_markup=InlineKeyboardMarkup(buttons)
                )
            )
        await query.answer(results=answers, cache_time=0)
        return

    if search_query == "":
        await client.answer_inline_query(
            query.id,
            results=answers,
            switch_pm_text="ادخل عنوان الفيديو علي يوتيوب...",
            switch_pm_parameter="help",
            cache_time=0,
        )
    else:
        search = VideosSearch(search_query, limit=50)

        for result in search.result()["result"]:
            answers.append(
                InlineQueryResultArticle(
                    title=result["title"],
                    description="المدة {}, {}.".format(
                        result["duration"], result["viewCount"]["short"]
                    ),
                    input_message_content=InputTextMessageContent(
                        "https://www.youtube.com/watch?v={}".format(result["id"])
                    ),
                    thumb_url=result["thumbnails"][0]["url"],
                )
            )

        try:
            await query.answer(results=answers, cache_time=0)
        except errors.QueryIdInvalid:
            await query.answer(
                results=answers,
                cache_time=0,
                switch_pm_text="خطأ: انتهاء وقت البحث",
                switch_pm_parameter="",
            )
