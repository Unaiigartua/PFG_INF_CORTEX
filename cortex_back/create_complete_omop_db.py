#!/usr/bin/env python3
"""
Script para crear una base de datos OMOP CDM v5.3 completa en SQLite
"""
import sqlite3
from pathlib import Path
import random
from datetime import datetime, timedelta

# Crear directorio si no existe
omop_dir = Path("omop_testing")
omop_dir.mkdir(exist_ok=True)

DB_PATH = omop_dir / "omop_complete.db"

# DDL completo para OMOP CDM v5.3
OMOP_DDL = {
    # STANDARDIZED CLINICAL DATA TABLES
    'PERSON': """
        CREATE TABLE person (
            person_id INTEGER NOT NULL,
            gender_concept_id INTEGER NOT NULL,
            year_of_birth INTEGER NOT NULL,
            month_of_birth INTEGER NULL,
            day_of_birth INTEGER NULL,
            birth_datetime TEXT NULL,
            race_concept_id INTEGER NOT NULL,
            ethnicity_concept_id INTEGER NOT NULL,
            location_id INTEGER NULL,
            provider_id INTEGER NULL,
            care_site_id INTEGER NULL,
            person_source_value TEXT NULL,
            gender_source_value TEXT NULL,
            gender_source_concept_id INTEGER NULL,
            race_source_value TEXT NULL,
            race_source_concept_id INTEGER NULL,
            ethnicity_source_value TEXT NULL,
            ethnicity_source_concept_id INTEGER NULL,
            PRIMARY KEY (person_id)
        );
    """,
    
    'OBSERVATION_PERIOD': """
        CREATE TABLE observation_period (
            observation_period_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            observation_period_start_date TEXT NOT NULL,
            observation_period_end_date TEXT NOT NULL,
            period_type_concept_id INTEGER NOT NULL,
            PRIMARY KEY (observation_period_id)
        );
    """,
    
    'VISIT_OCCURRENCE': """
        CREATE TABLE visit_occurrence (
            visit_occurrence_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            visit_concept_id INTEGER NOT NULL,
            visit_start_date TEXT NOT NULL,
            visit_start_datetime TEXT NULL,
            visit_end_date TEXT NOT NULL,
            visit_end_datetime TEXT NULL,
            visit_type_concept_id INTEGER NOT NULL,
            provider_id INTEGER NULL,
            care_site_id INTEGER NULL,
            visit_source_value TEXT NULL,
            visit_source_concept_id INTEGER NULL,
            admitted_from_concept_id INTEGER NULL,
            admitted_from_source_value TEXT NULL,
            discharge_to_concept_id INTEGER NULL,
            discharge_to_source_value TEXT NULL,
            preceding_visit_occurrence_id INTEGER NULL,
            PRIMARY KEY (visit_occurrence_id)
        );
    """,
    
    'VISIT_DETAIL': """
        CREATE TABLE visit_detail (
            visit_detail_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            visit_detail_concept_id INTEGER NOT NULL,
            visit_detail_start_date TEXT NOT NULL,
            visit_detail_start_datetime TEXT NULL,
            visit_detail_end_date TEXT NOT NULL,
            visit_detail_end_datetime TEXT NULL,
            visit_detail_type_concept_id INTEGER NOT NULL,
            provider_id INTEGER NULL,
            care_site_id INTEGER NULL,
            visit_detail_source_value TEXT NULL,
            visit_detail_source_concept_id INTEGER NULL,
            admitted_from_concept_id INTEGER NULL,
            admitted_from_source_value TEXT NULL,
            discharge_to_source_value TEXT NULL,
            discharge_to_concept_id INTEGER NULL,
            preceding_visit_detail_id INTEGER NULL,
            visit_detail_parent_id INTEGER NULL,
            visit_occurrence_id INTEGER NOT NULL,
            PRIMARY KEY (visit_detail_id)
        );
    """,
    
    'CONDITION_OCCURRENCE': """
        CREATE TABLE condition_occurrence (
            condition_occurrence_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            condition_concept_id INTEGER NOT NULL,
            condition_start_date TEXT NOT NULL,
            condition_start_datetime TEXT NULL,
            condition_end_date TEXT NULL,
            condition_end_datetime TEXT NULL,
            condition_type_concept_id INTEGER NOT NULL,
            condition_status_concept_id INTEGER NULL,
            stop_reason TEXT NULL,
            provider_id INTEGER NULL,
            visit_occurrence_id INTEGER NULL,
            visit_detail_id INTEGER NULL,
            condition_source_value TEXT NULL,
            condition_source_concept_id INTEGER NULL,
            condition_status_source_value TEXT NULL,
            PRIMARY KEY (condition_occurrence_id)
        );
    """,
    
    'DRUG_EXPOSURE': """
        CREATE TABLE drug_exposure (
            drug_exposure_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            drug_concept_id INTEGER NOT NULL,
            drug_exposure_start_date TEXT NOT NULL,
            drug_exposure_start_datetime TEXT NULL,
            drug_exposure_end_date TEXT NOT NULL,
            drug_exposure_end_datetime TEXT NULL,
            verbatim_end_date TEXT NULL,
            drug_type_concept_id INTEGER NOT NULL,
            stop_reason TEXT NULL,
            refills INTEGER NULL,
            quantity REAL NULL,
            days_supply INTEGER NULL,
            sig TEXT NULL,
            route_concept_id INTEGER NULL,
            lot_number TEXT NULL,
            provider_id INTEGER NULL,
            visit_occurrence_id INTEGER NULL,
            visit_detail_id INTEGER NULL,
            drug_source_value TEXT NULL,
            drug_source_concept_id INTEGER NULL,
            route_source_value TEXT NULL,
            dose_unit_source_value TEXT NULL,
            PRIMARY KEY (drug_exposure_id)
        );
    """,
    
    'PROCEDURE_OCCURRENCE': """
        CREATE TABLE procedure_occurrence (
            procedure_occurrence_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            procedure_concept_id INTEGER NOT NULL,
            procedure_date TEXT NOT NULL,
            procedure_datetime TEXT NULL,
            procedure_type_concept_id INTEGER NOT NULL,
            modifier_concept_id INTEGER NULL,
            quantity INTEGER NULL,
            provider_id INTEGER NULL,
            visit_occurrence_id INTEGER NULL,
            visit_detail_id INTEGER NULL,
            procedure_source_value TEXT NULL,
            procedure_source_concept_id INTEGER NULL,
            modifier_source_value TEXT NULL,
            PRIMARY KEY (procedure_occurrence_id)
        );
    """,
    
    'DEVICE_EXPOSURE': """
        CREATE TABLE device_exposure (
            device_exposure_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            device_concept_id INTEGER NOT NULL,
            device_exposure_start_date TEXT NOT NULL,
            device_exposure_start_datetime TEXT NULL,
            device_exposure_end_date TEXT NULL,
            device_exposure_end_datetime TEXT NULL,
            device_type_concept_id INTEGER NOT NULL,
            unique_device_id TEXT NULL,
            quantity INTEGER NULL,
            provider_id INTEGER NULL,
            visit_occurrence_id INTEGER NULL,
            visit_detail_id INTEGER NULL,
            device_source_value TEXT NULL,
            device_source_concept_id INTEGER NULL,
            PRIMARY KEY (device_exposure_id)
        );
    """,
    
    'MEASUREMENT': """
        CREATE TABLE measurement (
            measurement_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            measurement_concept_id INTEGER NOT NULL,
            measurement_date TEXT NOT NULL,
            measurement_datetime TEXT NULL,
            measurement_time TEXT NULL,
            measurement_type_concept_id INTEGER NOT NULL,
            operator_concept_id INTEGER NULL,
            value_as_number REAL NULL,
            value_as_concept_id INTEGER NULL,
            unit_concept_id INTEGER NULL,
            range_low REAL NULL,
            range_high REAL NULL,
            provider_id INTEGER NULL,
            visit_occurrence_id INTEGER NULL,
            visit_detail_id INTEGER NULL,
            measurement_source_value TEXT NULL,
            measurement_source_concept_id INTEGER NULL,
            unit_source_value TEXT NULL,
            value_source_value TEXT NULL,
            PRIMARY KEY (measurement_id)
        );
    """,
    
    'OBSERVATION': """
        CREATE TABLE observation (
            observation_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            observation_concept_id INTEGER NOT NULL,
            observation_date TEXT NOT NULL,
            observation_datetime TEXT NULL,
            observation_type_concept_id INTEGER NOT NULL,
            value_as_number REAL NULL,
            value_as_string TEXT NULL,
            value_as_concept_id INTEGER NULL,
            qualifier_concept_id INTEGER NULL,
            unit_concept_id INTEGER NULL,
            provider_id INTEGER NULL,
            visit_occurrence_id INTEGER NULL,
            visit_detail_id INTEGER NULL,
            observation_source_value TEXT NULL,
            observation_source_concept_id INTEGER NULL,
            unit_source_value TEXT NULL,
            qualifier_source_value TEXT NULL,
            observation_event_id INTEGER NULL,
            obs_event_field_concept_id INTEGER NULL,
            value_as_datetime TEXT NULL,
            PRIMARY KEY (observation_id)
        );
    """,
    
    'DEATH': """
        CREATE TABLE death (
            person_id INTEGER NOT NULL,
            death_date TEXT NOT NULL,
            death_datetime TEXT NULL,
            death_type_concept_id INTEGER NOT NULL,
            cause_concept_id INTEGER NULL,
            cause_source_value TEXT NULL,
            cause_source_concept_id INTEGER NULL,
            PRIMARY KEY (person_id)
        );
    """,
    
    'NOTE': """
        CREATE TABLE note (
            note_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            note_date TEXT NOT NULL,
            note_datetime TEXT NULL,
            note_type_concept_id INTEGER NOT NULL,
            note_class_concept_id INTEGER NOT NULL,
            note_title TEXT NULL,
            note_text TEXT NOT NULL,
            encoding_concept_id INTEGER NOT NULL,
            language_concept_id INTEGER NOT NULL,
            provider_id INTEGER NULL,
            visit_occurrence_id INTEGER NULL,
            visit_detail_id INTEGER NULL,
            note_source_value TEXT NULL,
            PRIMARY KEY (note_id)
        );
    """,
    
    'NOTE_NLP': """
        CREATE TABLE note_nlp (
            note_nlp_id INTEGER NOT NULL,
            note_id INTEGER NOT NULL,
            section_concept_id INTEGER NULL,
            snippet TEXT NULL,
            offset_char TEXT NULL,
            lexical_variant TEXT NOT NULL,
            note_nlp_concept_id INTEGER NULL,
            note_nlp_source_concept_id INTEGER NULL,
            nlp_system TEXT NULL,
            nlp_date TEXT NOT NULL,
            nlp_datetime TEXT NULL,
            term_exists TEXT NULL,
            term_temporal TEXT NULL,
            term_modifiers TEXT NULL,
            PRIMARY KEY (note_nlp_id)
        );
    """,
    
    'SPECIMEN': """
        CREATE TABLE specimen (
            specimen_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            specimen_concept_id INTEGER NOT NULL,
            specimen_type_concept_id INTEGER NOT NULL,
            specimen_date TEXT NOT NULL,
            specimen_datetime TEXT NULL,
            quantity REAL NULL,
            unit_concept_id INTEGER NULL,
            anatomic_site_concept_id INTEGER NULL,
            disease_status_concept_id INTEGER NULL,
            specimen_source_id TEXT NULL,
            specimen_source_value TEXT NULL,
            unit_source_value TEXT NULL,
            anatomic_site_source_value TEXT NULL,
            disease_status_source_value TEXT NULL,
            PRIMARY KEY (specimen_id)
        );
    """,
    
    # STANDARDIZED HEALTH SYSTEM DATA TABLES
    'LOCATION': """
        CREATE TABLE location (
            location_id INTEGER NOT NULL,
            address_1 TEXT NULL,
            address_2 TEXT NULL,
            city TEXT NULL,
            state TEXT NULL,
            zip TEXT NULL,
            county TEXT NULL,
            location_source_value TEXT NULL,
            PRIMARY KEY (location_id)
        );
    """,
    
    'CARE_SITE': """
        CREATE TABLE care_site (
            care_site_id INTEGER NOT NULL,
            care_site_name TEXT NULL,
            place_of_service_concept_id INTEGER NULL,
            location_id INTEGER NULL,
            care_site_source_value TEXT NULL,
            place_of_service_source_value TEXT NULL,
            PRIMARY KEY (care_site_id)
        );
    """,
    
    'PROVIDER': """
        CREATE TABLE provider (
            provider_id INTEGER NOT NULL,
            provider_name TEXT NULL,
            npi TEXT NULL,
            dea TEXT NULL,
            specialty_concept_id INTEGER NULL,
            care_site_id INTEGER NULL,
            year_of_birth INTEGER NULL,
            gender_concept_id INTEGER NULL,
            provider_source_value TEXT NULL,
            specialty_source_value TEXT NULL,
            specialty_source_concept_id INTEGER NULL,
            gender_source_value TEXT NULL,
            gender_source_concept_id INTEGER NULL,
            PRIMARY KEY (provider_id)
        );
    """,
    
    # STANDARDIZED HEALTH ECONOMICS DATA TABLES
    'PAYER_PLAN_PERIOD': """
        CREATE TABLE payer_plan_period (
            payer_plan_period_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            payer_plan_period_start_date TEXT NOT NULL,
            payer_plan_period_end_date TEXT NOT NULL,
            payer_concept_id INTEGER NULL,
            payer_source_value TEXT NULL,
            payer_source_concept_id INTEGER NULL,
            plan_concept_id INTEGER NULL,
            plan_source_value TEXT NULL,
            plan_source_concept_id INTEGER NULL,
            sponsor_concept_id INTEGER NULL,
            sponsor_source_value TEXT NULL,
            sponsor_source_concept_id INTEGER NULL,
            family_source_value TEXT NULL,
            stop_reason_concept_id INTEGER NULL,
            stop_reason_source_value TEXT NULL,
            stop_reason_source_concept_id INTEGER NULL,
            PRIMARY KEY (payer_plan_period_id)
        );
    """,
    
    'COST': """
        CREATE TABLE cost (
            cost_id INTEGER NOT NULL,
            cost_event_id INTEGER NOT NULL,
            cost_domain_id TEXT NOT NULL,
            cost_type_concept_id INTEGER NOT NULL,
            currency_concept_id INTEGER NULL,
            total_charge REAL NULL,
            total_cost REAL NULL,
            total_paid REAL NULL,
            paid_by_payer REAL NULL,
            paid_by_patient REAL NULL,
            paid_patient_copay REAL NULL,
            paid_patient_coinsurance REAL NULL,
            paid_patient_deductible REAL NULL,
            paid_by_primary REAL NULL,
            paid_ingredient_cost REAL NULL,
            paid_dispensing_fee REAL NULL,
            payer_plan_period_id INTEGER NULL,
            amount_allowed REAL NULL,
            revenue_code_concept_id INTEGER NULL,
            revenue_code_source_value TEXT NULL,
            drg_concept_id INTEGER NULL,
            drg_source_value TEXT NULL,
            PRIMARY KEY (cost_id)
        );
    """,
    
    # STANDARDIZED DERIVED ELEMENTS
    'DRUG_ERA': """
        CREATE TABLE drug_era (
            drug_era_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            drug_concept_id INTEGER NOT NULL,
            drug_era_start_date TEXT NOT NULL,
            drug_era_end_date TEXT NOT NULL,
            drug_exposure_count INTEGER NULL,
            gap_days INTEGER NULL,
            PRIMARY KEY (drug_era_id)
        );
    """,
    
    'DOSE_ERA': """
        CREATE TABLE dose_era (
            dose_era_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            drug_concept_id INTEGER NOT NULL,
            unit_concept_id INTEGER NOT NULL,
            dose_value REAL NOT NULL,
            dose_era_start_date TEXT NOT NULL,
            dose_era_end_date TEXT NOT NULL,
            PRIMARY KEY (dose_era_id)
        );
    """,
    
    'CONDITION_ERA': """
        CREATE TABLE condition_era (
            condition_era_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            condition_concept_id INTEGER NOT NULL,
            condition_era_start_date TEXT NOT NULL,
            condition_era_end_date TEXT NOT NULL,
            condition_occurrence_count INTEGER NULL,
            PRIMARY KEY (condition_era_id)
        );
    """,
    
    # STANDARDIZED VOCABULARIES
    'CONCEPT': """
        CREATE TABLE concept (
            concept_id INTEGER NOT NULL,
            concept_name TEXT NOT NULL,
            domain_id TEXT NOT NULL,
            vocabulary_id TEXT NOT NULL,
            concept_class_id TEXT NOT NULL,
            standard_concept TEXT NULL,
            concept_code TEXT NOT NULL,
            valid_start_date TEXT NOT NULL,
            valid_end_date TEXT NOT NULL,
            invalid_reason TEXT NULL,
            PRIMARY KEY (concept_id)
        );
    """,
    
    'VOCABULARY': """
        CREATE TABLE vocabulary (
            vocabulary_id TEXT NOT NULL,
            vocabulary_name TEXT NOT NULL,
            vocabulary_reference TEXT NOT NULL,
            vocabulary_version TEXT NULL,
            vocabulary_concept_id INTEGER NOT NULL,
            PRIMARY KEY (vocabulary_id)
        );
    """,
    
    'DOMAIN': """
        CREATE TABLE domain (
            domain_id TEXT NOT NULL,
            domain_name TEXT NOT NULL,
            domain_concept_id INTEGER NOT NULL,
            PRIMARY KEY (domain_id)
        );
    """,
    
    'CONCEPT_CLASS': """
        CREATE TABLE concept_class (
            concept_class_id TEXT NOT NULL,
            concept_class_name TEXT NOT NULL,
            concept_class_concept_id INTEGER NOT NULL,
            PRIMARY KEY (concept_class_id)
        );
    """,
    
    'CONCEPT_RELATIONSHIP': """
        CREATE TABLE concept_relationship (
            concept_id_1 INTEGER NOT NULL,
            concept_id_2 INTEGER NOT NULL,
            relationship_id TEXT NOT NULL,
            valid_start_date TEXT NOT NULL,
            valid_end_date TEXT NOT NULL,
            invalid_reason TEXT NULL
        );
    """,
    
    'RELATIONSHIP': """
        CREATE TABLE relationship (
            relationship_id TEXT NOT NULL,
            relationship_name TEXT NOT NULL,
            is_hierarchical TEXT NOT NULL,
            defines_ancestry TEXT NOT NULL,
            reverse_relationship_id TEXT NOT NULL,
            relationship_concept_id INTEGER NOT NULL,
            PRIMARY KEY (relationship_id)
        );
    """,
    
    'CONCEPT_SYNONYM': """
        CREATE TABLE concept_synonym (
            concept_id INTEGER NOT NULL,
            concept_synonym_name TEXT NOT NULL,
            language_concept_id INTEGER NOT NULL
        );
    """,
    
    'CONCEPT_ANCESTOR': """
        CREATE TABLE concept_ancestor (
            ancestor_concept_id INTEGER NOT NULL,
            descendant_concept_id INTEGER NOT NULL,
            min_levels_of_separation INTEGER NOT NULL,
            max_levels_of_separation INTEGER NOT NULL
        );
    """,
    
    'SOURCE_TO_CONCEPT_MAP': """
        CREATE TABLE source_to_concept_map (
            source_code TEXT NOT NULL,
            source_concept_id INTEGER NOT NULL,
            source_vocabulary_id TEXT NOT NULL,
            source_code_description TEXT NULL,
            target_concept_id INTEGER NOT NULL,
            target_vocabulary_id TEXT NOT NULL,
            valid_start_date TEXT NOT NULL,
            valid_end_date TEXT NOT NULL,
            invalid_reason TEXT NULL
        );
    """,
    
    'DRUG_STRENGTH': """
        CREATE TABLE drug_strength (
            drug_concept_id INTEGER NOT NULL,
            ingredient_concept_id INTEGER NOT NULL,
            amount_value REAL NULL,
            amount_unit_concept_id INTEGER NULL,
            numerator_value REAL NULL,
            numerator_unit_concept_id INTEGER NULL,
            denominator_value REAL NULL,
            denominator_unit_concept_id INTEGER NULL,
            box_size INTEGER NULL,
            valid_start_date TEXT NOT NULL,
            valid_end_date TEXT NOT NULL,
            invalid_reason TEXT NULL
        );
    """,
    
    # STANDARDIZED META-DATA
    'CDM_SOURCE': """
        CREATE TABLE cdm_source (
            cdm_source_name TEXT NOT NULL,
            cdm_source_abbreviation TEXT NOT NULL,
            cdm_holder TEXT NOT NULL,
            source_description TEXT NULL,
            source_documentation_reference TEXT NULL,
            cdm_etl_reference TEXT NULL,
            source_release_date TEXT NOT NULL,
            cdm_release_date TEXT NOT NULL,
            cdm_version TEXT NULL,
            vocabulary_version TEXT NULL
        );
    """,
    
    'METADATA': """
        CREATE TABLE metadata (
            metadata_concept_id INTEGER NOT NULL,
            metadata_type_concept_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            value_as_string TEXT NULL,
            value_as_concept_id INTEGER NULL,
            metadata_date TEXT NULL,
            metadata_datetime TEXT NULL
        );
    """
}

