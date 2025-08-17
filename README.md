# 🚀 Enterprise AI Customer Support System

A comprehensive, enterprise-grade customer support system that combines AI-powered responses with human agent escalation, featuring real-time chat, agent management, analytics, and hybrid database architecture.

## ✨ **Latest Updates & Features (v2.0)**

### 🔧 **Critical Bug Fixes & Improvements**
- ✅ **Fixed Online/Offline Button**: Resolved authentication routing conflicts and HTML structure issues
- ✅ **Real-time Data Integration**: Replaced all mock data with live SQLite database connections
- ✅ **Enhanced Authentication**: Custom login routing for different user types (Admin vs Agent)
- ✅ **Comprehensive Loading States**: Added proper loading, error, and empty states across all interfaces
- ✅ **Database Schema Updates**: Added `agent_sessions` table and `total_working_hours` tracking
- ✅ **Agent Status Management**: Real-time online/offline status with working hours calculation

### 🤖 **AI-Powered Chat System**
- **OpenAI Integration**: Uses GPT-3.5-turbo for intelligent customer responses
- **Intent Classification**: Automatically detects customer intent and routes appropriately
- **Smart Escalation**: Seamlessly escalates complex queries to human agents
- **Fallback System**: Rule-based responses when AI is unavailable
- **Real-time Chat**: WebSocket-based communication for instant updates
- **Session Management**: Persistent chat sessions with context preservation

### 👥 **Human Agent System**
- **Agent Management**: Super Admin can create, assign, and manage agent accounts
- **Availability Control**: Agents can mark themselves as online/offline and available/unavailable
- **Working Hours Tracking**: Automatic tracking of agent working hours for payment purposes
- **Real-time Status Updates**: Live status monitoring for admin oversight
- **Performance Metrics**: Individual agent performance tracking and analytics
- **Session Timer**: Daily reset timer with session resume functionality

### 🔐 **Enhanced Authentication & Roles**
- **Super Admin**: Full system control, agent management, analytics access
- **Agent Accounts**: Individual login credentials with role-based permissions
- **Secure Authentication**: Flask-Login with bcrypt password hashing
- **Custom Login Routing**: Different login pages for admin and agent users
- **Session Management**: Secure session handling with automatic timeouts

### 📊 **Advanced Analytics & Monitoring**
- **Real-time Dashboard**: Live statistics and performance metrics
- **Customer Feedback System**: Rating system for human agent interactions
- **Performance Reports**: Response times, resolution rates, and agent performance
- **Audit Logs**: Comprehensive system activity tracking
- **Agent Performance Metrics**: Individual agent statistics and working hours
- **System Health Monitoring**: Real-time system status and performance indicators

### 🌐 **Responsive Design & UX**
- **Mobile-First Design**: Optimized for mobile devices
- **Desktop Compatible**: Full-featured interface for larger screens
- **Loading States**: Visual feedback during data loading operations
- **Error Handling**: User-friendly error messages and recovery options
- **Empty States**: Helpful messages when no data is available
- **Modern UI Components**: Professional dashboard design with Chart.js integration

## 🏗️ **System Architecture & Technology Stack**

