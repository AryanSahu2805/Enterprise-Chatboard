# Enterprise AI Customer Support System
# Complete system with Super Admin, Agents, and Public Client Interface

import os
import json
import datetime
import logging
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Core dependencies
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import sqlite3
import threading
import time
import openai

# MongoDB integration
try:
    from mongodb_config import mongodb
    MONGODB_AVAILABLE = True
    print("✅ MongoDB integration loaded successfully!")
    
    # Initialize MongoDB connection with timeout
    print("🔌 Connecting to MongoDB...")
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("MongoDB connection timed out")
    
    # Set 10 second timeout for MongoDB connection
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)
    
    try:
        if mongodb.connect():
            from agent_service import agent_service
            print("✅ Agent service loaded successfully!")
        else:
            MONGODB_AVAILABLE = False
            print("❌ MongoDB connection failed, agent service not available")
    finally:
        signal.alarm(0)  # Cancel the alarm
        
except ImportError as e:
    MONGODB_AVAILABLE = False
    print(f"⚠️ MongoDB integration not available: {e}")
    print("   Some features will be limited. Please set up MongoDB for full functionality.")
except TimeoutError:
    MONGODB_AVAILABLE = False
    print("⏰ MongoDB connection timed out, agent service not available")
    print("   Some features will be limited. Please check your MongoDB connection.")
except Exception as e:
    MONGODB_AVAILABLE = False
    print(f"❌ MongoDB error: {e}")
    print("   Some features will be limited. Please check your MongoDB setup.")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
bcrypt = Bcrypt(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DATABASE_URL = 'enterprise_chatbot.db'
    MAX_RESPONSE_TIME = 5.0  # seconds
    SESSION_TIMEOUT = 3600   # 1 hour
    ESCALATION_THRESHOLD = 0.7  # AI confidence threshold for escalation

# Initialize OpenAI client
client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

# Data models
class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    ESCALATION = "escalation"

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    AGENT = "agent"

class IssueStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

@dataclass
class User(UserMixin):
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    created_at: datetime.datetime
    last_login: Optional[datetime.datetime] = None
    is_active: bool = True

@dataclass
class Message:
    id: str
    session_id: str
    content: str
    sender: str  # 'user', 'bot', 'agent_{id}'
    message_type: MessageType
    timestamp: datetime.datetime
    confidence: Optional[float] = None
    intent: Optional[str] = None
    is_escalated: bool = False

@dataclass
class ChatSession:
    session_id: str
    start_time: datetime.datetime
    last_activity: datetime.datetime
    context: Dict
    status: IssueStatus
    escalated_at: Optional[datetime.datetime] = None
    assigned_agent: Optional[str] = None
    satisfaction_score: Optional[int] = None
    user_id: Optional[str] = None

@dataclass
class Escalation:
    id: str
    session_id: str
    reason: str
    ai_confidence: float
    timestamp: datetime.datetime
    status: IssueStatus
    assigned_agent: Optional[str] = None

# Register datetime adapters globally
def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(s):
    return datetime.datetime.fromisoformat(s.decode())

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)

# Database setup
def init_database():
    """Initialize SQLite database with enterprise tables"""
    conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
    
    cursor = conn.cursor()
    
    # Users table (Super Admin + Agents)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME,
            last_login DATETIME
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            content TEXT,
            sender TEXT,
            message_type TEXT,
            timestamp DATETIME,
            confidence REAL,
            intent TEXT,
            is_escalated BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            start_time DATETIME,
            last_activity DATETIME,
            context TEXT,
            status TEXT,
            assigned_agent TEXT,
            escalated_at DATETIME,
            satisfaction_score INTEGER
        )
    ''')
    
    # Escalations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS escalations (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            reason TEXT,
            ai_confidence REAL,
            timestamp DATETIME,
            assigned_agent TEXT,
            status TEXT
        )
    ''')
    
    # Analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            total_queries INTEGER,
            resolved_queries INTEGER,
            escalated_queries INTEGER,
            avg_response_time REAL,
            avg_satisfaction REAL,
            ai_success_rate REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Create default super admin if not exists
    create_default_super_admin()