# Conceptos médicos básicos para pruebas
BASIC_CONCEPTS = {
    # Géneros
    8507: ("Male", "Gender", "Gender"),
    8532: ("Female", "Gender", "Gender"),
    
    # Condiciones comunes
    201826: ("Type 2 diabetes mellitus", "Condition", "Clinical Finding"),
    313217: ("Atrial fibrillation", "Condition", "Clinical Finding"), 
    320128: ("Essential hypertension", "Condition", "Clinical Finding"),
    134057: ("Acute myocardial infarction", "Condition", "Clinical Finding"),
    432867: ("Pneumonia", "Condition", "Clinical Finding"),
    133834: ("Breast cancer", "Condition", "Clinical Finding"),
    4298597: ("Malignant neoplasm of breast", "Condition", "Clinical Finding"),
    
    # Procedimientos
    4273391: ("Lumpectomy", "Procedure", "Procedure"),
    4342287: ("Mammography", "Procedure", "Procedure"),
    4163872: ("Electrocardiogram", "Procedure", "Procedure"),
    
    # Medicamentos
    1548195: ("Estradiol", "Drug", "Ingredient"),
    1559873: ("Insulin", "Drug", "Ingredient"),
    1314006: ("Metformin", "Drug", "Ingredient"),
    1308216: ("Lisinopril", "Drug", "Ingredient"),
    
    # Razas
    8527: ("White", "Race", "Race"),
    8516: ("Black or African American", "Race", "Race"),
    8515: ("Asian", "Race", "Race"),
    
    # Etnias
    38003563: ("Not Hispanic or Latino", "Ethnicity", "Ethnicity"),
    38003564: ("Hispanic or Latino", "Ethnicity", "Ethnicity"),
    
    # Tipos de visita
    9201: ("Inpatient Visit", "Visit", "Visit"),
    9202: ("Outpatient Visit", "Visit", "Visit"),
    9203: ("Emergency Room Visit", "Visit", "Visit"),
    
    # Tipos de observación
    44818701: ("From physical examination", "Type Concept", "Meas Type"),
    44818702: ("From laboratory", "Type Concept", "Meas Type")
}

