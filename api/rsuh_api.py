import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Callable, Awaitable

from aiohttp import ClientSession, ClientTimeout, TCPConnector, FormData
from aiohttp.client_exceptions import ClientError
from yarl import URL

from api.cache import InMemoryTTLCache


BASE_URL = URL("https://raspis.rggu.ru/api/")
MOSCOW_TZ = timezone(timedelta(hours=3))


class RgguApiError(Exception):
    """
    Базовая ошибка клиента РГГУ.
    """


class RgguInvalidInput(RgguApiError):
    """
    Неверные входные параметры.
    """


class RgguHTTPError(RgguApiError):
    """
    HTTP-ошибка при запросе к API.
    """

    def __init__(self, status: int, message: str = ""):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


class RgguBadResponse(RgguApiError):
    """
    Ответ не JSON или структура неожиданна.
    """


def _ttl_until_midnight_moscow(now: Optional[datetime] = None) -> int:
    now = now or datetime.now(MOSCOW_TZ)
    tomorrow = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return max(1, int((tomorrow - now).total_seconds()))


class RgguScheduleClient:
    """
    Асинхронный клиент для расписания РГГУ с опциональным кэшированием справочников.
    """

    def __init__(
        self,
        *,
        session: Optional[ClientSession] = None,
        timeout_seconds: float = 20.0,
        max_connections: int = 20,
        retries: int = 3,
        backoff_base: float = 0.5,
        cache=InMemoryTTLCache(),
        cache_ttl_seconds: Optional[int] = None,
    ):
        self._external_session = session
        self._session: Optional[ClientSession] = session
        self._timeout = ClientTimeout(total=timeout_seconds)
        self._connector = (
            TCPConnector(limit=max_connections, ssl=False) if session is None else None
        )
        self._retries = max(0, retries)
        self._backoff_base = max(0.1, backoff_base)

        self._cache = cache
        self._cache_ttl_seconds = cache_ttl_seconds

    async def __aenter__(self) -> "RgguScheduleClient":
        if self._session is None:
            self._session = ClientSession(
                timeout=self._timeout, connector=self._connector
            )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self._external_session is None and self._session is not None:
            await self._session.close()
            self._session = None

    async def get_eduforms_courses(self) -> Any:
        cache_key = self._key("Get_Eduforms_Courses_Lists")
        return await self._cached_fetch(
            cache_key,
            self._calc_ttl(),
            lambda: self._post("Get_Eduforms_Courses_Lists", data=None),
        )

    async def get_teachers_list(self) -> Any:
        cache_key = self._key("Get_Teachers_List")
        return await self._cached_fetch(
            cache_key,
            self._calc_ttl(),
            lambda: self._post("Get_Teachers_List", data=None),
        )

    async def get_rooms_list(self) -> Any:
        cache_key = self._key("Get_Rooms_List")
        return await self._cached_fetch(
            cache_key,
            self._calc_ttl(),
            lambda: self._post("Get_Rooms_List", data=None),
        )

    async def get_groups_list(self, eduform: str, course: str) -> Any:
        if not eduform or course is None:
            raise RgguInvalidInput("Нужно указать 'eduform' и 'course'.")
        payload = json.dumps({"eduform": str(eduform), "course": str(course)})
        form = FormData()
        form.add_field("0", payload)
        cache_key = self._key(
            "Get_Flows_List", eduform=str(eduform), course=str(course)
        )
        return await self._cached_fetch(
            cache_key,
            self._calc_ttl(),
            lambda: self._post("Get_Flows_List", data=form),
        )

    async def get_schedule_by_group(
        self, *, eduform: str, course: str, group_id: str
    ) -> Dict[str, Any]:
        """
        Расписание по группе (потоку). НЕ кэшируется.
        """
        if not (eduform and group_id and course is not None):
            raise RgguInvalidInput("Нужно указать 'eduform', 'course' и 'flow_id'.")
        form = FormData()
        form.add_field("eduform", str(eduform))
        form.add_field("course", str(course))
        form.add_field("flow", str(group_id))
        form.add_field("intervalMode", "4")
        form.add_field("menuMode", "flow")
        return await self._post("Get_Schedule_Table", data=form)

    async def get_schedule_by_teacher(self, *, teacher_id: str) -> Dict[str, Any]:
        """
        Расписание по преподавателю.
        """
        if not teacher_id:
            raise RgguInvalidInput("Нужно указать 'teacher_id'.")
        form = FormData()
        form.add_field("teacher", str(teacher_id))
        form.add_field("intervalMode", "4")
        form.add_field("menuMode", "teacher")
        return await self._post("Get_Schedule_Table", data=form)

    async def get_schedule_by_room(self, *, room_id: str) -> Dict[str, Any]:
        """
        Расписание по аудитории.
        """
        if not room_id:
            raise RgguInvalidInput("Нужно указать 'room_id'.")
        form = FormData()
        form.add_field("room", str(room_id))
        form.add_field("intervalMode", "4")
        form.add_field("menuMode", "room")
        return await self._post("Get_Schedule_Table", data=form)

    def _calc_ttl(self) -> int:
        """
        TTL для справочников: фиксированный, если задан, иначе до полуночи МСК.
        """
        if self._cache_ttl_seconds is not None:
            return max(1, int(self._cache_ttl_seconds))
        return _ttl_until_midnight_moscow()

    def _key(self, endpoint: str, **kwargs: str) -> str:
        """
        Генерация стабильного ключа кэша для endpoint + параметров.
        """
        if not kwargs:
            return f"rggu:{endpoint}"
        parts = [f"{k}={kwargs[k]}" for k in sorted(kwargs)]
        return f"rggu:{endpoint}|" + "&".join(parts)

    async def _cached_fetch(
        self,
        key: str,
        ttl_seconds: int,
        fetch: Callable[[], Awaitable[Any]],
    ) -> Any:
        if not self._cache:
            return await fetch()

        cached = await self._cache.get(key)
        if cached is not None:
            return cached

        lock = self._cache.lock_for(key)
        async with lock:
            cached2 = await self._cache.get(key)
            if cached2 is not None:
                return cached2
            value = await fetch()
            await self._cache.set(key, value, ttl_seconds)
            return value

    async def _post(self, endpoint: str, *, data: Optional[FormData]) -> Any | None:
        if self._session is None:
            self._session = ClientSession(
                timeout=self._timeout, connector=self._connector
            )

        url = BASE_URL / endpoint

        attempt = 0
        while True:
            try:
                async with self._session.post(str(url), data=data) as resp:
                    status = resp.status
                    if status in (429, 500, 502, 503, 504):
                        text_hint = ""
                        try:
                            text_hint = await resp.text()
                        except Exception:
                            pass

                        if attempt < self._retries:
                            await asyncio.sleep(self._backoff(attempt))
                            attempt += 1
                            continue
                        raise RgguHTTPError(status, text_hint[:300])

                    if status >= 400:
                        text_hint = ""
                        try:
                            text_hint = await resp.text()
                        except Exception:
                            pass
                        raise RgguHTTPError(status, text_hint[:300])

                    try:
                        data_obj = await resp.json(content_type=None)
                    except Exception as e:
                        text_snippet = ""
                        try:
                            raw = await resp.text()
                            text_snippet = raw[:300]
                        except Exception:
                            pass
                        raise RgguBadResponse(
                            f"Ответ не JSON. Фрагмент: {text_snippet}"
                        ) from e

                    return data_obj

            except ClientError as e:
                if attempt < self._retries:
                    await asyncio.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise RgguApiError(f"Сетевая ошибка: {e!r}") from e
            except asyncio.TimeoutError as e:
                if attempt < self._retries:
                    await asyncio.sleep(self._backoff(attempt))
                    attempt += 1
                    continue
                raise RgguApiError("Таймаут запроса к API.") from e

    def _backoff(self, attempt: int) -> float:
        jitter = 0.1 * (attempt + 1)
        return self._backoff_base * (2**attempt) + jitter