def create_default_super_admin():
    """Create default super admin account"""
    conn = sqlite3.connect(Config.DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if super admin exists
    cursor.execute('SELECT id FROM users WHERE role = ?', (UserRole.SUPER_ADMIN.value,))
    if not cursor.fetchone():
        # Create default super admin
        admin_id = str(uuid.uuid4())
        password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            admin_id, 'superadmin', 'admin@company.com', password_hash,
            UserRole.SUPER_ADMIN.value, True, datetime.datetime.now()
        ))
        
        conn.commit()
        logger.info("Default super admin created: username='superadmin', password='admin123'")
    
    conn.close()

# User management
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, email, password_hash, role, is_active, created_at, last_login
        FROM users WHERE id = ?
    ''', (user_id,))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(
            id=user_data[0], username=user_data[1], email=user_data[2],
            password_hash=user_data[3], role=UserRole(user_data[4]),
            is_active=user_data[5], created_at=user_data[6], last_login=user_data[7]
        )
    return None

# Intent Recognition System
class IntentClassifier:
    def __init__(self):
        self.intents = {
            "greeting": {
                "patterns": ["hi", "hello", "good morning", "good afternoon", "hey", "howdy"],
                "responses": ["Hello! How can I help you today?", "Hi there! What can I assist you with?", "Welcome! How may I help you?"]
            },
            "goodbye": {
                "patterns": ["bye", "goodbye", "see you later", "thanks bye", "good night"],
                "responses": ["Goodbye! Have a great day!", "Thanks for chatting. Take care!", "See you later! Feel free to return if you need help."]
            },
            "support": {
                "patterns": ["help", "i need help", "can you help me", "support", "i have a problem", "assist"],
                "responses": ["I'm here to help! What seems to be the issue?", "Of course! Please describe your problem.", "I'd be happy to help. What do you need assistance with?"]
            },
            "billing": {
                "patterns": ["billing", "payment", "invoice", "charge", "bill", "cost", "price"],
                "responses": ["I can help with billing questions. Let me look into that for you.", "For billing inquiries, I'll need some details. What specific billing issue are you experiencing?"]
            },
            "technical": {
                "patterns": ["technical", "bug", "not working", "error", "broken", "issue", "problem"],
                "responses": ["I'll help you resolve this technical issue. Can you provide more details?", "Let me help you troubleshoot this. What exactly isn't working?"]
            },
            "human_agent": {
                "patterns": ["human", "agent", "person", "real person", "speak to someone", "talk to human"],
                "responses": ["I understand you'd like to speak with a human agent. Let me connect you with one of our specialists."]
            },
            "thanks": {
                "patterns": ["thank you", "thanks", "appreciate it", "grateful"],
                "responses": ["You're welcome! Is there anything else I can help you with?", "Happy to help! Let me know if you need anything else."]
            }
        }
    
    def predict_intent(self, text: str) -> tuple:
        """Predict intent from user message"""
        text_lower = text.lower()
        
        # Check for exact matches first
        for intent, data in self.intents.items():
            for pattern in data["patterns"]:
                if pattern in text_lower:
                    return intent, 0.9
        
        # Check for partial matches
        for intent, data in self.intents.items():
            for pattern in data["patterns"]:
                if any(word in text_lower for word in pattern.split()):
                    return intent, 0.7
        
        # Default to support if no match
        return "support", 0.5
    
    def get_response(self, intent: str) -> str:
        """Get predefined response for recognized intent"""
        if intent in self.intents:
            responses = self.intents[intent]["responses"]
            import random
            return random.choice(responses)
        return "I understand you're asking about that. Let me help you with more information."

# Chat Service with Escalation
class ChatService:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.active_sessions: Dict[str, ChatSession] = {}
        
    def create_session(self, session_id: str = None, user_id: Optional[str] = None) -> str:
        """Create new chat session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        now = datetime.datetime.now()
        
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            start_time=now,
            last_activity=now,
            context={'previous_messages': []},
            status=IssueStatus.OPEN
        )
        
        self.active_sessions[session_id] = chat_session
        self._save_session_to_db(chat_session)
        
        return session_id
    
    def _load_session_from_db(self, session_id: str) -> Optional[ChatSession]:
        """Load chat session from database"""
        try:
            conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, start_time, last_activity, context, status, user_id, escalated_at, assigned_agent, satisfaction_score
                FROM sessions WHERE session_id = ?
            ''', (session_id,))
            
            session_data = cursor.fetchone()
            conn.close()
            
            if session_data:
                # Parse context JSON
                context = json.loads(session_data[3]) if session_data[3] else {'previous_messages': []}
                
                return ChatSession(
                    session_id=session_data[0],
                    start_time=session_data[1],
                    last_activity=session_data[2],
                    context=context,
                    status=IssueStatus(session_data[4]),
                    user_id=session_data[5],
                    escalated_at=session_data[6],
                    assigned_agent=session_data[7],
                    satisfaction_score=session_data[8]
                )
            return None
            
        except Exception as e:
            logger.error(f"Error loading session from database: {e}")
            return None
    
    def process_message(self, session_id: str, user_message: str) -> Message:
        """Process user message and generate bot response"""
        start_time = time.time()
        
        # Get or create session
        if session_id not in self.active_sessions:
            # Try to load from database first
            chat_session = self._load_session_from_db(session_id)
            if not chat_session:
                # Session doesn't exist, create new one
                self.create_session(session_id)
            chat_session = self.active_sessions[session_id]
        
        chat_session = self.active_sessions[session_id]
        
        # Save user message
        user_msg = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content=user_message,
            sender='user',
            message_type=MessageType.TEXT,
            timestamp=datetime.datetime.now()
        )
        self._save_message_to_db(user_msg)
        
        # Predict intent
        intent, confidence = self.intent_classifier.predict_intent(user_message)
        
        # Check if escalation is needed
        if self._should_escalate(intent, confidence, user_message):
            # Save user message to context before escalation
            chat_session.context['previous_messages'].append(f"User: {user_message}")
            chat_session.last_activity = datetime.datetime.now()
            self._save_session_to_db(chat_session)
            return self._handle_escalation(session_id, user_message, intent, confidence)
        
        # Generate AI response using OpenAI
        response_text = self._generate_ai_response(user_message, chat_session.context)
        
        # If OpenAI fails, fallback to rule-based response
        if response_text is None:
            logger.info("OpenAI API failed, using fallback response")
            response_text = self.intent_classifier.get_response(intent)
        
        # Create bot response
        bot_response = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content=response_text,
            sender='bot',
            message_type=MessageType.TEXT,
            timestamp=datetime.datetime.now(),
            confidence=confidence,
            intent=intent
        )
        
        # Update session context
        chat_session.context['previous_messages'].append(f"User: {user_message}")
        if response_text:  # Only append if response_text is not None
            chat_session.context['previous_messages'].append(f"Bot: {response_text}")
        chat_session.last_activity = datetime.datetime.now()
        
        # Keep only last 20 messages in context
        if len(chat_session.context['previous_messages']) > 20:
            chat_session.context['previous_messages'] = chat_session.context['previous_messages'][-20:]
        
        # Save bot response
        self._save_message_to_db(bot_response)
        self._save_session_to_db(chat_session)
        
        # Log analytics
        response_time = time.time() - start_time
        self._log_analytics(response_time, intent)
        
        return bot_response
    
    def _should_escalate(self, intent: str, confidence: float, message: str) -> bool:
        """Determine if message should be escalated to human agent"""
        # Explicit request for human agent
        if intent == "human_agent":
            return True
        
        # Low AI confidence
        if confidence < Config.ESCALATION_THRESHOLD:
            return True
        
        # Complex technical issues
        technical_keywords = ["complex", "advanced", "detailed", "complicated", "specific"]
        if any(keyword in message.lower() for keyword in technical_keywords):
            return True
        
        return False
    
    def _handle_escalation(self, session_id: str, user_message: str, intent: str, confidence: float) -> Message:
        """Handle escalation to human agent"""
        chat_session = self.active_sessions[session_id]
        
        # Update session status
        chat_session.status = IssueStatus.ESCALATED
        chat_session.escalated_at = datetime.datetime.now()
        
        # Create escalation record
        escalation = Escalation(
            id=str(uuid.uuid4()),
            session_id=session_id,
            reason=f"Intent: {intent}, Confidence: {confidence:.2f}",
            ai_confidence=confidence,
            timestamp=datetime.datetime.now(),
            status=IssueStatus.OPEN
        )
        
        self._save_escalation_to_db(escalation)
        self._save_session_to_db(chat_session)
        
        # Create escalation message
        escalation_msg = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content="I'm connecting you with a human agent who will be able to help you better with this request. Please wait a moment while I transfer you.",
            sender='bot',
            message_type=MessageType.ESCALATION,
            timestamp=datetime.datetime.now(),
            confidence=confidence,
            intent=intent,
            is_escalated=True
        )
        
        self._save_message_to_db(escalation_msg)
        
        return escalation_msg
    
    def _generate_ai_response(self, user_message: str, context: Dict) -> str:
        """Generate AI response using OpenAI API"""
        try:
            # Check if we have a valid API key and quota
            if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY == 'your-openai-api-key':
                raise Exception("No valid OpenAI API key configured")
            
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful and professional customer support AI assistant. 
                    You help customers with their inquiries in a friendly, knowledgeable, and efficient manner. 
                    Keep responses concise but helpful. If you don't know something, be honest about it and offer to help find the right person or resource."""
                }
            ]
            
            # Add conversation history if available
            if context.get('previous_messages'):
                for msg in context['previous_messages'][-6:]:  # Last 6 messages for context
                    if msg.startswith('User: '):
                        messages.append({"role": "user", "content": msg[6:]})
                    elif msg.startswith('Bot: '):
                        messages.append({"role": "assistant", "content": msg[5:]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # Return None to trigger fallback
            return None
    
    def _save_message_to_db(self, message: Message):
        """Save message to database"""
        conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages 
            (id, session_id, content, sender, message_type, timestamp, confidence, intent, is_escalated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message.id, message.session_id, message.content, message.sender,
            message.message_type.value, message.timestamp, message.confidence, message.intent, message.is_escalated
        ))
        
        conn.commit()
        conn.close()
    
    def _save_session_to_db(self, session: ChatSession):
        """Save session to database"""
        conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (session_id, user_id, start_time, last_activity, context, status, assigned_agent, escalated_at, satisfaction_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.session_id, session.user_id, session.start_time,
            session.last_activity, json.dumps(session.context), session.status.value,
            session.assigned_agent, session.escalated_at, session.satisfaction_score
        ))
        
        conn.commit()
        conn.close()
    
    def _save_escalation_to_db(self, escalation: Escalation):
        """Save escalation to database"""
        conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO escalations 
            (id, session_id, reason, ai_confidence, timestamp, assigned_agent, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            escalation.id, escalation.session_id, escalation.reason,
            escalation.ai_confidence, escalation.timestamp, escalation.assigned_agent, escalation.status.value
        ))
        
        conn.commit()
        conn.close()
    
    def _log_analytics(self, response_time: float, intent: str):
        """Log analytics data"""
        logger.info(f"Response time: {response_time:.2f}s, Intent: {intent}")