def create_database():
    """Crear la base de datos y todas las tablas OMOP"""
    print(f"🗄️  Creando base de datos OMOP completa en {DB_PATH}")
    
    # Eliminar base de datos existente
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("   Base de datos anterior eliminada")
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Crear todas las tablas
        for table_name, ddl in OMOP_DDL.items():
            print(f"   Creando tabla {table_name}")
            cursor.execute(ddl)
        
        # Crear índices básicos para mejorar rendimiento
        print("   Creando índices...")
        indices = [
            "CREATE INDEX idx_person_id ON person(person_id);",
            "CREATE INDEX idx_condition_person_id ON condition_occurrence(person_id);",
            "CREATE INDEX idx_condition_concept_id ON condition_occurrence(condition_concept_id);",
            "CREATE INDEX idx_drug_person_id ON drug_exposure(person_id);",
            "CREATE INDEX idx_drug_concept_id ON drug_exposure(drug_concept_id);",
            "CREATE INDEX idx_procedure_person_id ON procedure_occurrence(person_id);",
            "CREATE INDEX idx_procedure_concept_id ON procedure_occurrence(procedure_concept_id);",
            "CREATE INDEX idx_concept_id ON concept(concept_id);",
            "CREATE INDEX idx_concept_code ON concept(concept_code);",
        ]
        
        for index in indices:
            cursor.execute(index)
        
        conn.commit()
        print(f"✅ {len(OMOP_DDL)} tablas creadas exitosamente")

