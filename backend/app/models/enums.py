from sqlalchemy import Enum as SAEnum

# Native PostgreSQL ENUM types. These mirror the 8 ENUM types created in
# database/schema.sql exactly (name, values, and member order).

gender_enum = SAEnum(
    "male", "female", "other",
    name="gender_enum",
)

officer_status_enum = SAEnum(
    "active", "on_leave", "suspended", "retired", "terminated",
    name="officer_status_enum",
)

user_role_enum = SAEnum(
    "admin", "supervisor", "officer", "viewer",
    name="user_role_enum",
)

unit_type_enum = SAEnum(
    "headquarters", "division", "precinct", "special_unit",
    name="unit_type_enum",
)

assignment_type_enum = SAEnum(
    "permanent", "temporary", "detached",
    name="assignment_type_enum",
)

operation_type_enum = SAEnum(
    "raid", "patrol_sweep", "checkpoint", "investigation", "surveillance", "crowd_control",
    name="operation_type_enum",
)

incident_severity_enum = SAEnum(
    "low", "medium", "high", "critical",
    name="incident_severity_enum",
)

shift_enum = SAEnum(
    "morning", "evening", "night",
    name="shift_enum",
)