# Initialize services
chat_service = ChatService()

# Flask Routes

# Public Client Interface
@app.route('/')
def index():
    """Render public client chat interface"""
    return render_template('client.html')

# Super Admin Interface
@app.route('/admin')
def admin_dashboard():
    """Super admin dashboard"""
    if not current_user.is_authenticated or current_user.role != UserRole.SUPER_ADMIN:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Super admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ? AND role = ?', 
                      (username, UserRole.SUPER_ADMIN.value))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and bcrypt.check_password_hash(user_data[3], password):
            user = User(
                id=user_data[0], username=user_data[1], email=user_data[2],
                password_hash=user_data[3], role=UserRole(user_data[4]),
                is_active=user_data[5], created_at=user_data[6], last_login=user_data[7]
            )
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

# Agent Interface
@app.route('/agent')
def agent_dashboard():
    """Agent dashboard"""
    if not current_user.is_authenticated or current_user.role != UserRole.AGENT:
        return redirect(url_for('agent_login'))
    return render_template('agent_dashboard.html')

@app.route('/agent/login', methods=['GET', 'POST'])
def agent_login():
    """Agent login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ? AND role = ? AND is_active = 1', 
                      (username, UserRole.AGENT.value))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and bcrypt.check_password_hash(user_data[3], password):
            user = User(
                id=user_data[0], username=user_data[1], email=user_data[2],
                password_hash=user_data[3], role=UserRole(user_data[4]),
                is_active=user_data[5], created_at=user_data[6], last_login=user_data[7]
            )
            login_user(user)
            return redirect(url_for('agent_dashboard'))
        else:
            flash('Invalid credentials or account inactive', 'error')
    
    return render_template('agent_login.html')

# API Routes
@app.route('/api/session', methods=['POST'])
def create_session():
    """Create new chat session"""
    user_id = request.json.get('user_id') if request.json else None
    session_id = chat_service.create_session(user_id)
    return jsonify({'session_id': session_id})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat message"""
    data = request.get_json()
    session_id = data.get('session_id')
    message = data.get('message')
    
    if not session_id or not message:
        return jsonify({'error': 'Missing session_id or message'}), 400
    
    try:
        response = chat_service.process_message(session_id, message)
        # Use custom JSON serialization to handle Message objects
        return jsonify({
            'id': response.id,
            'session_id': response.session_id,
            'content': response.content,
            'sender': response.sender,
            'message_type': response.message_type.value,
            'timestamp': response.timestamp.isoformat(),
            'confidence': response.confidence,
            'intent': response.intent,
            'is_escalated': response.is_escalated
        })
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    """Super admin user management"""
    if current_user.role != UserRole.SUPER_ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not all([username, email, password, role]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, role, True, datetime.datetime.now()))
            
            conn.commit()
            return jsonify({'success': True, 'user_id': user_id})
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username or email already exists'}), 400
        finally:
            conn.close()
    
    # GET - List all users
    conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email, role, is_active, created_at FROM users')
    users = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'users': [
            {
                'id': user[0], 'username': user[1], 'email': user[2],
                'role': user[3], 'is_active': user[4], 'created_at': user[5].isoformat()
            }
            for user in users
        ]
    })

