from app.crud.base import CRUDBase
from app.crud.user import crud_user
from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.officer import Officer
from app.models.operation import Operation
from app.models.operation_participant import OperationParticipant
from app.models.patrol import Patrol
from app.models.promotion import Promotion
from app.models.rank import Rank
from app.models.training_attendance import TrainingAttendance
from app.models.training_session import TrainingSession
from app.models.unit import Unit
from app.models.unit_assignment import UnitAssignment
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.schemas.officer import OfficerCreate, OfficerUpdate
from app.schemas.operation import OperationCreate, OperationUpdate
from app.schemas.operation_participant import (
    OperationParticipantCreate,
    OperationParticipantUpdate,
)
from app.schemas.patrol import PatrolCreate, PatrolUpdate
from app.schemas.promotion import PromotionCreate, PromotionUpdate
from app.schemas.rank import RankCreate, RankUpdate
from app.schemas.training_attendance import (
    TrainingAttendanceCreate,
    TrainingAttendanceUpdate,
)
from app.schemas.training_session import TrainingSessionCreate, TrainingSessionUpdate
from app.schemas.unit import UnitCreate, UnitUpdate
from app.schemas.unit_assignment import UnitAssignmentCreate, UnitAssignmentUpdate

crud_rank = CRUDBase[Rank, RankCreate, RankUpdate](Rank)
crud_unit = CRUDBase[Unit, UnitCreate, UnitUpdate](Unit)
crud_officer = CRUDBase[Officer, OfficerCreate, OfficerUpdate](Officer)
crud_promotion = CRUDBase[Promotion, PromotionCreate, PromotionUpdate](Promotion)
crud_unit_assignment = CRUDBase[UnitAssignment, UnitAssignmentCreate, UnitAssignmentUpdate](
    UnitAssignment
)
crud_operation = CRUDBase[Operation, OperationCreate, OperationUpdate](Operation)
crud_operation_participant = CRUDBase[
    OperationParticipant, OperationParticipantCreate, OperationParticipantUpdate
](OperationParticipant)
crud_patrol = CRUDBase[Patrol, PatrolCreate, PatrolUpdate](Patrol)
crud_incident = CRUDBase[Incident, IncidentCreate, IncidentUpdate](Incident)
crud_training_session = CRUDBase[
    TrainingSession, TrainingSessionCreate, TrainingSessionUpdate
](TrainingSession)
crud_training_attendance = CRUDBase[
    TrainingAttendance, TrainingAttendanceCreate, TrainingAttendanceUpdate
](TrainingAttendance)
crud_audit_log = CRUDBase[AuditLog, None, None](AuditLog)

__all__ = [
    "crud_rank",
    "crud_unit",
    "crud_officer",
    "crud_user",
    "crud_promotion",
    "crud_unit_assignment",
    "crud_operation",
    "crud_operation_participant",
    "crud_patrol",
    "crud_incident",
    "crud_training_session",
    "crud_training_attendance",
    "crud_audit_log",
]
