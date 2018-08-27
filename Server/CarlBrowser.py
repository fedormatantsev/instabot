import asyncio
import json
import logging
import os
import typing

from pyppeteer import *
from pyppeteer.browser import Browser
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page

from CarlJob import Job
from CarlPostInfo import CarlPostInfo

logging.basicConfig(
    filename="Data/CarlBrowser.log",
    level="INFO",
    format="%(levelname)s %(asctime)s [%(module)s]: %(message)s")

log = logging.getLogger("CarlBrowser")


class CarlBrowser:
    _page: Page
    _browser: Browser
    _terminate_flag: bool = False

    _login_url = "https://www.instagram.com/accounts/login/"
    _challenge_url = "https://www.instagram.com/challenge/"
    _main_url = "https://www.instagram.com/"
    _tag_url = "https://www.instagram.com/explore/tags/{tag}/"
    _cookies_file = "Data/Cookies.json"

    @classmethod
    async def create(cls):
        self = cls()
        self._browser = await launch(headless=False)
        self._page = await self._browser.newPage()

        # Load saved cookies
        try:
            with open(cls._cookies_file, "r") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    await self._page.setCookie(cookie)
        except FileNotFoundError:
            log.info("No cookie file found")
        except json.decoder.JSONDecodeError:
            log.error("Error during cookie file decoding. Removing defective file")
            os.remove(self._cookies_file)

        # Open logon window.
        await self._page.goto(url=self._login_url)

        # Wait for login. (Probably, verification will be required...)
        if self._login_url in self._page.url:
            log.info("Waiting for log in")

            await self._page.waitForNavigation(url=self._main_url, timeout=0)

            # Wait for verification...
            if self._challenge_url in self._page.url:
                log.info("Waiting for verification")
                await self._page.waitForNavigation(url=self._main_url, timeout=0)

        log.info("Logged in")

        # Update cookies
        log.info("Updating cookies")
        cookies = await self._page.cookies(self._main_url)

        with open(self._cookies_file, "w") as file:
            json.dump(cookies, file)

        log.info("CarlBrowser is ready")

        return self

    async def execute_job(self, job: Job) -> typing.Optional[Job]:
        log.info(f"Executing next job (\"{job.tag}\", count={job.count}).")
        await self._page.goto(self._tag_url.format(tag=job.tag))
        await asyncio.sleep(1)
        entry = await self._page.J(f"a[href*='?tagged={job.tag}']")

        if not entry:
            log.error("Can't open entry for tag. Aborting job.")
            return
        await entry.click()

        # todo: use navigation promise or event here instead of sleep
        await asyncio.sleep(2)

        remaining_count = job.count

        try:
            while remaining_count > 0:
                post_info, like_button, next_button = await self._parse_post()

                post_is_valid = job.check_post(post_info)
                if not post_is_valid:
                    log.info("Post doesn't meet job requirements.")

                if like_button and post_is_valid:
                    await like_button.click()
                    await asyncio.sleep(27)
                    remaining_count -= 1

                await next_button.click()
                await asyncio.sleep(3)
        except Exception as e:
            log.error(e)
            return Job(job.tag, remaining_count, job._validate)

        return None

    async def _parse_post(self) -> (CarlPostInfo, ElementHandle, ElementHandle):
        like_button = await self._page.J("span[aria-label=Like]")
        next_button = await self._page.J("a[role=button].coreSpriteRightPaginationArrow")
        tags = await self._fetch_post_tags()
        url = self._page.url
        author = await self._page.querySelectorEval(
            "header > div > div > div > a.notranslate",
            "function(obj){return obj.text;}")
        likes_str = await self._page.querySelectorEval(
            "div > section > div > a",
            "function(obj){return obj.text.split(\" \")[0].replace(\",\", \"\")}")
        likes = 0
        try:
            likes = int(likes_str)
        except ValueError:
            pass

        return CarlPostInfo(tags, url, author, likes), like_button, next_button

    async def _fetch_post_tags(self):
        raw_list = await self._page.querySelectorAllEval(
            "li:first-child > div > div > div > span > a",
            """
                function (array)
                {
                    result = array.map(function(elem)
                    {
                        return elem.text;
                    });
                    return result;
                }
            """)

        filtered_list = filter(lambda elem: elem[0] == "#", raw_list)
        return list(map(lambda elem: elem[1:], filtered_list))