# Logout routes
@app.route('/admin/logout')
@login_required
def admin_logout():
    """Super admin logout"""
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/agent/logout')
@login_required
def agent_logout():
    """Agent logout"""
    logout_user()
    return redirect(url_for('agent_login'))

# Agent API routes
@app.route('/api/agent/escalations')
@login_required
def get_escalations():
    """Get escalated issues for agents"""
    if current_user.role != UserRole.AGENT:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    # Get escalated issues
    cursor.execute('''
        SELECT id, session_id, reason, ai_confidence, timestamp, status
        FROM escalations 
        WHERE status = 'open' OR status = 'in_progress'
        ORDER BY timestamp DESC
    ''')
    
    escalations = cursor.fetchall()
    
    # Get total issues count
    cursor.execute('SELECT COUNT(*) FROM escalations')
    total_issues = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'escalations': [
            {
                'id': esc[0], 'session_id': esc[1], 'reason': esc[2],
                'ai_confidence': esc[3], 'timestamp': esc[4], 'status': esc[5]
            }
            for esc in escalations
        ],
        'total_issues': total_issues
    })

@app.route('/api/agent/chat-history/<session_id>')
@login_required
def get_chat_history(session_id):
    """Get chat history for a specific session"""
    if current_user.role != UserRole.AGENT:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT content, sender, timestamp
        FROM messages 
        WHERE session_id = ?
        ORDER BY timestamp ASC
    ''', (session_id,))
    
    messages = cursor.fetchall()
    
    return jsonify({
        'messages': [
            {
                'content': msg[0], 'sender': msg[1], 'timestamp': msg[2].isoformat()
            }
            for msg in messages
        ]
    })

@app.route('/api/agent/send-message', methods=['POST'])
@login_required
def agent_send_message():
    """Send message as agent"""
    if current_user.role != UserRole.AGENT:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    session_id = data.get('session_id')
    message = data.get('message')
    agent_id = data.get('agent_id')
    
    if not all([session_id, message, agent_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Save agent message
    agent_msg = Message(
        id=str(uuid.uuid4()),
        session_id=session_id,
        content=message,
        sender=f'agent_{agent_id}',
        message_type=MessageType.TEXT,
        timestamp=datetime.datetime.now()
    )
    
    chat_service._save_message_to_db(agent_msg)
    
    # Update escalation status
    conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE escalations 
        SET status = 'in_progress', assigned_agent = ?
        WHERE session_id = ?
    ''', (agent_id, session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/analytics')
def analytics():
    """Get analytics dashboard data"""
    conn = sqlite3.connect(Config.DATABASE_URL, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    # Get today's stats
    today = datetime.date.today()
    cursor.execute('''
        SELECT COUNT(*) as total_messages,
               AVG(confidence) as avg_confidence
        FROM messages 
        WHERE DATE(timestamp) = ? AND sender = 'bot'
    ''', (today,))
    
    stats = cursor.fetchone()
    
    # Get intent distribution
    cursor.execute('''
        SELECT intent, COUNT(*) as count
        FROM messages 
        WHERE DATE(timestamp) = ? AND sender = 'user' AND intent IS NOT NULL
        GROUP BY intent
    ''', (today,))
    
    intents = cursor.fetchall()
    
    # Get escalation stats
    cursor.execute('''
        SELECT COUNT(*) as escalated_count
        FROM escalations 
        WHERE DATE(timestamp) = ?
    ''', (today,))
    
    escalated = cursor.fetchone()
    
    conn.close()
    
    return jsonify({
        'total_messages': stats[0] or 0,
        'avg_confidence': stats[1] or 0,
        'intent_distribution': [{'intent': i[0], 'count': i[1]} for i in intents],
        'escalated_count': escalated[0] or 0
    })

# ============================================================================
# AGENT MANAGEMENT & AVAILABILITY SYSTEM
# ============================================================================

@app.route('/api/agent/status', methods=['POST'])
@login_required
def update_agent_status():
    """Update agent availability status"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    try:
        data = request.get_json()
        agent_id = current_user.id
        status = data.get('status')  # 'online' or 'offline'
        availability = data.get('availability')  # 'available', 'unavailable', 'busy', 'break'
        reason = data.get('reason', '')
        
        if not status or not availability:
            return jsonify({'error': 'Status and availability required'}), 400
        
        # Update agent status
        success = agent_service.update_agent_status(agent_id, status, availability, reason)
        
        if success:
            return jsonify({'message': 'Status updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update status'}), 500
            
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/agent/availability', methods=['GET'])
def get_available_agents():
    """Get list of currently available agents"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    try:
        available_agents = agent_service.get_available_agents()
        
        agents_data = []
        for agent in available_agents:
            agents_data.append({
                'id': agent.id,
                'username': agent.username,
                'first_name': agent.first_name,
                'last_name': agent.last_name,
                'skills': agent.skills,
                'avg_rating': agent.avg_rating
            })
        
        return jsonify({'agents': agents_data}), 200
        
    except Exception as e:
        logger.error(f"Error getting available agents: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/agent/random', methods=['GET'])
def get_random_agent():
    """Get a random available agent for customer queries"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    try:
        agent = agent_service.get_random_available_agent()
        
        if agent:
            return jsonify({
                'agent_id': agent.id,
                'name': f"{agent.first_name} {agent.last_name}",
                'skills': agent.skills
            }), 200
        else:
            return jsonify({'error': 'No agents available'}), 404
            
    except Exception as e:
        logger.error(f"Error getting random agent: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/agent/hours/<agent_id>', methods=['GET'])
def get_agent_hours(agent_id):
    """Get agent's working hours"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    try:
        # Get today's hours
        today_hours = agent_service.get_agent_hours_today(agent_id)
        
        # Get date range if provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            range_hours = agent_service.get_agent_hours_range(agent_id, start_date, end_date)
        else:
            range_hours = 0.0
        
        return jsonify({
            'agent_id': agent_id,
            'today_hours': today_hours,
            'range_hours': range_hours,
            'start_date': start_date,
            'end_date': end_date
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting agent hours: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/agent/feedback', methods=['POST'])
def add_customer_feedback():
    """Add customer feedback for an agent"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    try:
        data = request.get_json()
        required_fields = ['session_id', 'agent_id', 'rating', 'comment']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create feedback
        feedback_data = {
            'session_id': data['session_id'],
            'agent_id': data['agent_id'],
            'customer_id': data.get('customer_id', 'anonymous'),
            'rating': int(data['rating']),
            'comment': data['comment'],
            'feedback_type': data.get('feedback_type', 'general')
        }
        
        feedback_id = agent_service.add_customer_feedback(feedback_data)
        
        if feedback_id:
            return jsonify({
                'message': 'Feedback submitted successfully',
                'feedback_id': feedback_id
            }), 201
        else:
            return jsonify({'error': 'Failed to submit feedback'}), 500
            
    except Exception as e:
        logger.error(f"Error adding feedback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/agent/feedback/<agent_id>', methods=['GET'])
def get_agent_feedback(agent_id):
    """Get feedback for a specific agent"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    try:
        limit = request.args.get('limit', 50, type=int)
        feedback_list = agent_service.get_agent_feedback(agent_id, limit)
        
        feedback_data = []
        for feedback in feedback_list:
            feedback_data.append({
                'id': feedback.id,
                'session_id': feedback.session_id,
                'rating': feedback.rating.value,
                'comment': feedback.comment,
                'feedback_type': feedback.feedback_type,
                'created_at': feedback.created_at.isoformat(),
                'is_resolved': feedback.is_resolved
            })
        
        return jsonify({'feedback': feedback_data}), 200
        
    except Exception as e:
        logger.error(f"Error getting agent feedback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/agent/performance/<agent_id>', methods=['GET'])
def get_agent_performance(agent_id):
    """Get agent performance metrics"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            # Default to last 30 days
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        
        performance = agent_service.get_agent_performance(agent_id, start_date, end_date)
        
        performance_data = []
        for perf in performance:
            performance_data.append({
                'date': perf.date,
                'total_hours': perf.total_hours,
                'total_sessions': perf.total_sessions,
                'avg_rating': perf.avg_rating,
                'total_feedback': perf.total_feedback
            })
        
        return jsonify({
            'agent_id': agent_id,
            'start_date': start_date,
            'end_date': end_date,
            'performance': performance_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/agents', methods=['GET'])
@login_required
def get_all_agents():
    """Get summary of all agents for Super Admin"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    if current_user.role != UserRole.SUPER_ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        agents_summary = agent_service.get_all_agents_summary()
        return jsonify({'agents': agents_summary}), 200
        
    except Exception as e:
        logger.error(f"Error getting agents summary: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/admin/agent/<agent_id>', methods=['GET'])
@login_required
def get_agent_details(agent_id):
    """Get detailed information about a specific agent"""
    if not MONGODB_AVAILABLE:
        return jsonify({'error': 'MongoDB not available'}), 503
    
    if current_user.role != UserRole.SUPER_ADMIN:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Get agent analytics
        analytics = agent_service.get_agent_analytics(agent_id)
        
        if analytics:
            return jsonify(analytics), 200
        else:
            return jsonify({'error': 'Agent not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting agent details: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'Connected to chatbot'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('ping')
def handle_ping():
    """Handle ping for health check"""
    emit('pong', {'timestamp': datetime.datetime.now().isoformat()})

@socketio.on('message')
def handle_message(data):
    """Handle real-time message"""
    session_id = data.get('session_id')
    message = data.get('message')
    
    if session_id and message:
        # Emit typing indicator
        emit('typing', {'typing': True})
        
        # Process message
        response = chat_service.process_message(session_id, message)
        
        # Emit response using custom serialization
        emit('typing', {'typing': False})
        emit('response', {
            'id': response.id,
            'session_id': response.session_id,
            'content': response.content,
            'sender': response.sender,
            'message_type': response.message_type.value,
            'timestamp': response.timestamp.isoformat(),
            'confidence': response.confidence,
            'intent': response.intent,
            'is_escalated': response.is_escalated
        })

if __name__ == '__main__':
    # Initialize database and services
    init_database()
    
    # MongoDB already initialized during import
    if MONGODB_AVAILABLE:
        print("✅ MongoDB: Already connected - Full functionality available")
    else:
        print("⚠️ MongoDB: Not available - Limited functionality")
    
    print("🚀 Starting Enterprise AI Customer Support System...")
    print("👑 Super Admin: /admin (username: superadmin, password: admin123)")
    print("👥 Agent Interface: /agent")
    print("🌐 Public Client: /")
    print("📊 Features: AI Chat, Human Escalation, Agent Management, Analytics")
    print("🔗 Access at: http://localhost:8000")
    
    if MONGODB_AVAILABLE:
        print("🗄️ MongoDB: Connected - Full functionality available")
        print("   - Agent Availability System")
        print("   - Hours Tracking")
        print("   - Customer Feedback")
        print("   - Performance Analytics")
    else:
        print("⚠️ MongoDB: Not available - Limited functionality")
    
    # Run the application
    try:
        print("🚀 Starting with SocketIO...")
        socketio.run(app, debug=True, host='0.0.0.0', port=8000)
    except Exception as e:
        print(f"⚠️ SocketIO failed: {e}")
        print("🔄 Falling back to Flask development server...")
        app.run(debug=True, host='0.0.0.0', port=8000)
