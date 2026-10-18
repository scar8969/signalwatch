import asyncio


async def replay(signals, speed=1.0):
    last_ts = None
    for s in signals:
        if last_ts is not None and s.ts:
            await asyncio.sleep(max(0.1, (s.ts - last_ts).total_seconds() / speed))
        last_ts = s.ts
        yield s
