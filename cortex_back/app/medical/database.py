import pandas as pd
import sqlite3

df = pd.read_csv("OMOP_SNOMED/CONCEPT.csv", sep='\t', usecols=[
    "concept_id", "concept_name", "domain_id", "vocabulary_id",
    "concept_class_id", "standard_concept", "concept_code", "invalid_reason"
])

conn = sqlite3.connect("OMOP_SNOMED/omop_snomed.db")
df.to_sql("concepts", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_code ON concepts(concept_code);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON concepts(concept_name);")
conn.commit()