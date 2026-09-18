import pandas as pd
from sqlalchemy import create_engine
from config import Config

PARQUET_FILE = "data/cleaned/NYC_Trips.parquet"
TABLE_NAME = "nyc_taxi"
CHUNK_SIZE = 50_000

engine = create_engine(str(Config.SQLALCHEMY_DATABASE_URI))

df = pd.read_parquet(PARQUET_FILE)

print(f"Loaded Parquet: {len(df):,} rows")

CHUNK_SIZE = 20_000

for start in range(0, len(df), CHUNK_SIZE):
    chunk = df.iloc[start:start + CHUNK_SIZE]

    chunk.to_sql(
        TABLE_NAME,
        engine,
        if_exists="append",
        index=False
    )

    print(f"Inserted {min(start + CHUNK_SIZE, len(df)):,} / {len(df):,}")
    
print("Data loading completed!")