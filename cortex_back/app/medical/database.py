import pandas as pd
import sqlite3

from app.core.config import OMOP_DIR, OMOP_CONCEPTS_DB
df = pd.read_csv(OMOP_DIR / "CONCEPT.csv", sep='\t', usecols=[...])
conn = sqlite3.connect(OMOP_CONCEPTS_DB)

df.to_sql("concepts", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_code ON concepts(concept_code);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON concepts(concept_name);")
conn.commit()