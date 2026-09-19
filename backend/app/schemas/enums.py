from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class OfficerStatusEnum(str, Enum):
    active = "active"
    on_leave = "on_leave"
    suspended = "suspended"
    retired = "retired"
    terminated = "terminated"


class UserRoleEnum(str, Enum):
    admin = "admin"
    supervisor = "supervisor"
    officer = "officer"
    viewer = "viewer"


class UnitTypeEnum(str, Enum):
    headquarters = "headquarters"
    division = "division"
    precinct = "precinct"
    special_unit = "special_unit"


class AssignmentTypeEnum(str, Enum):
    permanent = "permanent"
    temporary = "temporary"
    detached = "detached"


class OperationTypeEnum(str, Enum):
    raid = "raid"
    patrol_sweep = "patrol_sweep"
    checkpoint = "checkpoint"
    investigation = "investigation"
    surveillance = "surveillance"
    crowd_control = "crowd_control"


class OperationStatusEnum(str, Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class OperationParticipantRoleEnum(str, Enum):
    lead = "lead"
    participant = "participant"
    support = "support"


class ShiftEnum(str, Enum):
    morning = "morning"
    evening = "evening"
    night = "night"


class PatrolStatusEnum(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class IncidentTypeEnum(str, Enum):
    theft = "theft"
    assault = "assault"
    traffic = "traffic"
    homicide = "homicide"
    fraud = "fraud"
    public_disturbance = "public_disturbance"
    other = "other"


class IncidentSeverityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatusEnum(str, Enum):
    reported = "reported"
    under_investigation = "under_investigation"
    resolved = "resolved"
    closed = "closed"


class TrainingTypeEnum(str, Enum):
    firearms = "firearms"
    legal = "legal"
    physical = "physical"
    cyber = "cyber"
    first_aid = "first_aid"
    ethics = "ethics"


class TrainingAttendanceStatusEnum(str, Enum):
    registered = "registered"
    attended = "attended"
    absent = "absent"
    excused = "excused"


class AuditActionEnum(str, Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
