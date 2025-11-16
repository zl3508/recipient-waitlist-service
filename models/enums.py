from enum import Enum

class BloodType(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"

class OrganType(str, Enum):
    HEART = "heart"
    LIVER = "liver"
    KIDNEY = "kidney"
    LUNG = "lung"
    PANCREAS = "pancreas"
    INTESTINE = "intestine"

class CommonStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class NeedStatus(str, Enum):
    WAITING = "waiting"
    MATCHED = "matched"
    REMOVED = "removed"

#class UrgencyLevel(str, Enum):
  #  LOW = "low"
   # MEDIUM= "medium"
   # HIGH = "high"
   # CRITICAL = "critical"
