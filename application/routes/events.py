from sanic import Blueprint, response
from application.database.db import fetch_all, fetch_one

bp = Blueprint("events", url_prefix="/events")


@bp.route("/", methods=["GET"])
async def get_all_events(request):
    events = await fetch_all(request.app.ctx.db, "SELECT * FROM event")

    if not events:
        return response.json({"message": "No events found"}, status=404)

    return response.json(events)


@bp.route("/<event_id>", methods=["GET"])
async def get_event_by_id(request, event_id):
    event = await fetch_one(
        request.app.ctx.db, "SELECT * FROM event WHERE id = ?", (event_id,)
    )

    if event:
        return response.json(event)
    else:
        return response.json({"error": "Event not found"}, status=404)


@bp.route("/", methods=["POST"])
async def create_event(request):
    event_data = request.json
    # Your code to validate and save the event to the database

    return response.json(event_data, status=201)


@bp.route("/<event_id>", methods=["PATCH"])
async def update_event(request, event_id):
    event_data = request.json
    # Your code to validate and update the event in the database

    return response.json(event_data)


@bp.route("/<event_id>", methods=["DELETE"])
async def delete_event(request, event_id):
    # Your code to delete the event with the given ID from the database

    return response.empty(status=204)