def insert_basic_concepts(conn):
    """Insertar conceptos básicos necesarios para las pruebas"""
    print("📝 Insertando conceptos básicos...")
    cursor = conn.cursor()
    
    for concept_id, (concept_name, domain, concept_class) in BASIC_CONCEPTS.items():
        cursor.execute("""
            INSERT INTO concept (
                concept_id, concept_name, domain_id, vocabulary_id, 
                concept_class_id, standard_concept, concept_code,
                valid_start_date, valid_end_date, invalid_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            concept_id, concept_name, domain, "SNOMED", 
            concept_class, "S", str(concept_id),
            "1970-01-01", "2099-12-31", None
        ))
    
    conn.commit()
    print(f"✅ {len(BASIC_CONCEPTS)} conceptos básicos insertados")

def insert_sample_data(conn, num_persons=100):
    """Insertar datos de muestra para pruebas"""
    print(f"👥 Insertando datos de muestra para {num_persons} personas...")
    cursor = conn.cursor()
    
    # Insertar personas
    for person_id in range(1, num_persons + 1):
        gender = random.choice([8507, 8532])  # Male or Female
        birth_year = random.randint(1940, 2000)
        race = random.choice([8527, 8516, 8515])  # White, Black, Asian
        ethnicity = random.choice([38003563, 38003564])  # Hispanic or not
        
        cursor.execute("""
            INSERT INTO person (
                person_id, gender_concept_id, year_of_birth, month_of_birth, day_of_birth,
                race_concept_id, ethnicity_concept_id, location_id, provider_id, care_site_id,
                person_source_value, gender_source_value, race_source_value, ethnicity_source_value
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            person_id, gender, birth_year, random.randint(1, 12), random.randint(1, 28),
            race, ethnicity, None, None, None,
            f"Person_{person_id}", "M" if gender == 8507 else "F", 
            "White" if race == 8527 else "Other", "Hispanic" if ethnicity == 38003564 else "Not Hispanic"
        ))
    
    # Insertar períodos de observación
    for person_id in range(1, num_persons + 1):
        start_date = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 365*5))
        end_date = start_date + timedelta(days=random.randint(365, 365*10))
        
        cursor.execute("""
            INSERT INTO observation_period (
                observation_period_id, person_id, observation_period_start_date,
                observation_period_end_date, period_type_concept_id
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            person_id, person_id, start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'), 44814724  # Period inferred by algorithm
        ))
    
    # Insertar algunas condiciones de muestra
    condition_concepts = [201826, 313217, 320128, 134057, 432867, 133834]
    condition_id = 1
    
    for person_id in range(1, min(50, num_persons) + 1):  # Solo primeros 50 para muestra
        # Cada persona tiene 1-3 condiciones
        num_conditions = random.randint(1, 3)
        person_conditions = random.sample(condition_concepts, num_conditions)
        
        for condition_concept_id in person_conditions:
            condition_date = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 365*5))
            
            cursor.execute("""
                INSERT INTO condition_occurrence (
                    condition_occurrence_id, person_id, condition_concept_id,
                    condition_start_date, condition_type_concept_id,
                    condition_source_value
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                condition_id, person_id, condition_concept_id,
                condition_date.strftime('%Y-%m-%d'), 32020,  # EHR encounter diagnosis
                f"Condition_{condition_id}"
            ))
            condition_id += 1
    
    conn.commit()
    print(f"✅ Datos de muestra insertados: {num_persons} personas, {condition_id-1} condiciones")

