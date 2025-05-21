from telethon.sync import TelegramClient
from datetime import datetime, timezone

api_id = 29986445
api_hash = '0a6151883a6ecbb50a2c65d2d3df9649'

client = TelegramClient('uniapi', api_id, api_hash)

async def fetch_and_separate_posts():
    await client.start()
    entity = await client.get_entity('upc_news')
    start_date = datetime(2022, 2, 24, tzinfo=timezone.utc)

    with_tag = []
    without_tag = []

    async for msg in client.iter_messages(entity, offset_date=None, reverse=True):
        if msg.date < start_date:
            continue
        if not msg.message:
            continue

        text = msg.message.strip()
        timestamp = msg.date.strftime('%Y-%m-%d %H:%M')
        entry = f"{timestamp}\n{text}\n\n"

        if "#ПроповідьПредстоятеля" in text:
            with_tag.append(entry)
        else:
            without_tag.append(entry)

    # Збереження у файли
    with open("posts_with_hashtag.txt", "w", encoding="utf-8") as f1:
        f1.writelines(with_tag)
    with open("posts_without_hashtag.txt", "w", encoding="utf-8") as f2:
        f2.writelines(without_tag)

    print(f"✅ {len(with_tag)} з хештегом | {len(without_tag)} без хештегу")

with client:
    client.loop.run_until_complete(fetch_and_separate_posts())