### **🏛️ High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                    Enterprise AI Chatbot System                 │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer (Client Interface)                             │
│  ├── Public Client Interface (/)                               │
│  ├── Agent Dashboard (/agent)                                  │
│  └── Admin Dashboard (/admin)                                  │
├─────────────────────────────────────────────────────────────────┤
│  Application Layer (Flask Backend)                             │
│  ├── Web Server (Flask + SocketIO)                            │
│  ├── Authentication & Authorization                            │
│  ├── AI Chat Engine (OpenAI Integration)                      │
│  ├── Agent Management System                                   │
│  └── Real-time Communication Hub                               │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer (Hybrid Database)                                  │
│  ├── SQLite (Primary: Chat, Users, Sessions)                  │
│  ├── MongoDB (Optional: Agent Management)                     │
│  └── File System (Logs, Configurations)                       │
├─────────────────────────────────────────────────────────────────┤
│  External Services                                             │
│  ├── OpenAI API (AI Responses)                                 │
│  ├── MongoDB Atlas (Cloud Database)                            │
│  └── WebSocket Server (Real-time Updates)                     │
└─────────────────────────────────────────────────────────────────┘
```

### **🔧 Backend Framework Architecture**
- **Flask Core**: Python web framework with modular blueprint architecture
- **Flask-SocketIO**: Real-time bidirectional communication for live chat
- **Flask-Login**: User session management with custom authentication handlers
- **Flask-Bcrypt**: Secure password hashing and verification system
- **Flask-CORS**: Cross-origin resource sharing for API accessibility
- **Blueprint Pattern**: Modular route organization for scalability

### **🗄️ Database Architecture & Schema**

#### **SQLite Database (Primary)**
```sql
-- Core User Management
users:
  - id (UUID, Primary Key)
  - username (VARCHAR, Unique)
  - email (VARCHAR, Unique)
  - password_hash (VARCHAR, Bcrypt)
  - role (ENUM: super_admin, agent)
  - created_at (DATETIME)
  - last_login (DATETIME)
  - total_working_hours (REAL, Default: 0)

-- Chat Session Management
sessions:
  - session_id (UUID, Primary Key)
  - start_time (DATETIME)
  - last_activity (DATETIME)
  - context (JSON)
  - status (ENUM: open, in_progress, resolved, escalated)
  - escalated_at (DATETIME, Nullable)
  - assigned_agent (UUID, Foreign Key to users.id)
  - satisfaction_score (INTEGER, Nullable)
  - user_id (UUID, Nullable)

-- Message Storage
messages:
  - id (UUID, Primary Key)
  - session_id (UUID, Foreign Key to sessions.session_id)
  - content (TEXT)
  - sender (VARCHAR: 'user', 'bot', 'agent_{id}')
  - message_type (ENUM: text, image, file, system, escalation)
  - timestamp (DATETIME)
  - confidence (REAL, Nullable)
  - intent (VARCHAR, Nullable)
  - is_escalated (BOOLEAN, Default: false)

-- Escalation Tracking
escalations:
  - id (UUID, Primary Key)
  - session_id (UUID, Foreign Key to sessions.session_id)
  - reason (TEXT)
  - ai_confidence (REAL)
  - timestamp (DATETIME)
  - status (ENUM: open, in_progress, resolved, escalated)
  - assigned_agent (UUID, Foreign Key to users.id)

-- Agent Session Tracking
agent_sessions:
  - id (INTEGER, Primary Key, Auto-increment)
  - agent_id (UUID, Foreign Key to users.id)
  - start_time (DATETIME)
  - end_time (DATETIME, Nullable)
  - duration_minutes (REAL, Nullable)
  - status (ENUM: online, offline)
```

#### **MongoDB Collections (Optional)**
```javascript
// Agent Management & Performance
agents: {
  _id: ObjectId,
  user_id: UUID,
  first_name: String,
  last_name: String,
  skills: [String],
  hourly_rate: Number,
  availability: {
    status: String, // available, busy, offline
    working_hours: {
      start: String,
      end: String
    }
  },
  performance_metrics: {
    avg_response_time: Number,
    satisfaction_score: Number,
    total_resolved_issues: Number
  }
}

// Customer Feedback System
customer_feedback: {
  _id: ObjectId,
  session_id: UUID,
  agent_id: UUID,
  rating: Number, // 1-5 stars
  feedback_type: String, // positive, negative, neutral
  comment: String,
  timestamp: Date,
  customer_satisfaction: Number
}

