# Reedox - Oboe Reed Tracking System

A Django REST API backend for tracking oboe reeds, their usage, playing qualities, and modifications to help analyze what gives you the best outcomes for your reedmaking.

## Features

### Core Models

- **Reed**: Track basic reed information including construction details, status, and total playing time
- **UsageSession**: Record each time you use a reed with start/end times and context (practice, rehearsal, performance)
- **QualitySnapshot**: Take snapshots of playing qualities at different points in a reed's life (tone, response, intonation, stability, etc.)
- **Modification**: Track changes made to reeds (clips, scraping, wire adjustments) with goals and success ratings

### Analytics

- Individual reed analytics with quality averages, usage statistics, and modification breakdown
- Overall summary analytics across all reeds
- Status tracking for reed lifecycle (new → breaking in → prime → declining → retired)

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jsteinbecker/reedox.git
cd reedox
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser (for Django admin access):
```bash
python manage.py createsuperuser
```

5. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Reeds
- `GET /api/reeds/` - List all reeds
- `POST /api/reeds/` - Create a new reed
- `GET /api/reeds/{id}/` - Get reed details with all related data
- `PATCH /api/reeds/{id}/` - Update a reed
- `DELETE /api/reeds/{id}/` - Delete a reed
- `GET /api/reeds/{id}/analytics/` - Get analytics for a specific reed
- `GET /api/reeds/summary/` - Get overall summary across all reeds

### Usage Sessions
- `GET /api/usage-sessions/` - List all usage sessions
- `POST /api/usage-sessions/` - Create a new usage session
- `GET /api/usage-sessions/{id}/` - Get session details
- `PATCH /api/usage-sessions/{id}/` - Update a session
- `DELETE /api/usage-sessions/{id}/` - Delete a session

### Quality Snapshots
- `GET /api/quality-snapshots/` - List all quality snapshots
- `POST /api/quality-snapshots/` - Create a new quality snapshot
- `GET /api/quality-snapshots/{id}/` - Get snapshot details
- `PATCH /api/quality-snapshots/{id}/` - Update a snapshot
- `DELETE /api/quality-snapshots/{id}/` - Delete a snapshot

### Modifications
- `GET /api/modifications/` - List all modifications
- `POST /api/modifications/` - Create a new modification
- `GET /api/modifications/{id}/` - Get modification details
- `PATCH /api/modifications/{id}/` - Update a modification
- `DELETE /api/modifications/{id}/` - Delete a modification

## Usage Examples

### Create a Reed
```bash
curl -X POST http://localhost:8000/api/reeds/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Reed #42",
    "status": "new",
    "cane_source": "Rigotti",
    "shape": "Mack+",
    "gouge_thickness": 0.58
  }'
```

### Add a Usage Session
```bash
curl -X POST http://localhost:8000/api/usage-sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "reed": 1,
    "start_time": "2026-02-01T10:00:00Z",
    "end_time": "2026-02-01T11:30:00Z",
    "context": "Practice"
  }'
```

### Record a Quality Snapshot
```bash
curl -X POST http://localhost:8000/api/quality-snapshots/ \
  -H "Content-Type: application/json" \
  -d '{
    "reed": 1,
    "tone_quality": 8,
    "response": 7,
    "intonation": 9,
    "stability": 8,
    "ease_of_playing": 8,
    "overall_rating": 8,
    "notes": "Playing well after breaking in"
  }'
```

### Record a Modification
```bash
curl -X POST http://localhost:8000/api/modifications/ \
  -H "Content-Type: application/json" \
  -d '{
    "reed": 1,
    "modification_type": "clip",
    "description": "Clipped 0.5mm to improve pitch",
    "goal": "Lower pitch to 440Hz",
    "success_rating": 9
  }'
```

### Get Reed Analytics
```bash
curl http://localhost:8000/api/reeds/1/analytics/
```

## Django Admin

Access the Django admin interface at `http://localhost:8000/admin/` to manage data through a user-friendly web interface.

Features:
- View and manage all reeds, sessions, snapshots, and modifications
- Inline editing of related records
- Filter and search capabilities
- Visual organization with fieldsets

## Development

### Running Tests
```bash
python manage.py test reeds
```

### Making Changes
1. Update models in `reeds/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`

## Data Model

### Reed
- Basic info: name, status, created_date
- Construction: cane_source, shape, gouge_thickness
- Tracking: total_play_time_minutes
- Related: usage_sessions, quality_snapshots, modifications

### UsageSession
- Time tracking: start_time, end_time, duration_minutes (auto-calculated)
- Context: practice, rehearsal, performance, etc.

### QualitySnapshot
- Ratings (1-10 scale): tone_quality, response, intonation, stability, ease_of_playing, overall_rating
- Timestamp for tracking quality changes over time

### Modification
- Type: clip, scrape (tip/heart/back/rails), wire adjustment, etc.
- Tracking: description, goal, success_rating
- Helps analyze which modifications improve performance

## Security Notes

**Important**: This project is configured for development use. Before deploying to production:

1. **Secret Key**: Move `SECRET_KEY` to environment variables and never commit it to version control
2. **Debug Mode**: Set `DEBUG = False` in production
3. **Allowed Hosts**: Configure `ALLOWED_HOSTS` with your production domains
4. **CORS**: Restrict `CORS_ALLOW_ALL_ORIGINS` to specific allowed origins
5. **Authentication**: Implement proper authentication and permission classes for the API
6. **Database**: Use a production database (PostgreSQL, MySQL) instead of SQLite

## License

This project is licensed under the terms in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
