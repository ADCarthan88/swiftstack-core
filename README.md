# SwiftStack ⚡

**Generate production-ready FastAPI projects from plain English.**

Describe your data model in natural language — get a complete, working API scaffold in seconds.

```
swiftstack generate --prompt "Build a blog with User and Post entities"
```

```
Built a blog with User and Post entities.
  ✓  blog_api/models.py
  ✓  blog_api/schemas.py
  ✓  blog_api/routers.py
  ✓  blog_api/main.py
  ✓  blog_api/requirements.txt

✅ Done! Project written to: blog_api/
```

---

## Install

```bash
pip install swiftstack
```

Or from source:

```bash
git clone https://github.com/ADCarthan88/swiftstack-core.git
cd swiftstack-core
pip install -e .
```

---

## Usage

### Generate from a prompt

```bash
swiftstack generate --prompt "Build a task manager with Project, Task, and User entities"
```

### Use a built-in template

```bash
swiftstack generate --template blog
swiftstack generate --template ecommerce --out ./my-shop
swiftstack generate --template taskmanager
```

### List templates

```bash
swiftstack templates
```

---

## Example prompt format

```
Build a Clinical Trial API with:

1. **Organization**
   - name, region, complianceTier

2. **User**
   - firstName, lastName, email, role
   - belongsTo: Organization

3. **Trial**
   - title, phase, startDate, status
   - belongsTo: Organization
```

---

## What's generated

Each run produces:

| File | Contents |
|---|---|
| `models.py` | SQLAlchemy ORM models with modern `declarative_base` |
| `schemas.py` | Pydantic v2 schemas (Create / Update / Response) |
| `routers.py` | FastAPI CRUD routers with pagination |
| `main.py` | FastAPI app with CORS, health check, lifespan |
| `requirements.txt` | Pinned dependencies |

---

## Open-source limits

This edition supports **up to 3 entities** per generation.

For production use you likely need:
- More than 3 entities
- Automatic FK/relationship columns (`organizatin_id`, `trial_id`, etc.)
- Multi-framework output (Flask, Django REST, Go, Node.js)
- HIPAA / PCI compliance field detection
- OpenAPI spec export

**→ Full hosted version: https://swiftstackapi.up.railway.app**

Send a POST to `/api/generate` with your prompt — no install required.

---

## Development

```bash
git clone https://github.com/ADCarthan88/swiftstack-core.git
cd swiftstack-core
pip install -e .
python -c "from swiftstack import generate; print(generate('Blog with User and Post')['models.py'])"
```

---

## License

MIT — use it freely, fork it, build on it.

If SwiftStack saved you time, consider [sponsoring](https://github.com/sponsors/ADCarthan88) or trying the [hosted tier](https://swiftstackapi.up.railway.app).
