"""Concept CRUD endpoints for grammatical concepts (cases, verb types, etc.)."""

import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models_db import Concept, UserConceptProgress

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/concepts", tags=["concepts"])


@router.get("")
async def list_concepts(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List concepts with optional pagination. Pass user_id to include mastery."""
    stmt = (
        select(Concept)
        .order_by(Concept.priority.desc(), Concept.name)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    concepts = result.scalars().all()

    # Batch-fetch mastery for user if provided
    mastery_map = {}
    if user_id:
        prog_stmt = select(UserConceptProgress).where(
            UserConceptProgress.user_id == user_id
        )
        prog_result = await db.execute(prog_stmt)
        for p in prog_result.scalars().all():
            mastery_map[p.concept_id] = {"mastery": p.mastery, "exercise_count": p.exercise_count}

    return [
        {
            "id": c.id,
            "name": c.name,
            "name_fi": c.name_fi,
            "description": c.description,
            "examples": json.loads(c.examples) if c.examples else None,
            "tags": json.loads(c.tags) if c.tags else [],
            "frequency": c.frequency,
            "difficulty": c.difficulty,
            "priority": c.priority,
            "times_served": c.times_served,
            "mastery": mastery_map.get(c.id, {}).get("mastery") if user_id else None,
            "exercise_count": mastery_map.get(c.id, {}).get("exercise_count") if user_id else None,
        }
        for c in concepts
    ]


@router.get("/{concept_id}")
async def get_concept(
    concept_id: str,
    user_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get a single concept by ID. Pass user_id to include mastery."""
    stmt = select(Concept).where(Concept.id == concept_id)
    result = await db.execute(stmt)
    c = result.scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail="Concept not found")

    resp = {
        "id": c.id,
        "name": c.name,
        "name_fi": c.name_fi,
        "description": c.description,
        "examples": json.loads(c.examples) if c.examples else None,
        "tags": json.loads(c.tags) if c.tags else [],
        "frequency": c.frequency,
        "difficulty": c.difficulty,
        "priority": c.priority,
        "times_served": c.times_served,
        "total_score": c.total_score,
        "last_score": c.last_score,
        "last_served": c.last_served.isoformat() if c.last_served else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }

    if user_id:
        prog_stmt = select(UserConceptProgress).where(
            UserConceptProgress.user_id == user_id,
            UserConceptProgress.concept_id == concept_id,
        )
        prog_result = await db.execute(prog_stmt)
        progress = prog_result.scalars().first()
        resp["mastery"] = progress.mastery if progress else 0.0
        resp["exercise_count"] = progress.exercise_count if progress else 0

    return resp


@router.post("")
async def create_concept(
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a concept.
    Body: {"name": "...", "name_fi": "...", "description": "...", "frequency": 3, "difficulty": 2, "tags": [...]}
    """
    name = (request.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    concept = Concept(
        id=str(uuid.uuid4()),
        name=name,
        name_fi=request.get("name_fi"),
        description=request.get("description"),
        examples=json.dumps(request.get("examples", [])) if request.get("examples") else None,
        tags=json.dumps(request.get("tags", [])),
        frequency=request.get("frequency"),
        difficulty=request.get("difficulty"),
        priority=float(request.get("priority", 1.0)),
    )
    db.add(concept)
    await db.commit()
    await db.refresh(concept)
    return {
        "id": concept.id,
        "name": concept.name,
        "name_fi": concept.name_fi,
        "frequency": concept.frequency,
        "difficulty": concept.difficulty,
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
    if "name_fi" in request:
        concept.name_fi = request["name_fi"]
    if "description" in request:
        concept.description = request["description"]
    if "examples" in request:
        concept.examples = json.dumps(request["examples"]) if request["examples"] else None
    if "tags" in request:
        concept.tags = json.dumps(request["tags"])
    if "frequency" in request:
        concept.frequency = request["frequency"]
    if "difficulty" in request:
        concept.difficulty = request["difficulty"]
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
