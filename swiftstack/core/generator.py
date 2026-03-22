"""
SwiftStack Core Generator — limited open-source edition.

Generates a basic FastAPI scaffold from a plain-English description.
Supports up to 3 entities per generation.

For unlimited entities, multi-framework output (Flask, DRF, Go, Node),
relationship inference, HIPAA/PCI compliance detection, and hosted API
access, see the full version at https://swiftstackapi.up.railway.app
"""

from __future__ import annotations

import re
import os
from typing import Dict, List, Optional


# ── Hard limit for the open-core edition ────────────────────────────────────
MAX_ENTITIES = 3
HOSTED_URL = "https://swiftstackapi.up.railway.app"


# ── Minimal field-type inference ─────────────────────────────────────────────

def _snake(name: str) -> str:
    """camelCase / PascalCase → snake_case"""
    s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', name)
    return s.lower()


def _col_type(field: str) -> str:
    f = field.lower()
    if any(k in f for k in ("_at", "timestamp", "datetime")): return "DateTime"
    if any(k in f for k in ("_date", "date", "birthday")):    return "Date"
    if any(k in f for k in ("is_", "has_", "enabled", "active", "verified")): return "Boolean"
    if any(k in f for k in ("price", "amount", "score", "rating")): return "Float"
    if any(k in f for k in ("count", "qty", "quantity", "age")): return "Integer"
    if any(k in f for k in ("description", "content", "notes", "body")): return "Text"
    if "email" in f: return "String(255)"
    if "phone" in f: return "String(20)"
    return "String(255)"


def _pluralize(word: str) -> str:
    if word.endswith('y') and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    if word.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    return word + 's'


# ── Prompt parser (basic — no relationship inference) ────────────────────────

def parse_entities(prompt: str) -> Dict[str, List[str]]:
    """
    Extract up to MAX_ENTITIES entities and their fields from a prompt.

    Supported formats:
      - "User with name, email, role"
      - "1. **User** - name, email, role"
      - "User: name, email, role"
    """
    entities: Dict[str, List[str]] = {}

    # Numbered bold markdown: "1. **User**"
    numbered = re.compile(r'^\s*\d+[.)]\s*\*{1,2}([A-Z][a-zA-Z]+)\*{1,2}', re.MULTILINE)
    # Simple colon: "User:"
    colon = re.compile(r'^([A-Z][a-zA-Z]+):\s*$', re.MULTILINE)

    lines = prompt.splitlines()
    current: Optional[str] = None

    for line in lines:
        # Detect entity header
        m = numbered.match(line) or colon.match(line.strip())
        if m:
            name = m.group(1).strip()
            if len(entities) < MAX_ENTITIES:
                current = name
                entities[current] = []
            else:
                current = None  # over limit — silently skip
            continue

        if current is None:
            continue

        stripped = re.sub(r'^[-*•]\s*', '', line.strip())
        if not stripped:
            continue

        # Skip relationship annotations
        if re.match(r'(?:hasMany|belongsTo|has_many|belongs_to)\b', stripped, re.I):
            continue

        # Comma-separated or single field
        if ',' in stripped:
            for part in stripped.split(','):
                field = _snake(re.match(r'(\w+)', part.strip()).group(1)) if re.match(r'(\w+)', part.strip()) else None
                if field and field not in entities[current]:
                    entities[current].append(field)
        else:
            fm = re.match(r'(\w+)', stripped)
            if fm:
                field = _snake(fm.group(1))
                if field not in entities[current]:
                    entities[current].append(field)

    if len(entities) == MAX_ENTITIES and _count_remaining(prompt, entities) > 0:
        entities['_limit_hit'] = []

    return entities


def _count_remaining(prompt: str, found: dict) -> int:
    """Rough count of entity headers not yet in found."""
    all_headers = re.findall(r'^\s*\d+[.)]\s*\*{1,2}([A-Z][a-zA-Z]+)\*{1,2}', prompt, re.MULTILINE)
    return sum(1 for h in all_headers if h not in found)


# ── Code generators ──────────────────────────────────────────────────────────

def generate_models(entities: Dict[str, List[str]]) -> str:
    lines = [
        "from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Float, ForeignKey, create_engine",
        "from sqlalchemy.orm import sessionmaker, declarative_base",
        "from datetime import datetime, timezone",
        "import os",
        "",
        'DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")',
        'engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})',
        "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)",
        "Base = declarative_base()",
        "",
        "class BaseModel(Base):",
        "    __abstract__ = True",
        "    id = Column(Integer, primary_key=True, index=True)",
        "    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))",
        "    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))",
        "",
    ]

    for entity, fields in entities.items():
        if entity.startswith('_'):
            continue
        table = _pluralize(_snake(entity))
        lines += [
            f"class {entity}(BaseModel):",
            f'    __tablename__ = "{table}"',
        ]
        for f in fields:
            ct = _col_type(f)
            lines.append(f"    {f} = Column({ct}, nullable=True)")
        lines.append("")

    lines.append("Base.metadata.create_all(bind=engine)")
    return "\n".join(lines) + "\n"


