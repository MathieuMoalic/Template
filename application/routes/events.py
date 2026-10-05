from slugify import slugify
from aiosqlite import Error
from pydantic import ValidationError
from sanic import Blueprint
from sanic.response import json, text

from application.database.db import execute_query, fetch_all, fetch_one
from application.schemas.schemas import EventCreate, EventUpdate

bp = Blueprint("events", url_prefix="/events")


@bp.route("/", methods=["GET"])
async def get_all_events(request) -> json:
    try:
        events = await fetch_all(request.app.ctx.db, "SELECT * FROM event")
    except Error as e:
        return json({"message": f"An error occurred: {e}"}, 500)

    if not events:
        return json({"message": "No events found"}, 404)

    return json(events)


@bp.route("/<event_id:int>", methods=["GET"])
async def get_event_by_id(request, event_id: int) -> json:
    try:
        event = await fetch_one(
            request.app.ctx.db, "SELECT * FROM event WHERE id = ?", (event_id,)
        )
    except Error as e:
        return json({"message": f"An error occurred: {e}"}, 500)

    if not event:
        return json({"message": "Event not found"}, 404)

    return json(event)


@bp.route("/", methods=["POST"])
async def create_event(request) -> json:
    try:
        event = EventCreate(**request.json).model_dump()

        if not event.get("slug"):
            event["slug"] = slugify(event["name"])

    except ValidationError as e:
        return json({"message": f"Invalid data: {e.errors()}"}, 400)

    try:
        await execute_query(
            request.app.ctx.db,
            """
            INSERT INTO event (
                name,
                active,
                slug,
                type,
                status,
                start_time,
                actual_start_time,
                sport_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["name"],
                event["active"],
                event["slug"],
                event["type"],
                event["status"],
                event["start_time"],
                event["actual_start_time"],
                event["sport_id"],
            ),
        )
    except Error as e:
        return json({"message": f"An error occurred: {e}"}, 500)

    return json({"message": "Event created successfully"}, 201)


@bp.route("/<event_id:int>", methods=["PATCH"])
async def update_event(request, event_id: int):
    event_data = EventUpdate(**request.json).model_dump()
    query = "UPDATE event SET "
    values = []
    for key, value in event_data.items():
        if value is None:
            continue
        query += f"{key} = ?, "
        values.append(value)

    query = query.rstrip(", ") + " WHERE id = ?"
    values.append(event_id)

    try:
        await execute_query(request.app.ctx.db, query, tuple(values))
    except Error as e:
        return json({"message": f"An error occurred: {e}"}, 500)

    return json({"message": "Event updated successfully"})


@bp.route("/<event_id:int>", methods=["DELETE"])
async def delete_event(request, event_id: int):
    try:
        await execute_query(
            request.app.ctx.db, "DELETE FROM event WHERE id = ?", (event_id,)
        )
    except Error as e:
        return json({"message": f"An error occurred: {e}"}, 500)
    return text("", 204)
