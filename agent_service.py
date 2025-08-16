from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
import random

from mongodb_config import mongodb
from agent_models import (
    Agent, AgentSession, CustomerFeedback, AgentPerformance, 
    AgentAvailabilityUpdate, AgentStatus, AgentAvailability, FeedbackRating
)

class AgentService:
    """Service layer for agent management operations"""
    
    def __init__(self):
        self._agents_collection = None
        self._sessions_collection = None
        self._feedback_collection = None
        self._performance_collection = None
    
    @property
    def agents_collection(self):
        if self._agents_collection is None:
            self._agents_collection = mongodb.get_collection('agents')
        return self._agents_collection
    
    @property
    def sessions_collection(self):
        if self._sessions_collection is None:
            self._sessions_collection = mongodb.get_collection('agent_sessions')
        return self._sessions_collection
    
    @property
    def feedback_collection(self):
        if self._feedback_collection is None:
            self._feedback_collection = mongodb.get_collection('customer_feedback')
        return self._feedback_collection
    
    @property
    def performance_collection(self):
        if self._performance_collection is None:
            self._performance_collection = mongodb.get_collection('agent_performance')
        return self._performance_collection
    
    # Agent Management Methods
    def create_agent(self, agent_data: Dict[str, Any]) -> Optional[str]:
        """Create a new agent"""
        try:
            agent = Agent(**agent_data)
            result = self.agents_collection.insert_one(agent.to_dict())
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating agent: {e}")
            return None
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        try:
            agent_data = self.agents_collection.find_one({"_id": ObjectId(agent_id)})
            if agent_data:
                agent_data["id"] = str(agent_data["_id"])
                del agent_data["_id"]
                return Agent.from_dict(agent_data)
            return None
        except Exception as e:
            print(f"Error getting agent: {e}")
            return None
    
    def get_agent_by_username(self, username: str) -> Optional[Agent]:
        """Get agent by username"""
        try:
            agent_data = self.agents_collection.find_one({"username": username})
            if agent_data:
                agent_data["id"] = str(agent_data["_id"])
                del agent_data["_id"]
                return Agent.from_dict(agent_data)
            return None
        except Exception as e:
            print(f"Error getting agent by username: {e}")
            return None
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, availability: AgentAvailability, reason: str = "") -> bool:
        """Update agent status and availability"""
        try:
            update_data = {
                "status": status.value,
                "availability": availability.value,
                "last_status_change": datetime.utcnow()
            }
            
            result = self.agents_collection.update_one(
                {"_id": ObjectId(agent_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Log the status change
                status_update = AgentAvailabilityUpdate(
                    agent_id=agent_id,
                    status=status,
                    availability=availability,
                    reason=reason
                )
                
                # Start/stop session tracking
                if status == AgentStatus.ONLINE and availability == AgentAvailability.AVAILABLE:
                    self._start_agent_session(agent_id)
                elif status == AgentStatus.OFFLINE or availability == AgentAvailability.UNAVAILABLE:
                    self._end_agent_session(agent_id)
                
                return True
            return False
        except Exception as e:
            print(f"Error updating agent status: {e}")
            return False
    
    def get_available_agents(self) -> List[Agent]:
        """Get all currently available agents"""
        try:
            available_agents = self.agents_collection.find({
                "status": AgentStatus.ONLINE.value,
                "availability": AgentAvailability.AVAILABLE.value,
                "is_active": True
            })
            
            agents = []
            for agent_data in available_agents:
                agent_data["id"] = str(agent_data["_id"])
                del agent_data["_id"]
                agents.append(Agent.from_dict(agent_data))
            
            return agents
        except Exception as e:
            print(f"Error getting available agents: {e}")
            return []
    
    def get_random_available_agent(self) -> Optional[Agent]:
        """Get a random available agent for customer queries"""
        try:
            available_agents = self.get_available_agents()
            if available_agents:
                return random.choice(available_agents)
            return None
        except Exception as e:
            print(f"Error getting random agent: {e}")
            return None
    
    # Session Management Methods
    def _start_agent_session(self, agent_id: str) -> bool:
        """Start tracking agent work session"""
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Check if session already exists for today
            existing_session = self.sessions_collection.find_one({
                "agent_id": agent_id,
                "date": today,
                "status": "active"
            })
            
            if not existing_session:
                session = AgentSession(
                    agent_id=agent_id,
                    date=today,
                    start_time=datetime.utcnow()
                )
                
                result = self.sessions_collection.insert_one(session.to_dict())
                return result.inserted_id is not None
            
            return True
        except Exception as e:
            print(f"Error starting agent session: {e}")
            return False
    
    def _end_agent_session(self, agent_id: str) -> bool:
        """End agent work session and calculate hours"""
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Find active session
            session = self.sessions_collection.find_one({
                "agent_id": agent_id,
                "date": today,
                "status": "active"
            })
            
            if session:
                end_time = datetime.utcnow()
                start_time = session["start_time"]
                
                # Calculate hours worked
                duration = end_time - start_time
                hours_worked = duration.total_seconds() / 3600
                
                # Update session
                self.sessions_collection.update_one(
                    {"_id": session["_id"]},
                    {
                        "$set": {
                            "end_time": end_time,
                            "total_hours": hours_worked,
                            "status": "completed"
                        }
                    }
                )
                
                # Update agent total hours
                self.agents_collection.update_one(
                    {"_id": ObjectId(agent_id)},
                    {"$inc": {"total_hours_worked": hours_worked}}
                )
                
                # Update performance metrics
                self._update_agent_performance(agent_id, today, hours_worked)
                
                return True
            
            return False
        except Exception as e:
            print(f"Error ending agent session: {e}")
            return False
    
    def get_agent_hours_today(self, agent_id: str) -> float:
        """Get agent's total hours worked today"""
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            pipeline = [
                {"$match": {"agent_id": agent_id, "date": today}},
                {"$group": {"_id": None, "total_hours": {"$sum": "$total_hours"}}}
            ]
            
            result = list(self.sessions_collection.aggregate(pipeline))
            if result:
                return result[0]["total_hours"]
            return 0.0
        except Exception as e:
            print(f"Error getting agent hours: {e}")
            return 0.0
    
    def get_agent_hours_range(self, agent_id: str, start_date: str, end_date: str) -> float:
        """Get agent's total hours worked in a date range"""
        try:
            pipeline = [
                {"$match": {
                    "agent_id": agent_id,
                    "date": {"$gte": start_date, "$lte": end_date}
                }},
                {"$group": {"_id": None, "total_hours": {"$sum": "$total_hours"}}}
            ]
            
            result = list(self.sessions_collection.aggregate(pipeline))
            if result:
                return result[0]["total_hours"]
            return 0.0
        except Exception as e:
            print(f"Error getting agent hours range: {e}")
            return 0.0
    
    # Feedback Management Methods
    def add_customer_feedback(self, feedback_data: Dict[str, Any]) -> Optional[str]:
        """Add customer feedback for an agent"""
        try:
            feedback = CustomerFeedback(**feedback_data)
            result = self.feedback_collection.insert_one(feedback.to_dict())
            
            if result.inserted_id:
                # Update agent's average rating
                self._update_agent_rating(feedback.agent_id)
                return str(result.inserted_id)
            return None
        except Exception as e:
            print(f"Error adding feedback: {e}")
            return None
    
    def get_agent_feedback(self, agent_id: str, limit: int = 50) -> List[CustomerFeedback]:
        """Get feedback for a specific agent"""
        try:
            feedback_data = self.feedback_collection.find(
                {"agent_id": agent_id}
            ).sort("created_at", -1).limit(limit)
            
            feedback_list = []
            for fb in feedback_data:
                fb["id"] = str(fb["_id"])
                del fb["_id"]
                feedback_list.append(CustomerFeedback.from_dict(fb))
            
            return feedback_list
        except Exception as e:
            print(f"Error getting agent feedback: {e}")
            return []
    
    def _update_agent_rating(self, agent_id: str) -> bool:
        """Update agent's average rating"""
        try:
            pipeline = [
                {"$match": {"agent_id": agent_id}},
                {"$group": {
                    "_id": None,
                    "avg_rating": {"$avg": "$rating"},
                    "total_feedback": {"$sum": 1}
                }}
            ]
            
            result = list(self.feedback_collection.aggregate(pipeline))
            if result:
                avg_rating = result[0]["avg_rating"]
                total_feedback = result[0]["total_feedback"]
                
                self.agents_collection.update_one(
                    {"_id": ObjectId(agent_id)},
                    {
                        "$set": {
                            "avg_rating": round(avg_rating, 2),
                            "total_feedback": total_feedback
                        }
                    }
                )
                return True
            
            return False
        except Exception as e:
            print(f"Error updating agent rating: {e}")
            return False
    
    # Performance Management Methods
    def _update_agent_performance(self, agent_id: str, date: str, hours_worked: float) -> bool:
        """Update agent performance metrics"""
        try:
            # Get or create performance record
            performance = self.performance_collection.find_one({
                "agent_id": agent_id,
                "date": date
            })
            
            if performance:
                # Update existing record
                self.performance_collection.update_one(
                    {"_id": performance["_id"]},
                    {
                        "$inc": {
                            "total_hours": hours_worked,
                            "total_sessions": 1
                        },
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
            else:
                # Create new record
                new_performance = AgentPerformance(
                    agent_id=agent_id,
                    date=date,
                    total_hours=hours_worked,
                    total_sessions=1
                )
                self.performance_collection.insert_one(new_performance.to_dict())
            
            return True
        except Exception as e:
            print(f"Error updating agent performance: {e}")
            return False
    
    def get_agent_performance(self, agent_id: str, start_date: str, end_date: str) -> List[AgentPerformance]:
        """Get agent performance in a date range"""
        try:
            performance_data = self.performance_collection.find({
                "agent_id": agent_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }).sort("date", 1)
            
            performance_list = []
            for perf in performance_data:
                perf["id"] = str(perf["_id"])
                del perf["_id"]
                performance_list.append(AgentPerformance.from_dict(perf))
            
            return performance_list
        except Exception as e:
            print(f"Error getting agent performance: {e}")
            return []
    
    # Analytics Methods
    def get_agent_analytics(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for an agent"""
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Get today's hours
            today_hours = self.get_agent_hours_today(agent_id)
            
            # Get this week's hours
            week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
            week_hours = self.get_agent_hours_range(agent_id, week_ago, today)
            
            # Get this month's hours
            month_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            month_hours = self.get_agent_hours_range(agent_id, month_ago, today)
            
            # Get recent feedback
            recent_feedback = self.get_agent_feedback(agent_id, limit=10)
            
            # Get agent info
            agent = self.get_agent_by_id(agent_id)
            
            analytics = {
                "today_hours": round(today_hours, 2),
                "week_hours": round(week_hours, 2),
                "month_hours": round(month_hours, 2),
                "total_hours": round(agent.total_hours_worked, 2) if agent else 0.0,
                "avg_rating": round(agent.avg_rating, 2) if agent else 0.0,
                "total_feedback": agent.total_feedback if agent else 0,
                "recent_feedback": recent_feedback,
                "current_status": agent.status.value if agent else "offline",
                "current_availability": agent.availability.value if agent else "unavailable"
            }
            
            return analytics
        except Exception as e:
            print(f"Error getting agent analytics: {e}")
            return {}
    
    def get_all_agents_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all agents for Super Admin"""
        try:
            agents = self.agents_collection.find({"is_active": True})
            
            summary = []
            for agent_data in agents:
                agent_id = str(agent_data["_id"])
                
                # Get today's hours
                today_hours = self.get_agent_hours_today(agent_id)
                
                # Get recent feedback
                recent_feedback = self.get_agent_feedback(agent_id, limit=5)
                
                summary.append({
                    "id": agent_id,
                    "username": agent_data["username"],
                    "first_name": agent_data["first_name"],
                    "last_name": agent_data["last_name"],
                    "status": agent_data["status"],
                    "availability": agent_data["availability"],
                    "today_hours": round(today_hours, 2),
                    "total_hours": round(agent_data["total_hours_worked"], 2),
                    "avg_rating": round(agent_data["avg_rating"], 2),
                    "total_feedback": agent_data["total_feedback"],
                    "recent_feedback": recent_feedback,
                    "last_status_change": agent_data["last_status_change"]
                })
            
            return summary
        except Exception as e:
            print(f"Error getting agents summary: {e}")
            return []

# Global agent service instance
agent_service = AgentService()