// System Analytics & Logs
system_logs: {
  _id: ObjectId,
  timestamp: Date,
  level: String, // info, warning, error
  component: String,
  message: String,
  user_id: UUID,
  session_id: UUID,
  metadata: Object
}
```

### **🌐 Frontend Architecture & Technologies**

#### **Component Structure**
```
Frontend/
├── Public Client Interface
│   ├── Chat Interface (Real-time)
│   ├── Message History
│   ├── Feedback System
│   └── Responsive Design
├── Agent Dashboard
│   ├── Overview Dashboard
│   ├── Active Issues Management
│   ├── Performance Metrics
│   ├── Status Toggle System
│   └── Working Hours Timer
└── Admin Dashboard
    ├── Analytics Overview
    ├── Agent Management
    ├── Performance Reports
    ├── System Monitoring
    └── User Administration
```

#### **Technology Stack**
- **HTML5**: Semantic markup with accessibility features
- **CSS3**: 
  - Grid Layout for complex dashboard arrangements
  - Flexbox for responsive component layouts
  - CSS Variables for consistent theming
  - Animations and transitions for enhanced UX
- **JavaScript (ES6+)**:
  - Modern async/await patterns
  - Event-driven architecture
  - Module-based code organization
  - Real-time data binding
- **Socket.IO Client**: WebSocket communication for live updates
- **Chart.js**: Interactive data visualization
- **Responsive Design**: Mobile-first approach with progressive enhancement

### **🤖 AI & Machine Learning Architecture**

#### **OpenAI Integration Pipeline**
```
User Input → Intent Classification → AI Processing → Response Generation → Confidence Check → Escalation Decision
     ↓              ↓                ↓              ↓                ↓              ↓
  Text Input   Rule-based      GPT-3.5-turbo   AI Response    Score < 0.7?   Human Agent
              Classification      API Call       Generation      Yes → Escalate
```

#### **Intent Recognition System**
- **Keyword-based Classification**: Predefined patterns for common queries
- **Confidence Scoring**: AI response reliability assessment
- **Escalation Triggers**: Automatic routing to human agents
- **Fallback Mechanisms**: Rule-based responses when AI fails

#### **Response Processing**
- **Context Preservation**: Maintains conversation history
- **Dynamic Escalation**: Seamless handoff to human agents
- **Response Optimization**: Tailored responses based on user context
- **Error Handling**: Graceful degradation with helpful fallbacks

### **🔐 Security Architecture**

#### **Authentication & Authorization**
```
User Request → Session Validation → Role Check → Resource Access → Audit Logging
     ↓              ↓              ↓           ↓              ↓
  Login Form   Flask-Login    UserRole     Endpoint      Database Log
              Session Mgmt    Validation   Permission    Activity Track
```

#### **Security Layers**
- **Password Security**: Bcrypt hashing with salt
- **Session Management**: Secure Flask-Login implementation
- **Role-based Access Control**: Granular permissions system
- **Input Validation**: Comprehensive sanitization and validation
- **CSRF Protection**: Built-in Flask security features
- **Rate Limiting**: API abuse prevention

### **📡 Real-time Communication Architecture**

#### **WebSocket Implementation**
```
Client ←→ Socket.IO Client ←→ Flask-SocketIO ←→ Event Handlers ←→ Database Updates
   ↓              ↓                ↓              ↓              ↓
