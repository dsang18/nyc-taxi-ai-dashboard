from sqlalchemy import func, extract
from app.db.database import SessionLocal
from app.models.taxi_trip import TaxiTrip
from datetime import datetime, timedelta


def apply_filters(
    query,
    start_date=None,
    end_date=None,
    payment_type=None,
    pickup_zone=None,
    dropoff_zone=None
):

    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")

        query = query.filter(
            TaxiTrip.pickup_datetime >= start
        )

    if end_date:
        end = (
            datetime.strptime(end_date, "%Y-%m-%d")
            + timedelta(days=1)
        )

        query = query.filter(
            TaxiTrip.pickup_datetime < end
        )

    if payment_type:
        query = query.filter(
            TaxiTrip.payment_type == payment_type
        )

    if pickup_zone:
        query = query.filter(
            TaxiTrip.pickup_location_id == int(pickup_zone)
        )

    if dropoff_zone:
        query = query.filter(
            TaxiTrip.dropoff_location_id == int(dropoff_zone)
        )

    return query


def get_filter_options():

    db = SessionLocal()

    try:
        min_date, max_date = (
            db.query(
                func.min(TaxiTrip.pickup_datetime),
                func.max(TaxiTrip.pickup_datetime)
            )
            .one()
        )

        payment_types = (
            db.query(TaxiTrip.payment_type)
            .filter(TaxiTrip.payment_type.isnot(None))
            .distinct()
            .order_by(TaxiTrip.payment_type)
            .all()
        )

        pickup_zones = (
            db.query(TaxiTrip.pickup_location_id)
            .filter(TaxiTrip.pickup_location_id.isnot(None))
            .distinct()
            .order_by(TaxiTrip.pickup_location_id)
            .all()
        )

        dropoff_zones = (
            db.query(TaxiTrip.dropoff_location_id)
            .filter(TaxiTrip.dropoff_location_id.isnot(None))
            .distinct()
            .order_by(TaxiTrip.dropoff_location_id)
            .all()
        )

        return {
            "min_date": min_date.strftime("%Y-%m-%d"),
            "max_date": max_date.strftime("%Y-%m-%d"),

            "payment_types": [
                row[0]
                for row in payment_types
            ],

            "pickup_zones": [
                row[0]
                for row in pickup_zones
            ],

            "dropoff_zones": [
                row[0]
                for row in dropoff_zones
            ]
        }

    finally:
        db.close()


def get_kpis(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None) -> dict:
    with SessionLocal() as session:
        results = session.query(
                func.count().label("total_trips"),
                func.sum(TaxiTrip.total_amount).label("total_revenue"),
                func.avg(TaxiTrip.total_amount).label("avg_trip_amount"),
                func.avg(TaxiTrip.trip_distance).label("avg_trip_distance"),
            )

        results = apply_filters(
            results,
            start_date,
            end_date,
            payment_type,
            pickup_zone,
            dropoff_zone
        )

        results = (results).first()

        if results:
            result_dict = results._asdict()
        else:
            result_dict = {
                "total_trips": 0,
                "total_revenue": 0.0,
                "avg_trip_amount": 0.0,
                "avg_trip_distance": 0.0
            }

    return result_dict


def get_trips_by_hour(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None) -> list:
    db = SessionLocal()

    try:
        results = db.query(
                extract("hour", TaxiTrip.pickup_datetime).label("hour"),
                func.count(TaxiTrip.id).label("trip_count")
            )

        results = apply_filters(
            results,
            start_date,
            end_date,
            payment_type,
            pickup_zone,
            dropoff_zone
        )

        results = (results).group_by(extract("hour", TaxiTrip.pickup_datetime)).order_by(extract("hour", TaxiTrip.pickup_datetime)).all()
        

        return [
            {
                "hour": int(row.hour),
                "trip_count": row.trip_count
            }
            for row in results
        ]

    finally:
        db.close()


