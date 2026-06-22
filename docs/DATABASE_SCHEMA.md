# Database Schema: SymptoScan AI

## Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ PROFILES : has
    USERS ||--o{ AUDIT_LOGS : generates
    USERS ||--o{ NOTIFICATIONS : receives
    PROFILES ||--o{ ASSESSMENTS : takes
    PROFILES ||--o{ MEDICAL_REPORTS : uploads
    PROFILES ||--o{ CHAT_SESSIONS : engages
    
    ASSESSMENTS ||--o{ SYMPTOMS_REPORTED : includes
    ASSESSMENTS ||--o| PREDICTIONS : generates
    ASSESSMENTS ||--o{ RECOMMENDATIONS : produces
    
    MEDICAL_REPORTS ||--o{ REPORT_MARKERS : extracts
    
    DISEASES ||--o{ PREDICTIONS : linked_to
    DISEASES ||--o{ SYMPTOMS : characterized_by

    USERS {
        uuid id PK
        string email
        string password_hash
        string role "ADMIN or PATIENT"
        datetime created_at
        datetime updated_at
    }

    PROFILES {
        uuid id PK
        uuid user_id FK
        string full_name
        date date_of_birth
        string gender
        float height_cm
        float weight_kg
        string medical_history "JSONB"
        datetime created_at
    }

    ASSESSMENTS {
        uuid id PK
        uuid profile_id FK
        string ai_summary
        string risk_level
        datetime assessment_date
    }

    SYMPTOMS {
        uuid id PK
        string name
        string category
    }

    SYMPTOMS_REPORTED {
        uuid id PK
        uuid assessment_id FK
        uuid symptom_id FK
        string severity "1-10"
        int duration_days
    }

    DISEASES {
        uuid id PK
        string name
        string description
        string icd10_code
    }

    PREDICTIONS {
        uuid id PK
        uuid assessment_id FK
        uuid disease_id FK
        float probability_score
        string contributing_factors "JSONB"
    }

    MEDICAL_REPORTS {
        uuid id PK
        uuid profile_id FK
        string file_url
        string report_type
        string ai_analysis_summary
        datetime uploaded_at
    }

    REPORT_MARKERS {
        uuid id PK
        uuid report_id FK
        string marker_name "e.g., Blood Sugar"
        float value
        string unit
        boolean is_abnormal
    }

    CHAT_SESSIONS {
        uuid id PK
        uuid profile_id FK
        string title
        datetime started_at
        string message_history "JSONB"
    }

    RECOMMENDATIONS {
        uuid id PK
        uuid assessment_id FK
        string category "Diet, Exercise, etc."
        string description
    }

    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        string title
        string message
        boolean is_read
        datetime created_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        string resource
        datetime timestamp
    }
```

## Schema Details
- **PostgreSQL** is the primary database.
- Extensive use of `uuid` for primary keys to ensure global uniqueness and prevent enumeration attacks.
- Use of `JSONB` for flexible storage (e.g., `medical_history`, `message_history`, `contributing_factors`) where schemas might evolve without needing structural migrations.
- **pgvector** extension will be used alongside this schema to store embeddings for AI retrieval, potentially linked via `document_id` references.
