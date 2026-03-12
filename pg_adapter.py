"""
pg_adapter.py — aiosqlite interfeysi orqali asyncpg ishlatuvchi adapter.
Bot kodida faqat shu faylni import qilib, qolgan barcha kod o'zgarmaydi.
"""
import asyncpg
import re
import os

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        database_url = os.environ.get('DATABASE_URL', '')
        # Railway ba'zan postgres:// beradi, asyncpg postgresql:// talab qiladi
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        _pool = await asyncpg.create_pool(database_url, min_size=1, max_size=10)
    return _pool


def _sqlite_to_pg(sql: str) -> str:
    """SQLite SQL ni PostgreSQL ga aylantirish"""
    sql = sql.strip()

    # ? → $1, $2, $3 ...
    n = 0
    out = []
    for ch in sql:
        if ch == '?':
            n += 1
            out.append(f'${n}')
        else:
            out.append(ch)
    sql = ''.join(out)

    # excluded → EXCLUDED (PostgreSQL standard)
    sql = re.sub(r'\bexcluded\.', 'EXCLUDED.', sql)

    # SQLite AUTOINCREMENT ifodalari (DDL ichida)
    sql = re.sub(
        r'\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b',
        'SERIAL PRIMARY KEY', sql, flags=re.I)
    sql = re.sub(
        r'\bINTEGER\s+PRIMARY\s+KEY\b(?!\s+AUTOINCREMENT)',
        'SERIAL PRIMARY KEY', sql, flags=re.I)

    # INSERT OR IGNORE → INSERT ... ON CONFLICT DO NOTHING
    sql = re.sub(
        r'\bINSERT\s+OR\s+IGNORE\s+INTO\b',
        'INSERT INTO', sql, flags=re.I)
    # ON CONFLICT DO NOTHING ni qo'shish (agar yo'q bo'lsa)
    if 'INSERT OR IGNORE' in sql.upper():  # fallback
        sql = sql + ' ON CONFLICT DO NOTHING'

    # INSERT OR REPLACE → INSERT ... ON CONFLICT DO UPDATE
    sql = re.sub(
        r'\bINSERT\s+OR\s+REPLACE\s+INTO\b',
        'INSERT INTO', sql, flags=re.I)

    return sql


class _FakeCursor:
    """aiosqlite Cursor ni taqlid qiluvchi klass"""

    def __init__(self, rows=None, last_id=None):
        self._rows = rows if rows is not None else []
        self.lastrowid = last_id

    async def fetchall(self):
        return [tuple(r) for r in self._rows]

    async def fetchone(self):
        if self._rows:
            return tuple(self._rows[0])
        return None

    def __aiter__(self):
        self._iter_idx = 0
        return self

    async def __anext__(self):
        if self._iter_idx >= len(self._rows):
            raise StopAsyncIteration
        row = tuple(self._rows[self._iter_idx])
        self._iter_idx += 1
        return row


class _FakeConnection:
    """aiosqlite Connection ni taqlid qiluvchi klass"""

    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn
        self._tr = None

    async def execute(self, sql: str, params=None):
        params = list(params) if params else []
        sql = sql.strip()

        # PRAGMA table_info → PostgreSQL information_schema
        m = re.match(r'PRAGMA\s+table_info\((\w+)\)', sql, re.I)
        if m:
            table = m.group(1).lower()
            rows = await self._conn.fetch(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name=$1 ORDER BY ordinal_position",
                table
            )
            # (cid, name, type, notnull, dflt_value, pk) formatida
            fake = [(i, r['column_name'], '', 0, None, 0) for i, r in enumerate(rows)]
            return _FakeCursor(fake)

        pg_sql = _sqlite_to_pg(sql)

        # INSERT — lastrowid uchun RETURNING id
        if re.match(r'\s*INSERT\s', pg_sql, re.I):
            # ON CONFLICT DO NOTHING bo'lsa RETURNING ishlashi mumkin emas
            if 'ON CONFLICT DO NOTHING' in pg_sql.upper():
                await self._conn.execute(pg_sql, *params)
                return _FakeCursor()
            try:
                # Jadvalda id ustuni bormi?
                returning = re.sub(r'\s*;?\s*$', ' RETURNING id', pg_sql)
                row = await self._conn.fetchrow(returning, *params)
                last_id = row['id'] if row else None
                return _FakeCursor(last_id=last_id)
            except Exception:
                await self._conn.execute(pg_sql, *params)
                return _FakeCursor()

        # SELECT
        if re.match(r'\s*SELECT\s', pg_sql, re.I):
            rows = await self._conn.fetch(pg_sql, *params)
            return _FakeCursor(rows)

        # UPDATE / DELETE / CREATE / ALTER / DROP
        await self._conn.execute(pg_sql, *params)
        return _FakeCursor()

    async def executemany(self, sql: str, params_list):
        pg_sql = _sqlite_to_pg(sql)
        await self._conn.executemany(pg_sql, params_list)

    async def commit(self):
        # asyncpg autocommit rejimida ishlaydi — hech narsa kerak emas
        pass

    async def rollback(self):
        if self._tr:
            await self._tr.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass  # pool.release _DBContextManager da amalga oshiriladi


class _DBContextManager:
    """async with pg_adapter.connect() as db: uchun"""

    def __init__(self):
        self._conn = None
        self._pool = None

    async def __aenter__(self) -> _FakeConnection:
        self._pool = await get_pool()
        self._conn = await self._pool.acquire()
        return _FakeConnection(self._conn)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn and self._pool:
            await self._pool.release(self._conn)


def connect(*args, **kwargs):
    """aiosqlite.connect() ni almashtiradi"""
    return _DBContextManager()
