# Cithai — AI Music Generation Platform

Django backend implementing the domain model from Exercise 2.

---

## Quick Start

### 1. Clone & install dependencies

```bash
git clone <https://github.com/Natcha-limsuwan/Cithai.git>
cd cithai
pip install django djangorestframework
```

### 2. Apply migrations

```bash
python manage.py migrate
```

### 3. Seed demo data

```bash
python manage.py seed_data
```

### 4. Create an admin superuser

```bash
python manage.py createsuperuser
```

When prompted for a password you can leave it blank (Google OAuth is used in
production — no passwords are stored).

### 5. Run the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/admin/` | Django Admin — full CRUD for all entities |
| `/api/` | Browsable REST API root |
| `/api/users/` | User CRUD |
| `/api/songs/` | Song CRUD |
| `/api/requests/` | MusicGenerationRequest CRUD |
| `/api/shares/` | ShareLink CRUD |

---

## Domain Entities

| Model | Maps to domain concept |
|-------|------------------------|
| `User` | Authenticated person, Google OAuth identity |
| `Song` | Central entity — stores metadata & generation status |
| `MusicGenerationRequest` | Input data submitted by user; preserved on failure |
| `ShareLink` | Unique token URL for authenticated sharing |

**Enumerations (fixed at design time — A-6):**
`Mood`, `Genre`, `Occasion`, `VoiceType`, `GenerationStatus`

---

## Business Rules Enforced

| Rule | Where enforced |
|------|---------------|
| C-1 Song belongs to exactly one User | ForeignKey with CASCADE |
| C-2 Max 20 songs per User | `Song.save()` + serializer validation |
| C-3 `is_shared = false` by default | model field `default=False` |
| C-4 ShareLink only for Complete songs | `ShareLink.save()` + serializer validation |
| A-1 No passwords stored | `set_unusable_password()` in UserManager |
| A-2 One Request → at most one Song | OneToOneField on MusicGenerationRequest.song |
| A-4 ShareLink is optional (0..1) | OneToOneField, nullable |
| A-5 Only Complete songs can be shared | same as C-4 |
| A-7 Audio stored externally | No file field; only metadata in DB |

---

## REST API — Example Requests

```bash
# List all songs
curl http://127.0.0.1:8000/api/songs/

# Create a song
curl -X POST http://127.0.0.1:8000/api/songs/ \
  -H "Content-Type: application/json" \
  -d '{"user":1,"title":"Chill Vibes","mood":"Calm","genre":"Jazz",
       "occasion":"Anniversary","voice_type":"Instrumental","status":"Pending"}'

# Update status
curl -X PATCH http://127.0.0.1:8000/api/songs/1/ \
  -H "Content-Type: application/json" \
  -d '{"status":"Complete"}'

# Delete
curl -X DELETE http://127.0.0.1:8000/api/songs/1/
```

---

## Project Structure

```
cithai/
├── manage.py
├── README.md
├── db.sqlite3              # SQLite database (dev only)
├── CRUD/
│    ├── api:musicgenerationrequest.png
│    ├── api:shares.png
│    ├── api:songs:1.png
│    ├── api:songs.png
│    └── api:users.png
├── cithai/
│   ├── settings.py
│   └── urls.py
└── core/
    ├── models.py           # Domain entities + enumerations
    ├── serializers.py      # DRF serializers with constraint validation
    ├── views.py            # ModelViewSet CRUD endpoints
    ├── admin.py            # Django Admin registration
    ├── migrations/
    │   └── 0001_initial.py
    └── management/
        └── commands/
            └── seed_data.py
```
