# services/hospitals_service.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID, uuid4

from models.hospital import HospitalRead, HospitalCreate, HospitalUpdate
from models.enums import CommonStatus
from services.db import db_cursor


def list_hospitals(
    city: Optional[str],
    state: Optional[str],
    status_q: Optional[CommonStatus],
    limit: int = 50,
) -> List[HospitalRead]:
    sql = """
        SELECT id, name, city, state, phone, status,
               created_at, updated_at
        FROM hospitals
    """
    where: list[str] = []
    params: list[object] = []

    if city:
        where.append("city = %s")
        params.append(city)
    if state:
        where.append("state = %s")
        params.append(state)
    if status_q is not None:
        where.append("status = %s")
        params.append(status_q.value)

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)

    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [HospitalRead(**row) for row in rows]


def create_hospital(h: HospitalCreate) -> HospitalRead:
    new_id = uuid4()
    sql = """
        INSERT INTO hospitals (id, name, city, state, phone, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    with db_cursor() as cur:
        cur.execute(
            sql,
            (
                str(new_id),
                h.name,
                h.city,
                h.state,
                h.phone,
                h.status.value,
            ),
        )
        cur.execute(
            """
            SELECT id, name, city, state, phone, status,
                   created_at, updated_at
            FROM hospitals
            WHERE id = %s
            """,
            (str(new_id),),
        )
        row = cur.fetchone()

    return HospitalRead(**row)


def get_hospital(hospital_id: UUID) -> HospitalRead | None:
    sql = """
        SELECT id, name, city, state, phone, status,
               created_at, updated_at
        FROM hospitals
        WHERE id = %s
    """
    with db_cursor() as cur:
        cur.execute(sql, (str(hospital_id),))
        row = cur.fetchone()

    if not row:
        return None
    return HospitalRead(**row)


def update_hospital(hospital_id: UUID, patch: HospitalUpdate) -> HospitalRead | None:
    parts: list[str] = []
    params: list[object] = []

    if patch.name is not None:
        parts.append("name = %s")
        params.append(patch.name)
    if patch.city is not None:
        parts.append("city = %s")
        params.append(patch.city)
    if patch.state is not None:
        parts.append("state = %s")
        params.append(patch.state)
    if patch.phone is not None:
        parts.append("phone = %s")
        params.append(patch.phone)
    if patch.status is not None:
        parts.append("status = %s")
        params.append(patch.status.value)

    if not parts:
        return get_hospital(hospital_id)

    sql = f"""
        UPDATE hospitals
        SET {', '.join(parts)}, updated_at = NOW()
        WHERE id = %s
    """
    params.append(str(hospital_id))

    with db_cursor() as cur:
        cur.execute(sql, params)

    return get_hospital(hospital_id)


def delete_hospital(hospital_id: UUID) -> bool:
    sql = "DELETE FROM hospitals WHERE id = %s"
    with db_cursor() as cur:
        cur.execute(sql, (str(hospital_id),))
        return cur.rowcount > 0
