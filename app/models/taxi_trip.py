from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TaxiTrip(Base):
    __tablename__ = "nyc_taxi"

    id: Mapped[int] = mapped_column(primary_key=True)

    pickup_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime)
    dropoff_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime)

    passenger_count: Mapped[Optional[int]] = mapped_column()
    trip_distance: Mapped[Optional[float]] = mapped_column()

    pickup_location_id: Mapped[Optional[int]] = mapped_column()
    dropoff_location_id: Mapped[Optional[int]] = mapped_column()

    payment_type: Mapped[Optional[str]] = mapped_column(String(30))

    fare_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    extra: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    mta_tax: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tip_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    tolls_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    improvement_surcharge: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    congestion_surcharge: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    airport_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    cbd_congestion_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))