import asyncio

from CarlJobScheduler import Job, CarlJobScheduler
from CarlPostInfo import CarlPostInfo

tags = ["скетч", "art", "illustrator", "watercolor", "sketch", "акварель", "рисунок", "graphic",
        "graphicdesign", "рисунок", "творчество", "иллюстрация", "иллюстратор", "digitalart", "графика"]

tags_black_list = ["lol", "fitness", "like4like", "me"]

job_count = int(950 / len(tags))


def validate(post_info: CarlPostInfo) -> bool:
    blacklist_intersection = set(tags_black_list) & set(post_info.tags)
    if len(blacklist_intersection) != 0:
        return False
    elif post_info.likes > 200:
        return False
    else:
        return True


async def start():
    scheduler = await CarlJobScheduler.create()
    for tag in tags:
        scheduler.update_job(Job(tag, job_count, validate))

    await scheduler.run_batch()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start())