Real-time    Connection      Message Routing   Business Logic   Data Persistence
Updates      Management      & Broadcasting     Execution        & Broadcasting
```

#### **Event Flow**
1. **Connection Establishment**: Client connects to Socket.IO server
2. **Event Broadcasting**: Real-time updates across all connected clients
3. **Message Routing**: Intelligent message distribution
4. **State Synchronization**: Consistent data across all interfaces
5. **Error Handling**: Graceful connection recovery

### **🚀 Scalability & Performance Architecture**

#### **Horizontal Scaling Considerations**
- **Stateless Design**: Session data stored in database, not memory
- **Load Balancer Ready**: Multiple Flask instances support
- **Database Optimization**: Indexed queries and connection pooling
- **Caching Strategy**: Redis integration ready for performance boost
- **Microservices Ready**: Modular architecture for service decomposition

#### **Performance Optimizations**
- **Database Indexing**: Optimized query performance
- **Connection Pooling**: Efficient database connection management
- **Async Processing**: Non-blocking operations for better responsiveness
- **Resource Management**: Efficient memory and CPU utilization
- **Monitoring & Metrics**: Real-time performance tracking

### **🔧 Deployment Architecture**

#### **Development Environment**
```
Local Development → Virtual Environment → Flask Debug Mode → Hot Reload
       ↓                ↓                ↓              ↓
   Source Code    Python Dependencies   Development    Auto-restart
   Management     Isolation            Features       on Changes
```

#### **Production Environment**
```
Load Balancer → Web Server (Gunicorn) → Flask App → Database Cluster
      ↓              ↓                    ↓           ↓
  SSL/TLS        Process Mgmt        Application   Data Storage
  Termination    & Scaling           Logic         & Backup
