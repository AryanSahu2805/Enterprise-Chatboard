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

## 🏗️ **Architecture & Technology Stack**

### **Backend Framework**
- **Flask**: Python web framework with modular architecture
- **Flask-SocketIO**: Real-time bidirectional communication
- **Flask-Login**: User session management and authentication
- **Flask-Bcrypt**: Secure password hashing and verification
- **Flask-CORS**: Cross-origin resource sharing support

### **Database Architecture**
- **SQLite**: Primary database for chat sessions, messages, users, and escalations
- **MongoDB Atlas**: Cloud-hosted NoSQL database for agent management (optional)
- **Hybrid Approach**: Combines SQLite reliability with MongoDB scalability
- **Real-time Updates**: Live data synchronization across all interfaces

### **Frontend Technologies**
- **HTML5/CSS3**: Modern, responsive design with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Interactive client-side functionality
- **Socket.IO Client**: Real-time communication with backend
- **Chart.js**: Data visualization and analytics charts
- **Responsive Design**: Mobile-first approach with progressive enhancement

### **AI & Machine Learning**
- **OpenAI GPT-3.5-turbo**: Natural language processing and response generation
- **Intent Recognition**: Rule-based customer intent classification
- **Confidence Scoring**: AI response confidence assessment for escalation decisions
- **Fallback Mechanisms**: Graceful degradation when AI services are unavailable

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
