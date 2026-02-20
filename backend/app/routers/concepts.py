"""Concept CRUD endpoints for grammatical concepts (cases, verb types, etc.)."""

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models_db import Concept

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.get("")
async def list_concepts(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List concepts with optional pagination."""
    stmt = (
        select(Concept)
        .order_by(Concept.priority.desc(), Concept.name)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    concepts = result.scalars().all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "examples": json.loads(c.examples) if c.examples else None,
            "tags": json.loads(c.tags) if c.tags else [],
            "priority": c.priority,
            "times_served": c.times_served,
        }
        for c in concepts
    ]


@router.get("/{concept_id}")
async def get_concept(
    concept_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single concept by ID."""
    stmt = select(Concept).where(Concept.id == concept_id)
    result = await db.execute(stmt)
    c = result.scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail="Concept not found")
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "examples": json.loads(c.examples) if c.examples else None,
        "tags": json.loads(c.tags) if c.tags else [],
        "priority": c.priority,
        "times_served": c.times_served,
        "total_score": c.total_score,
        "last_score": c.last_score,
        "last_served": c.last_served.isoformat() if c.last_served else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


@router.post("")
async def create_concept(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a concept.
    Body: {"name": "...", "description": "...", "tags": [...]}
    """
    name = (request.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    concept = Concept(
        id=str(uuid.uuid4()),
        name=name,
        description=request.get("description"),
        examples=json.dumps(request.get("examples", [])) if request.get("examples") else None,
        tags=json.dumps(request.get("tags", [])),
        priority=float(request.get("priority", 1.0)),
    )
    db.add(concept)
    await db.commit()
    await db.refresh(concept)
    return {
        "id": concept.id,
        "name": concept.name,
        "description": concept.description,
        "priority": concept.priority,
    }


@router.put("/{concept_id}")
async def update_concept(
    concept_id: str,
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update a concept."""
    stmt = select(Concept).where(Concept.id == concept_id)
    result = await db.execute(stmt)
    concept = result.scalars().first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    if "name" in request and request["name"]:
        concept.name = request["name"].strip()
    if "description" in request:
        concept.description = request["description"]
    if "examples" in request:
        concept.examples = json.dumps(request["examples"]) if request["examples"] else None
    if "tags" in request:
        concept.tags = json.dumps(request["tags"])
    if "priority" in request:
        concept.priority = float(request["priority"])

    await db.commit()
    await db.refresh(concept)
    return {"id": concept.id, "name": concept.name, "status": "updated"}


@router.delete("/{concept_id}")
async def delete_concept(
    concept_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a concept."""
    stmt = select(Concept).where(Concept.id == concept_id)
    result = await db.execute(stmt)
    concept = result.scalars().first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    await db.delete(concept)
    await db.commit()
    return {"status": "deleted", "id": concept_id}