def create_metadata(conn):
    """Insertar metadata básica del CDM"""
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO cdm_source (
            cdm_source_name, cdm_source_abbreviation, cdm_holder,
            source_description, cdm_etl_reference, source_release_date,
            cdm_release_date, cdm_version, vocabulary_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Cortex Test Database", "CORTEX_TEST", "Cortex Medical API",
        "Test database for SQL generation validation", "cortex_backend_v1",
        "2024-01-01", "2024-01-01", "v5.3", "v5.0 20-JAN-24"
    ))
    
    conn.commit()
    print("✅ Metadata del CDM insertada")

def verify_database(conn):
    """Verificar que la base de datos se creó correctamente"""
    cursor = conn.cursor()
    
    print("\n🔍 Verificando base de datos...")
    
    # Contar tablas
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
    table_count = cursor.fetchone()[0]
    print(f"   Tablas creadas: {table_count}")
    
    # Contar registros en tablas principales
    main_tables = ['person', 'concept', 'condition_occurrence', 'observation_period']
    
    for table in main_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"   Registros en {table}: {count}")
    
    # Verificar que se pueden hacer consultas básicas
    cursor.execute("""
        SELECT COUNT(DISTINCT p.person_id) 
        FROM person p 
        JOIN condition_occurrence co ON p.person_id = co.person_id
    """)
    patients_with_conditions = cursor.fetchone()[0]
    print(f"   Pacientes con condiciones: {patients_with_conditions}")
    
    print("✅ Base de datos verificada correctamente")

def main():
    """Función principal para crear la base de datos OMOP completa"""
    print("🏗️  Creando base de datos OMOP CDM v5.3 completa...")
    print("="*60)
    
    try:
        # Crear base de datos y tablas
        create_database()
        
        # Conectar y poblar con datos básicos
        with sqlite3.connect(DB_PATH) as conn:
            insert_basic_concepts(conn)
            insert_sample_data(conn, num_persons=1000)  # 1000 personas de muestra
            create_metadata(conn)
            verify_database(conn)
        
        print("="*60)
        print("🎉 Base de datos OMOP creada exitosamente!")
        print(f"📍 Ubicación: {DB_PATH.absolute()}")
        print(f"📊 Tamaño: {DB_PATH.stat().st_size / 1024 / 1024:.2f} MB")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: python scripts/test_setup.py")
        print("2. Probar SQL generation: uvicorn app.main:app --reload")
        print("3. Usar: python scripts/test_sql_generation.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando la base de datos: {e}")
        return False

if __name__ == "__main__":
    main()