def generate_schemas(entities: Dict[str, List[str]]) -> str:
    lines = [
        "from pydantic import BaseModel",
        "from datetime import datetime",
        "from typing import Optional",
        "",
    ]
    for entity, fields in entities.items():
        if entity.startswith('_'):
            continue
        base_fields = "\n".join(
            f"    {f}: Optional[str] = None" for f in fields
        ) or "    pass"
        lines += [
            f"class {entity}Base(BaseModel):",
            base_fields,
            "",
            f"class {entity}Create({entity}Base):",
            "    pass",
            "",
            f"class {entity}Update(BaseModel):",
            "\n".join(f"    {f}: Optional[str] = None" for f in fields) or "    pass",
            "",
            f"class {entity}({entity}Base):",
            "    id: int",
            "    created_at: datetime",
            "    updated_at: datetime",
            "    class Config:",
            "        from_attributes = True",
            "",
        ]
    return "\n".join(lines) + "\n"


def generate_main(entities: Dict[str, List[str]], api_name: str = "API") -> str:
    entity_names = [e for e in entities if not e.startswith('_')]
    router_vars = [f"router_{e.lower()}" for e in entity_names]
    imports = ", ".join(router_vars)
    includes = "\n".join(f"app.include_router({v})" for v in router_vars)

    return f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup")
    yield
    logger.info("Shutdown")

app = FastAPI(title="{api_name}", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from routers import {imports}
{includes}

@app.get("/health")
async def health():
    return {{"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}}
'''


def generate_routers(entities: Dict[str, List[str]]) -> str:
    lines = [
        "from fastapi import APIRouter, Depends, HTTPException, Query",
        "from sqlalchemy.orm import Session as DBSession",
        "",
        "def get_db():",
        "    from models import SessionLocal",
        "    db = SessionLocal()",
        "    try:",
        "        yield db",
        "    finally:",
        "        db.close()",
        "",
    ]

    for entity, fields in entities.items():
        if entity.startswith('_'):
            continue
        snake = _snake(entity)
        plural = _pluralize(snake)
        var = f"router_{snake}"
        ser = (
            '"id": item.id, '
            + ", ".join(f'"{f}": item.{f}' for f in fields)
            + ', "created_at": item.created_at.isoformat() if item.created_at else None'
        )
        create_kw = ", ".join(f"{f}=data.{f}" for f in fields)

        lines += [
            f'{var} = APIRouter(prefix="/api/{plural}", tags=["{entity}"])',
            "",
            f'@{var}.get("")',
            f"async def list_{plural}(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), db: DBSession = Depends(get_db)):",
            f"    from models import {entity}",
            f"    total = db.query({entity}).count()",
            f"    items = db.query({entity}).offset((page-1)*per_page).limit(per_page).all()",
            f"    return {{\"total\": total, \"items\": [{{{ser}}} for item in items]}}",
            "",
            f'@{var}.get("/{{id}}")',
            f"async def get_{snake}(id: int, db: DBSession = Depends(get_db)):",
            f"    from models import {entity}",
            f"    item = db.query({entity}).filter({entity}.id == id).first()",
            f"    if not item: raise HTTPException(status_code=404, detail=\"{entity} not found\")",
            f"    return {{{ser}}}",
            "",
            f'@{var}.post("", status_code=201)',
            f"async def create_{snake}(data: {entity}Create, db: DBSession = Depends(get_db)):",  # noqa: E501
            f"    from models import {entity}",
            f"    item = {entity}({create_kw})",
            "    db.add(item); db.commit(); db.refresh(item)",
            f"    return {{{ser}}}",
            "",
            f'@{var}.delete("/{{id}}", status_code=204)',
            f"async def delete_{snake}(id: int, db: DBSession = Depends(get_db)):",
            f"    from models import {entity}",
            f"    item = db.query({entity}).filter({entity}.id == id).first()",
            f"    if not item: raise HTTPException(status_code=404, detail=\"{entity} not found\")",
            "    db.delete(item); db.commit()",
            "",
        ]
    # Import schema names at top
    schema_imports = ", ".join(
        f"{e}Create" for e in entities if not e.startswith('_')
    )
    return f"from schemas import {schema_imports}\n\n" + "\n".join(lines) + "\n"


# ── Public API ───────────────────────────────────────────────────────────────

def generate(prompt: str, api_name: str = "API") -> Dict[str, str]:
    """
    Generate a FastAPI scaffold from a plain-English prompt.

    Limited to {MAX_ENTITIES} entities in the open-source edition.
    For more, use the hosted API: {HOSTED_URL}

    Returns a dict of filename → file content.
    """
    entities = parse_entities(prompt)
    limit_hit = '_limit_hit' in entities
    clean = {k: v for k, v in entities.items() if not k.startswith('_')}

    files = {
        "models.py":   generate_models(clean),
        "schemas.py":  generate_schemas(clean),
        "routers.py":  generate_routers(clean),
        "main.py":     generate_main(clean, api_name),
        "requirements.txt": (
            "fastapi==0.104.1\n"
            "uvicorn[standard]==0.24.0\n"
            "sqlalchemy==2.0.23\n"
            "pydantic==2.5.0\n"
            "python-dotenv==1.0.0\n"
        ),
    }

    if limit_hit:
        files["UPGRADE.md"] = (
            f"# More entities detected\n\n"
            f"This open-source edition supports up to **{MAX_ENTITIES} entities**.\n\n"
            f"Your prompt contained additional entities that were not generated.\n\n"
            f"**Upgrade to the full version:** {HOSTED_URL}\n\n"
            f"The hosted API supports:\n"
            f"- Unlimited entities\n"
            f"- Automatic relationship inference (`hasMany`, `belongsTo`)\n"
            f"- Foreign key columns\n"
            f"- Flask, DRF, Go, Node.js, Kotlin targets\n"
            f"- HIPAA / PCI-DSS compliance field detection\n"
            f"- OpenAPI spec export\n"
        )

    return files
