from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from app.services.taxi_services import get_ai_context, detect_hourly_anomalies, detect_revenue_anomalies, detect_distance_anomalies

llm = init_chat_model(
    model="openai/gpt-oss-120b",
    model_provider="groq",
    temperature=1
)


def generate_ai_insights(analytics_data:dict):
    system_message = SystemMessage(
        content="""
You are an AI analytics assistant for an NYC Taxi Analytics Dashboard.
Generate exactly 4 insights using these categories:

Demand:
Revenue:
Payment:
Location:

Rules:
- Use ONLY the provided data.
- Never invent numbers.
- Mention specific numbers when useful.
- Identify meaningful patterns or relationships.
- Keep each insight concise.
- Do not simply repeat the raw metrics.
- Do not make unsupported claims.
- Return exactly one insight for each category.
- Return ONLY these four lines.
"""
    )

    
    human_message = HumanMessage(
        content=f"""
Analyze the following NYC taxi analytics data:

{"\n".join([f"{key}:{values}" for key,values in analytics_data.items()])}
"""
    )

    response = llm.invoke([
        system_message,
        human_message
    ])

    return response.content

def get_dashboard_insights(
    start_date=None,
    end_date=None,
    payment_type=None,
    pickup_zone=None,
    dropoff_zone=None
):
    analytics_data = get_ai_context(
        start_date=start_date,
        end_date=end_date,
        payment_type=payment_type,
        pickup_zone=pickup_zone,
        dropoff_zone=dropoff_zone
    )

    return generate_ai_insights(analytics_data)



def generate_anomaly_explanations(anomalies, analytics_data):

    if not any(anomalies.values()):
        return "<p>No significant anomalies were detected.</p>"

    system_message = SystemMessage(
        content="""
You are an AI analytics assistant for an NYC Taxi Analytics Dashboard.

Analyze the statistically detected anomalies.

Return the analysis as HTML.

Allowed HTML tags ONLY:
- <div>
- <p>
- <strong>
- <ul>
- <li>
- <span>

Formatting rules:
- Use <ul> and <li> for anomaly observations.
- Use <strong> for important values such as dates, hours,
  trip counts, revenue, and distances.
- Keep observations concise.
- Group observations by category.
- Use these category headings:
  Demand Anomalies
  Revenue Anomalies
  Trip Distance Anomalies

Example:

<div>
    <p><strong>Demand Anomalies</strong></p>
    <ul>
        <li>
            <strong>6:00 PM</strong> recorded
            <strong>245,000 trips</strong>, unusually high
            compared with the expected hourly range.
        </li>
    </ul>

    <p><strong>Revenue Anomalies</strong></p>
    <ul>
        <li>
            <strong>May 24</strong> recorded revenue of
            <strong>$2.62M</strong>, below the expected range.
        </li>
    </ul>
</div>

Important:
- Use ONLY the supplied data.
- Never invent numbers.
- Never invent causes.
- Clearly describe observed statistical patterns.
- Return ONLY HTML.
"""
    )

    human_message = HumanMessage(
        content=f"""
Analytics context:

{analytics_data}

Detected anomalies:

{anomalies}
"""
    )

    response = llm.invoke([
        system_message,
        human_message
    ])

    return response.content

def get_ai_anomalies(start_date=None, end_date=None, payment_type=None, pickup_zone=None, dropoff_zone=None):

    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "payment_type": payment_type,
        "pickup_zone": pickup_zone,
        "dropoff_zone": dropoff_zone
    }

    analytics_data = get_ai_context(**filters)
    demand_anomalies = detect_hourly_anomalies(**filters)
    revenue_anomalies = detect_revenue_anomalies(**filters)
    distance_anomalies = detect_distance_anomalies(**filters)

    anomalies =  {
        "demand": demand_anomalies,
        "revenue": revenue_anomalies,
        "distance": distance_anomalies
    }

    explanation = generate_anomaly_explanations(
        anomalies,
        analytics_data
    )

    return {
        "anomalies": anomalies,
        "explanation": explanation
    }

