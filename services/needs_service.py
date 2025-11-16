# services/needs_service.py
from __future__ import annotations

from uuid import UUID, uuid4
from typing import Optional, List

from models.need import NeedRead, NeedCreate, NeedUpdate
from models.enums import OrganType, BloodType, NeedStatus
from services.db import db_cursor


def list_needs(
    organ_type: Optional[OrganType],
    status_q: Optional[NeedStatus],
    recipient_id: Optional[UUID],
    limit: int = 50,
) -> List[NeedRead]:
    sql = """
        SELECT id, recipient_id, organ_type, urgency,
               blood_type, status, listed_at, updated_at
        FROM needs
    """
    where: list[str] = []
    params: list[object] = []

    if organ_type is not None:
        where.append("organ_type = %s")
        params.append(organ_type.value)
    if status_q is not None:
        where.append("status = %s")
        params.append(status_q.value)
    if recipient_id is not None:
        where.append("recipient_id = %s")
        params.append(str(recipient_id))

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY listed_at DESC, urgency DESC LIMIT %s"
    params.append(limit)

    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [NeedRead(**row) for row in rows]


def create_need(recipient_id: UUID, n: NeedCreate) -> NeedRead:
    new_id = uuid4()
    sql = """
        INSERT INTO needs (
            id, recipient_id, organ_type, urgency,
            blood_type, status, listed_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    with db_cursor() as cur:
        cur.execute(
            sql,
            (
                str(new_id),
                str(recipient_id),
                n.organ_type.value,
                n.urgency,
                n.blood_type.value,
                n.status.value,
            ),
        )
        cur.execute(
            """
            SELECT id, recipient_id, organ_type, urgency,
                   blood_type, status, listed_at, updated_at
            FROM needs
            WHERE id = %s
            """,
            (str(new_id),),
        )
        row = cur.fetchone()

    return NeedRead(**row)


def get_need(need_id: UUID) -> NeedRead | None:
    sql = """
        SELECT id, recipient_id, organ_type, urgency,
               blood_type, status, listed_at, updated_at
        FROM needs
        WHERE id = %s
    """
    with db_cursor() as cur:
        cur.execute(sql, (str(need_id),))
        row = cur.fetchone()
    if not row:
        return None
    return NeedRead(**row)


def update_need(need_id: UUID, patch: NeedUpdate) -> NeedRead | None:
    parts: list[str] = []
    params: list[object] = []

    if patch.organ_type is not None:
        parts.append("organ_type = %s")
        params.append(patch.organ_type.value)
    if patch.urgency is not None:
        parts.append("urgency = %s")
        params.append(patch.urgency)
    if patch.blood_type is not None:
        parts.append("blood_type = %s")
        params.append(patch.blood_type.value)
    if patch.status is not None:
        parts.append("status = %s")
        params.append(patch.status.value)

    if not parts:
        return get_need(need_id)

    sql = f"""
        UPDATE needs
        SET {', '.join(parts)}, updated_at = NOW()
        WHERE id = %s
    """
    params.append(str(need_id))

    with db_cursor() as cur:
        cur.execute(sql, params)

    return get_need(need_id)


def delete_need(need_id: UUID) -> bool:
    sql = "DELETE FROM needs WHERE id = %s"
    with db_cursor() as cur:
        cur.execute(sql, (str(need_id),))
        return cur.rowcount > 0
