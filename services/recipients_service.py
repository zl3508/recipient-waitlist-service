# services/recipients_service.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID, uuid4

from models.recipient import RecipientRead, RecipientCreate, RecipientUpdate
from models.enums import BloodType, CommonStatus
from services.db import db_cursor


def list_recipients(
    blood_type: Optional[BloodType],
    status_q: Optional[CommonStatus],
    hospital_id: Optional[UUID],
    limit: int = 50,
) -> List[RecipientRead]:
    sql = """
        SELECT id, full_name, dob, blood_type, status,
               primary_hospital_id, created_at, updated_at
        FROM recipients
    """
    where: list[str] = []
    params: list[object] = []

    if blood_type is not None:
        where.append("blood_type = %s")
        params.append(blood_type.value)
    if status_q is not None:
        where.append("status = %s")
        params.append(status_q.value)
    if hospital_id is not None:
        where.append("primary_hospital_id = %s")
        params.append(str(hospital_id))

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)

    with db_cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [RecipientRead(**row) for row in rows]


def create_recipient(r: RecipientCreate) -> RecipientRead:
    new_id = uuid4()
    sql = """
        INSERT INTO recipients (
            id, full_name, dob, blood_type, status,
            primary_hospital_id, created_at, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    with db_cursor() as cur:
        cur.execute(
            sql,
            (
                str(new_id),
                r.full_name,
                r.dob,
                r.blood_type.value,
                r.status.value,
                str(r.primary_hospital_id) if r.primary_hospital_id else None,
            ),
        )
        cur.execute(
            """
            SELECT id, full_name, dob, blood_type, status,
                   primary_hospital_id, created_at, updated_at
            FROM recipients
            WHERE id = %s
            """,
            (str(new_id),),
        )
        row = cur.fetchone()

    return RecipientRead(**row)


def get_recipient(recipient_id: UUID) -> RecipientRead | None:
    sql = """
        SELECT id, full_name, dob, blood_type, status,
               primary_hospital_id, created_at, updated_at
        FROM recipients
        WHERE id = %s
    """
    with db_cursor() as cur:
        cur.execute(sql, (str(recipient_id),))
        row = cur.fetchone()

    if not row:
        return None
    return RecipientRead(**row)


def update_recipient(recipient_id: UUID, patch: RecipientUpdate) -> RecipientRead | None:
    parts: list[str] = []
    params: list[object] = []

    if patch.full_name is not None:
        parts.append("full_name = %s")
        params.append(patch.full_name)
    if patch.dob is not None:
        parts.append("dob = %s")
        params.append(patch.dob)
    if patch.blood_type is not None:
        parts.append("blood_type = %s")
        params.append(patch.blood_type.value)
    if patch.status is not None:
        parts.append("status = %s")
        params.append(patch.status.value)
    if patch.primary_hospital_id is not None:
        parts.append("primary_hospital_id = %s")
        params.append(str(patch.primary_hospital_id))

    if not parts:
        return get_recipient(recipient_id)

    sql = f"""
        UPDATE recipients
        SET {', '.join(parts)}, updated_at = NOW()
        WHERE id = %s
    """
    params.append(str(recipient_id))

    with db_cursor() as cur:
        cur.execute(sql, params)

    return get_recipient(recipient_id)


def delete_recipient(recipient_id: UUID) -> bool:
    sql = "DELETE FROM recipients WHERE id = %s"
    with db_cursor() as cur:
        cur.execute(sql, (str(recipient_id),))
        return cur.rowcount > 0
