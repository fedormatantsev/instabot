from CarlBrowser import CarlBrowser
from CarlJob import Job

import asyncio
import typing


class CarlJobScheduler:
    _browser: CarlBrowser
    _jobs: typing.Dict[str, Job] = {}
    _job_queue: asyncio.Queue = asyncio.Queue()

    @classmethod
    async def create(cls):
        self = cls()
        self._browser = await CarlBrowser.create()
        return self

    async def run_batch(self):
        for job in self._jobs.values():
            await self._job_queue.put(job)

        while not self._job_queue.empty():
            job = await self._job_queue.get()
            new_job = await self._browser.execute_job(job)
            if new_job:
                await self._job_queue.put(new_job)

    def update_job(self, job: Job):
        self._jobs.update({job.tag: job})
