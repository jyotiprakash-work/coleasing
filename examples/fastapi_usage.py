"""FastAPI integration example (install FastAPI separately)."""

from fastapi import FastAPI, HTTPException

from coleasing import AsyncLeaseManager, AsyncMemoryBackend

app = FastAPI()
leases = AsyncLeaseManager(AsyncMemoryBackend(), default_ttl=30)


@app.post("/reports/daily")
async def create_daily_report() -> dict[str, str]:
    lease = await leases.try_acquire("daily-report")
    if lease is None:
        raise HTTPException(status_code=409, detail="Report generation is already running")
    async with lease:
        # await generate_daily_report()
        return {"status": "generated"}
