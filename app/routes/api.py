from flask import Blueprint, jsonify, request

from app.services.taxi_services import get_kpis, get_trips_by_hour, get_trips_by_day, get_payment_analysis, get_top_locations, get_revenue_by_day, get_revenue_by_hour, get_avg_revenue_by_hour, get_revenue_by_pickup_zone, get_revenue_by_dropoff_zone, get_filter_options

from app.services.ai_services import get_dashboard_insights, get_ai_anomalies


api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/filter-options")
def filter_options():
    return jsonify(get_filter_options())

@api.route("/kpis")
def kpis():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    
    return jsonify(
        get_kpis(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone
        )
    )

@api.route("/trips-by-hour")
def trips_by_hour():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_trips_by_hour(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/trips-by-day")
def trips_by_day():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_trips_by_day(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/payment-analysis")
def payment_analysis():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_payment_analysis(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/top-pickup-zones")
def top_pickup_zones():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_top_locations("pickup"))

@api.route("/top-dropoff-zones")
def top_dropoff_zones():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_top_locations(
            location_type="dropoff",
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/revenue-by-day")
def revenue_by_day():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_revenue_by_day(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/revenue-by-hour")
def revenue_by_hour():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_revenue_by_hour(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/avg-revenue-by-hour")
def avg_revenue_by_hour():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_avg_revenue_by_hour(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/revenue-by-pickup-zone")
def revenue_by_pickup_zone():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_revenue_by_pickup_zone(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))

@api.route("/revenue-by-dropoff-zone")
def revenue_by_dropoff_zone():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")
    return jsonify(get_revenue_by_dropoff_zone(
            start_date=start_date,
            end_date=end_date,
            payment_type=payment_type,
            pickup_zone=pickup_zone,
            dropoff_zone=dropoff_zone))


@api.route("/ai-insights")
def ai_insights():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")

    insights = get_dashboard_insights(start_date=start_date,
                end_date=end_date,
                payment_type=payment_type,
                pickup_zone=pickup_zone,
                dropoff_zone=dropoff_zone)

    return jsonify({
        "insights": insights
    })

@api.route("/ai-anomalies")
def ai_anomalies():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    payment_type = request.args.get("payment_type")
    pickup_zone = request.args.get("pickup_zone")
    dropoff_zone = request.args.get("dropoff_zone")

    result = get_ai_anomalies(start_date=start_date,
                end_date=end_date,
                payment_type=payment_type,
                pickup_zone=pickup_zone,
                dropoff_zone=dropoff_zone)

    return jsonify(result)

