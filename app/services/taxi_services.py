from sqlalchemy import func, extract
from app.db.database import SessionLocal
from app.models.taxi_trip import TaxiTrip
from datetime import datetime, timedelta
import traceback


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


def get_ai_context(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        return {
            "kpis": get_kpis(start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "trip_by_hour": get_trips_by_hour(start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "trip_by_day": get_trips_by_hour(start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "payment_type": get_payment_analysis(start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "top_pickup_zone": get_top_locations("pickup", 10, start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "top_dropoff_zone": get_top_locations("dropoff", 10, start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "revenue_by_day": get_revenue_by_day(start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "revenue_by_hour": get_revenue_by_hour(start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "revenue_by_pickup_zone": get_revenue_by_pickup_zone(10, start_date, end_date, payment_type, pickup_zone, dropoff_zone),
            "revenue_by_dropoff_zone": get_revenue_by_dropoff_zone(10, start_date, end_date, payment_type, pickup_zone, dropoff_zone)
        }

    except Exception as e:
        print(f"Failed to get AI Context - {e}\n{traceback.format_exc()}")
        raise Exception(traceback.format_exc())
    
    finally:
        db.close()


def detect_iqr_anomalies(results, value_key, label_key=None):
    if len(results) < 4:
        return []

    values = sorted(
        float(row._mapping[value_key])
        for row in results
    )

    q1 = values[len(values) // 4]
    q3 = values[(len(values) * 3) // 4]

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    anomalies = []

    for row in results:

        value = float(row._mapping[value_key])

        if value < lower_bound or value > upper_bound:

            anomaly = {
                value_key: value,
                "type": (
                    "high"
                    if value > upper_bound
                    else "low"
                )
            }

            if label_key:
                anomaly[label_key] = row._mapping[label_key]

            anomalies.append(anomaly)

    return anomalies


def detect_hourly_anomalies(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:
        query = db.query(
            extract("hour", TaxiTrip.pickup_datetime).label("hour"),
            func.count(TaxiTrip.id).label("trip_count")
        )

        query = apply_filters(
            query,
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone
        )

        results = (
            query
            .group_by(extract("hour", TaxiTrip.pickup_datetime))
            .order_by(extract("hour", TaxiTrip.pickup_datetime))
            .all()
        )

        return detect_iqr_anomalies(results,"trip_count", "hour")

    finally:
        db.close()


def detect_revenue_anomalies(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:

        query = db.query(
            func.date(TaxiTrip.pickup_datetime).label("date"),
            func.sum(TaxiTrip.total_amount).label("revenue")
        )

        query = apply_filters(
            query,
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone
        )

        results = (
            query
            .group_by(func.date(TaxiTrip.pickup_datetime))
            .order_by(func.date(TaxiTrip.pickup_datetime))
            .all()
        )

        return detect_iqr_anomalies(results,"revenue","date")

    finally:
        db.close()


def detect_distance_anomalies(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):
    db = SessionLocal()

    try:

        query = db.query(
            extract(
                "hour",
                TaxiTrip.pickup_datetime
            ).label("hour"),

            func.avg(
                TaxiTrip.trip_distance
            ).label("avg_distance")
        )

        query = apply_filters(
            query,
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone
        )

        results = (
            query
            .filter(TaxiTrip.trip_distance > 0)
            .group_by(
                extract(
                    "hour",
                    TaxiTrip.pickup_datetime
                )
            )
            .order_by(
                extract(
                    "hour",
                    TaxiTrip.pickup_datetime
                )
            )
            .all()
        )

        return detect_iqr_anomalies(results,"avg_distance","hour")
        
    finally:
        db.close()