def get_trips_by_day(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        results = db.query(
                func.date(TaxiTrip.pickup_datetime).label("date"),
                func.count(TaxiTrip.id).label("trip_count")
            )

        results = apply_filters(
            results,
            start_date,
            end_date,
            payment_type,
            pickup_zone,
            dropoff_zone
        )

        results = (results
            .group_by(func.date(TaxiTrip.pickup_datetime))
            .order_by(func.date(TaxiTrip.pickup_datetime))
            .all())
        

        return [
            {
                "date": str(row.date),
                "trip_count": row.trip_count
            }
            for row in results
        ]

    finally:
        db.close()


def get_payment_analysis(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        results = db.query(
                TaxiTrip.payment_type,
                func.count(TaxiTrip.id).label("trip_count"),
                func.sum(TaxiTrip.total_amount).label("total_revenue")
            )
        

        results = apply_filters(
            results,
            start_date,
            end_date,
            payment_type,
            pickup_zone,
            dropoff_zone
        )

        results = (results
            .group_by(TaxiTrip.payment_type)
            .order_by(func.count(TaxiTrip.id).desc())
            .all())

        return [
            {
                "payment_type": row.payment_type,
                "trip_count": row.trip_count,
                "total_revenue": float(row.total_revenue or 0)
            }
            for row in results
        ]

    finally:
        db.close()


def get_top_locations(location_type, limit=10, start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        if location_type == "pickup":
            location_column = TaxiTrip.pickup_location_id
        else:
            location_column = TaxiTrip.dropoff_location_id

        results = db.query(
                location_column.label("location_id"),
                func.count(TaxiTrip.id).label("trip_count")
            )

        results = apply_filters(
            results,
            start_date,
            end_date,
            payment_type,
            pickup_zone,
            dropoff_zone
        )

        results = (results.filter(location_column.isnot(None))
            .group_by(location_column)
            .order_by(func.count(TaxiTrip.id).desc())
            .limit(limit)
            .all())
        

        return [
            {
                "location_id": row.location_id,
                "trip_count": row.trip_count
            }
            for row in results
        ]

    finally:
        db.close()


def get_revenue_by_day(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        results = db.query(
                func.date(TaxiTrip.pickup_datetime).label("date"),
                func.sum(TaxiTrip.total_amount).label("revenue")
            )

        results = apply_filters(
            results,
            start_date,
            end_date,
            payment_type,
            pickup_zone,
            dropoff_zone
        )

        results = (results
            .group_by(func.date(TaxiTrip.pickup_datetime))
            .order_by(func.date(TaxiTrip.pickup_datetime))
            .all())
        

        return [
            {
                "date": str(row.date),
                "revenue": float(row.revenue or 0)
            }
            for row in results
        ]

    finally:
        db.close()


def get_revenue_by_hour(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        results = db.query(
                extract("hour", TaxiTrip.pickup_datetime).label("hour"),
                func.sum(TaxiTrip.total_amount).label("revenue")
            )

        results = apply_filters(
            results,
            start_date,
            end_date,
            payment_type,
            pickup_zone,
            dropoff_zone
        )
        results = (results
            .group_by(extract("hour", TaxiTrip.pickup_datetime))
            .order_by(extract("hour", TaxiTrip.pickup_datetime))
            .all())
        

        return [
            {
                "hour": int(row.hour),
                "revenue": float(row.revenue or 0)
            }
            for row in results
        ]

    finally:
        db.close()


def get_avg_revenue_by_hour(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        results = db.query(
                extract("hour", TaxiTrip.pickup_datetime).label("hour"),
                func.avg(TaxiTrip.total_amount).label("avg_revenue")
            )

        results = apply_filters(
                    results,
                    start_date,
                    end_date,
                    payment_type,
                    pickup_zone,
                    dropoff_zone
                )

        results = (results
            .group_by(extract("hour", TaxiTrip.pickup_datetime))
            .order_by(extract("hour", TaxiTrip.pickup_datetime))
            .all())
        

        return [
            {
                "hour": int(row.hour),
                "avg_revenue": float(row.avg_revenue or 0)
            }
            for row in results
        ]

    finally:
        db.close()


def get_revenue_by_pickup_zone(limit=10, start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        results = db.query(
                TaxiTrip.pickup_location_id.label("location_id"),
                func.count(TaxiTrip.id).label("trip_count"),
                func.sum(TaxiTrip.total_amount).label("revenue")
            )

        results = apply_filters(
                    results,
                    start_date,
                    end_date,
                    payment_type,
                    pickup_zone,
                    dropoff_zone
                )

        results = (results
            .filter(TaxiTrip.pickup_location_id.isnot(None))
            .group_by(TaxiTrip.pickup_location_id)
            .order_by(func.sum(TaxiTrip.total_amount).desc())
            .limit(limit)
            .all())
        

        return [
            {
                "location_id": row.location_id,
                "trip_count": row.trip_count,
                "revenue": float(row.revenue or 0)
            }
            for row in results
        ]

    finally:
        db.close()


def get_revenue_by_dropoff_zone(limit=10, start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        results = db.query(
                TaxiTrip.dropoff_location_id.label("location_id"),
                func.count(TaxiTrip.id).label("trip_count"),
                func.sum(TaxiTrip.total_amount).label("revenue")
            )

        results = apply_filters(
                    results,
                    start_date,
                    end_date,
                    payment_type,
                    pickup_zone,
                    dropoff_zone
                )

        results = (results
            .filter(TaxiTrip.dropoff_location_id.isnot(None))
            .group_by(TaxiTrip.dropoff_location_id)
            .order_by(func.sum(TaxiTrip.total_amount).desc())
            .limit(limit)
            .all())
        

        return [
            {
                "location_id": row.location_id,
                "trip_count": row.trip_count,
                "revenue": float(row.revenue or 0)
            }
            for row in results
        ]

    finally:
        db.close()