```

#### **Containerization Ready**
- **Docker Support**: Containerized deployment
- **Environment Variables**: Configuration management
- **Health Checks**: Application monitoring
- **Logging**: Centralized log management
- **Backup Strategies**: Data protection and recovery

### **📊 Monitoring & Observability**

#### **System Health Monitoring**
- **Application Metrics**: Response times, error rates, throughput
- **Database Performance**: Query execution times, connection status
- **External Service Health**: OpenAI API, MongoDB connectivity
- **User Experience Metrics**: Page load times, interaction success rates

#### **Logging Architecture**
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: Debug, Info, Warning, Error, Critical
- **Centralized Logging**: Central log aggregation and analysis
- **Audit Trails**: Complete user action tracking
- **Performance Monitoring**: Real-time system health indicators

## 🚀 **Quick Start Guide**

### **Prerequisites**
- Python 3.8+ (Python 3.13 recommended)
- MongoDB Atlas account (optional, system works with SQLite only)
- OpenAI API key
- Git for version control

### **1. Clone the Repository**
```bash
git clone https://github.com/AryanSahu2805/Enterprise-Chatboard.git
cd Enterprise-Chatboard
```

### **2. Set Up Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Environment Configuration**
Create a `.env` file in the root directory:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB=enterprise_chatbot
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### **5. Run the Application**
```bash
python app.py
```

The application will be available at:
- **Public Client**: http://localhost:8000
- **Super Admin**: http://localhost:8000/admin
- **Agent Interface**: http://localhost:8000/agent

## 🔑 **Default Credentials**

### **Super Admin**
- **Username**: `superadmin`
- **Password**: `admin123`

⚠️ **Change these credentials immediately after first login**

### **Agent Account**
- **Username**: `Aryan`
- **Password**: `agent123`

## 📱 **User Interface Guide**

### **For Customers (Public Interface)**
1. Visit the main page at `/`
2. Start typing your question in the chat interface
3. AI will attempt to answer automatically with real-time responses
4. If escalation is needed, you'll be seamlessly connected to a human agent
5. Provide feedback after human agent interaction (rating system)
6. View chat history and session context

### **For Super Admins**
1. Login at `/admin` with super admin credentials
2. **Analytics Dashboard**: View system-wide statistics and performance metrics
3. **Agent Management**: Create, edit, and delete agent accounts with detailed profiles
4. **Performance Reports**: Monitor agent performance, response times, and working hours
5. **System Settings**: Configure AI parameters, escalation rules, and system preferences
6. **Audit Logs**: Track all system activities, changes, and user interactions
7. **Real-time Monitoring**: Live agent status and system health indicators

### **For Agents**
1. Login at `/agent` with assigned credentials
2. **Overview Dashboard**: View assigned issues, current status, and performance metrics
3. **Active Issues**: Handle escalated customer queries with real-time chat
4. **Chat Interface**: Seamless communication with customers and other agents
5. **Performance Tracking**: Monitor your metrics, feedback, and working hours
6. **Status Management**: Toggle online/offline status with working hours tracking
7. **Knowledge Base**: Access support resources and quick action templates

## 🔧 **System Configuration**

### **AI Settings**
- **Confidence Threshold**: Minimum confidence for AI responses (configurable)
- **Escalation Keywords**: Words that trigger human escalation
- **Response Templates**: Customizable AI response patterns
- **Fallback Responses**: Graceful handling when AI is unavailable

### **System Preferences**
- **Port Configuration**: Change default port (currently 8000)
- **Debug Mode**: Enable/disable development features
- **Logging Level**: Configure system logging verbosity
- **Session Timeout**: User session duration settings

### **Security Settings**
- **HTTPS Support**: Production-ready SSL configuration
- **Password Policy**: Configurable password requirements
- **Rate Limiting**: API request limits and protection
- **Input Validation**: Comprehensive user input sanitization

## 📊 **API Endpoints Reference**

### **Public APIs**
- `POST /api/session` - Create new chat session
- `POST /api/chat` - Send chat message
- `GET /api/chat/<session_id>` - Get chat history
- `POST /api/agent/feedback` - Submit customer feedback

### **Admin APIs**
- `GET /api/admin/users` - List all users and agents
- `POST /api/admin/users` - Create new user/agent
- `GET /api/admin/agents` - List all agents with status
- `GET /api/admin/agent/<agent_id>` - Get detailed agent information
- `GET /api/admin/performance` - System performance metrics
- `GET /api/admin/audit-logs` - System activity logs

### **Agent APIs**
- `POST /api/agent/status` - Update agent online/offline status
- `GET /api/agent/status/<agent_id>` - Get current agent status
- `GET /api/agent/overview/<agent_id>` - Agent performance overview
- `GET /api/agent/stats/<agent_id>` - Detailed agent statistics
- `GET /api/agent/feedback/<agent_id>` - Customer feedback for agent

### **Analytics APIs**
- `GET /api/analytics` - System-wide analytics data
- `GET /api/analytics?date=<date>` - Date-specific analytics
- `GET /api/admin/system-status` - Real-time system health

## 🗄️ **Database Schema**

### **SQLite Tables (Primary Database)**
- **users**: User authentication, roles, and profile information
- **sessions**: Chat session management and context
- **messages**: Individual chat messages with metadata
- **escalations**: Escalation tracking and agent assignment
- **agent_sessions**: Agent login/logout and working hours tracking

### **MongoDB Collections (Optional)**
- **agents**: Agent account information and credentials
- **customer_feedback**: Customer ratings and feedback data
- **agent_performance**: Performance metrics and analytics
- **system_logs**: Comprehensive system activity logs

## 🚨 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **Port Already in Use**
```bash
# Check what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change the port in app.py
```

#### **MongoDB Connection Issues**
- Verify your MongoDB Atlas connection string
- Check network connectivity and firewall settings
- Ensure database user has proper permissions
- **Note**: System works without MongoDB using SQLite only

#### **OpenAI API Errors**
- Verify your API key is correct and active
- Check API usage limits and billing status
- Ensure internet connectivity and firewall access
- System includes fallback responses when AI is unavailable

#### **Authentication Issues**
- Clear browser cookies and cache
- Verify user credentials in the database
- Check Flask-Login configuration
- Ensure proper session management

### **Debug Mode**
Enable debug mode by setting `FLASK_DEBUG=True` in your `.env` file for detailed error messages and automatic reloading.

## 🔒 **Security Considerations**

### **Production Security**
- **HTTPS**: Use HTTPS in production for secure communication
- **API Keys**: Never commit API keys to version control
- **Password Hashing**: All passwords are hashed using bcrypt
- **Session Management**: Secure session handling with Flask-Login
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Configure API request limits for abuse prevention

### **Data Protection**
- **User Privacy**: Minimal data collection and retention policies
- **Encryption**: Sensitive data encryption at rest and in transit
- **Access Control**: Role-based access control for all system features
- **Audit Logging**: Comprehensive logging of all system activities

## 🚀 **Deployment Guide**

### **Production Deployment**
1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure reverse proxy (Nginx, Apache)
4. Set up SSL certificates for HTTPS
5. Configure MongoDB Atlas for production use
6. Set up monitoring and logging systems

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

### **Cloud Deployment**
- **Heroku**: Easy deployment with Procfile configuration
- **AWS**: EC2 with RDS and ElastiCache
- **Google Cloud**: App Engine with Cloud SQL
- **Azure**: App Service with Azure Database

## 🤝 **Contributing Guidelines**

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper testing
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request with detailed description

### **Code Standards**
- Follow PEP 8 Python style guidelines
- Include comprehensive docstrings for all functions
- Write unit tests for new features
- Update documentation for any API changes
- Ensure mobile-responsive design for UI changes

## 📄 **License & Legal**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support & Community**

### **Getting Help**
- **GitHub Issues**: Create detailed issue reports with reproduction steps
- **Documentation**: Check this README and inline code comments
- **Community**: Join discussions in GitHub Discussions
- **Email Support**: Contact the development team directly

### **Reporting Bugs**
When reporting bugs, please include:
- Operating system and Python version
- Steps to reproduce the issue
- Expected vs. actual behavior
- Error messages and stack traces
- Browser console logs (for frontend issues)

## 🔄 **Version History & Changelog**

### **v2.0.0 (Current Release)**
- ✅ **Major Bug Fixes**: Resolved online/offline button functionality
- ✅ **Real-time Data**: Replaced all mock data with live database connections
- ✅ **Enhanced Authentication**: Custom login routing for different user types
- ✅ **Agent Management**: Comprehensive agent status and working hours tracking
- ✅ **UI/UX Improvements**: Loading states, error handling, and responsive design
- ✅ **Database Schema**: Added agent sessions and working hours tracking
- ✅ **Performance Monitoring**: Real-time system health and performance metrics

### **v1.0.0 (Initial Release)**
- Basic AI chat functionality
- MongoDB integration for agent management
- Admin dashboard with basic analytics
- Real-time chat with WebSocket support
- Responsive design for mobile and desktop

## 🌟 **Feature Roadmap**

### **Upcoming Features (v2.1)**
- [ ] **Multi-language Support**: Internationalization for global deployment
- [ ] **Advanced Analytics**: Machine learning insights and predictive analytics
- [ ] **Integration APIs**: Third-party service integrations (CRM, Helpdesk)
- [ ] **Mobile App**: Native iOS and Android applications
- [ ] **Voice Chat**: Speech-to-text and text-to-speech capabilities

### **Future Enhancements (v3.0)**
- [ ] **AI Training**: Custom model training for domain-specific responses
- [ ] **Advanced Security**: Two-factor authentication and SSO integration
- [ ] **Scalability**: Microservices architecture and load balancing
- [ ] **Real-time Translation**: Multi-language chat support
- [ ] **Advanced Reporting**: Custom report builder and data export

---

## 🏆 **Acknowledgments**

- **OpenAI**: For providing the GPT API that powers our AI responses
- **Flask Community**: For the excellent web framework and ecosystem
- **Chart.js**: For beautiful and responsive data visualization
- **MongoDB**: For scalable NoSQL database solutions
- **Contributors**: All community members who have contributed to this project

---

**Built with ❤️ using Flask, MongoDB, OpenAI, and modern web technologies**

*Last updated: August 2025 - Version 2.0.0*

**⭐ Star this repository if you find it helpful!**
**🔄 Fork and contribute to make it even better!**
**🐛 Report issues to help improve the system!**
