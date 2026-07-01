from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://localhost:5432/ai_costs"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.scalar())

print("Postresql connected")