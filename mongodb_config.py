import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBConfig:
    """MongoDB Configuration and Connection Management"""
    
    def __init__(self):
        self.connection_string = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.database_name = os.getenv('MONGODB_DB', 'enterprise_chatbot')
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            # Add timeout settings to prevent hanging
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,          # 5 second connection timeout
                socketTimeoutMS=5000            # 5 second socket timeout
            )
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ MongoDB connection established successfully!")
            
            # Initialize collections
            self._initialize_collections()
            
            return True
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            return False
    
    def _initialize_collections(self):
        """Initialize all required collections with proper indexes"""
        try:
            # Agents collection
            agents = self.db.agents
            agents.create_index("username", unique=True)
            agents.create_index("email", unique=True)
            agents.create_index("status")  # online/offline
            agents.create_index("availability")  # available/unavailable
            
            # Agent Sessions collection (for tracking hours)
            agent_sessions = self.db.agent_sessions
            agent_sessions.create_index([("agent_id", 1), ("date", 1)])
            agent_sessions.create_index("start_time")
            agent_sessions.create_index("end_time")
            
            # Customer Feedback collection
            customer_feedback = self.db.customer_feedback
            customer_feedback.create_index([("agent_id", 1), ("created_at", -1)])
            customer_feedback.create_index("session_id")
            customer_feedback.create_index("rating")
            
            # Agent Performance collection
            agent_performance = self.db.agent_performance
            agent_performance.create_index([("agent_id", 1), ("date", 1)])
            agent_performance.create_index("total_hours")
            agent_performance.create_index("avg_rating")
            
            print("✅ MongoDB collections initialized successfully!")
            
        except Exception as e:
            print(f"❌ Collection initialization failed: {e}")
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        return self.db[collection_name]
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed")

# Global MongoDB instance
mongodb = MongoDBConfig()
