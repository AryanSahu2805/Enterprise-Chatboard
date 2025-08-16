from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import Enum

class AgentStatus(Enum):
    """Agent online/offline status"""
    ONLINE = "online"
    OFFLINE = "offline"

class AgentAvailability(Enum):
    """Agent availability for customer queries"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BUSY = "busy"
    BREAK = "break"

class FeedbackRating(Enum):
    """Customer feedback ratings"""
    EXCELLENT = 5
    VERY_GOOD = 4
    GOOD = 3
    FAIR = 2
    POOR = 1

@dataclass
class Agent:
    """Agent model for the system"""
    id: Optional[str] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    first_name: str = ""
    last_name: str = ""
    status: AgentStatus = AgentStatus.OFFLINE
    availability: AgentAvailability = AgentAvailability.UNAVAILABLE
    skills: List[str] = None
    hourly_rate: float = 0.0
    total_hours_worked: float = 0.0
    avg_rating: float = 0.0
    total_feedback: int = 0
    is_active: bool = True
    created_at: datetime = None
    last_login: datetime = None
    last_status_change: datetime = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_status_change is None:
            self.last_status_change = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        data['status'] = self.status.value
        data['availability'] = self.availability.value
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create Agent instance from dictionary"""
        if 'status' in data:
            data['status'] = AgentStatus(data['status'])
        if 'availability' in data:
            data['availability'] = AgentAvailability(data['availability'])
        return cls(**data)

@dataclass
class AgentSession:
    """Agent work session for tracking hours"""
    id: Optional[str] = None
    agent_id: str = ""
    date: str = ""  # YYYY-MM-DD format
    start_time: datetime = None
    end_time: Optional[datetime] = None
    total_hours: float = 0.0
    status: str = "active"  # active, completed, paused
    notes: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        """Create AgentSession instance from dictionary"""
        return cls(**data)

@dataclass
class CustomerFeedback:
    """Customer feedback for agent interactions"""
    id: Optional[str] = None
    session_id: str = ""
    agent_id: str = ""
    customer_id: str = ""
    rating: FeedbackRating = FeedbackRating.GOOD
    comment: str = ""
    feedback_type: str = "general"  # general, technical, service, etc.
    is_resolved: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        data['rating'] = self.rating.value
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create CustomerFeedback instance from dictionary"""
        if 'rating' in data:
            data['rating'] = FeedbackRating(data['rating'])
        return cls(**data)

@dataclass
class AgentPerformance:
    """Agent performance metrics"""
    id: Optional[str] = None
    agent_id: str = ""
    date: str = ""  # YYYY-MM-DD format
    total_hours: float = 0.0
    total_sessions: int = 0
    avg_rating: float = 0.0
    total_feedback: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    response_time_avg: float = 0.0
    customer_satisfaction: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        """Create AgentPerformance instance from dictionary"""
        return cls(**data)

@dataclass
class AgentAvailabilityUpdate:
    """Agent availability status update"""
    agent_id: str = ""
    status: AgentStatus = AgentStatus.OFFLINE
    availability: AgentAvailability = AgentAvailability.UNAVAILABLE
    reason: str = ""
    estimated_return: Optional[datetime] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        data = asdict(self)
        data['status'] = self.status.value
        data['availability'] = self.availability.value
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create AgentAvailabilityUpdate instance from dictionary"""
        if 'status' in data:
            data['status'] = AgentStatus(data['status'])
        if 'availability' in data:
            data['availability'] = AgentAvailability(data['availability'])
        return cls(**data)
