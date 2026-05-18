import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any, Optional

import httpx

BASE_URL = "https://pokeapi.co/api/v2"


class PokeApiClient:
    def __init__(self, concurrency: int = 5, cache_dir: Optional[Path] = None):
        self._sem = asyncio.Semaphore(concurrency)
        self._cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
        self._client = httpx.AsyncClient(timeout=30)

    async def close(self):
        await self._client.aclose()

    def _cache_path(self, url: str) -> Optional[Path]:
        if not self._cache_dir:
            return None
        return self._cache_dir / (hashlib.sha256(url.encode()).hexdigest() + ".json")

    async def get_json(self, path: str) -> Any:
        url = path if path.startswith("http") else f"{BASE_URL}{path}"
        cp = self._cache_path(url)
        if cp and cp.exists():
            return json.loads(cp.read_text())
        async with self._sem:
            for attempt in range(4):
                try:
                    resp = await self._client.get(url)
                    if resp.status_code in (429, 500, 502, 503):
                        raise httpx.HTTPStatusError("retryable", request=resp.request, response=resp)
                    resp.raise_for_status()
                    data = resp.json()
                    if cp:
                        cp.write_text(json.dumps(data))
                    return data
                except (httpx.HTTPStatusError, httpx.TransportError):
                    if attempt == 3:
                        raise
                    await asyncio.sleep(2**attempt)
