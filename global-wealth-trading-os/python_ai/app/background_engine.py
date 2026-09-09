from __future__ import annotations

import asyncio
from dataclasses import dataclass,field
from datetime import datetime,timezone
from typing import Awaitable,Callable


Job=Callable[[],Awaitable[None]]


@dataclass
class BackgroundJob:
    name:str
    interval_seconds:int
    callback:Job
    enabled:bool=True
    last_started_at:str|None=None
    last_completed_at:str|None=None
    last_error:str|None=None


class BackgroundEngine:
    """
    Lightweight in-process scheduler for autonomous research tasks.

    Production can later move these jobs to a durable queue/worker system.
    """
    def __init__(self)->None:
        self.jobs:dict[str,BackgroundJob]={}
        self.tasks:dict[str,asyncio.Task]={}
        self._stopping=False

    def register(self,name:str,interval_seconds:int,callback:Job)->None:
        if interval_seconds<60:
            raise ValueError("background investment jobs must run no more frequently than once per minute")
        self.jobs[name]=BackgroundJob(name,interval_seconds,callback)

    async def _runner(self,job:BackgroundJob)->None:
        while not self._stopping and job.enabled:
            job.last_started_at=datetime.now(timezone.utc).isoformat()
            job.last_error=None
            try:
                await job.callback()
                job.last_completed_at=datetime.now(timezone.utc).isoformat()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                job.last_error=str(exc)
            await asyncio.sleep(job.interval_seconds)

    def start(self)->None:
        self._stopping=False
        for name,job in self.jobs.items():
            if job.enabled and name not in self.tasks:
                self.tasks[name]=asyncio.create_task(self._runner(job))

    async def stop(self)->None:
        self._stopping=True
        for task in self.tasks.values():
            task.cancel()
        await asyncio.gather(*self.tasks.values(),return_exceptions=True)
        self.tasks.clear()

    def status(self)->list[dict]:
        return [
            {
                "name":j.name,"enabled":j.enabled,
                "interval_seconds":j.interval_seconds,
                "last_started_at":j.last_started_at,
                "last_completed_at":j.last_completed_at,
                "last_error":j.last_error,
            }
            for j in self.jobs.values()
        ]
