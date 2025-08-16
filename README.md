# 🚀 Enterprise AI Customer Support System

A comprehensive, enterprise-grade customer support system that combines AI-powered responses with human agent escalation, featuring real-time chat, agent management, analytics, and MongoDB integration.

## ✨ Features

### 🤖 AI-Powered Chat
- **OpenAI Integration**: Uses GPT-3.5-turbo for intelligent customer responses
- **Intent Classification**: Automatically detects customer intent and routes appropriately
- **Smart Escalation**: Seamlessly escalates complex queries to human agents
- **Fallback System**: Rule-based responses when AI is unavailable

### 👥 Human Agent System
- **Agent Management**: Super Admin can create, assign, and manage agent accounts
- **Availability Control**: Agents can mark themselves as online/offline and available/unavailable
- **Hours Tracking**: Automatic tracking of agent working hours for payment purposes
- **Real-time Chat**: Live chat interface for agents to handle escalated issues

### 🔐 Authentication & Roles
- **Super Admin**: Full system control, agent management, analytics access
- **Agent Accounts**: Individual login credentials with role-based permissions
- **Secure Authentication**: Flask-Login with bcrypt password hashing

### 📊 Analytics & Monitoring
- **Real-time Dashboard**: Live statistics and performance metrics
- **Customer Feedback**: Rating system for human agent interactions
- **Performance Reports**: Response times, resolution rates, and agent performance
- **Audit Logs**: Comprehensive system activity tracking

### 🌐 Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Desktop Compatible**: Full-featured interface for larger screens
- **Real-time Updates**: WebSocket-based communication for instant updates

## 🏗️ Architecture

### Backend
- **Flask**: Python web framework
- **Flask-SocketIO**: Real-time bidirectional communication
- **Flask-Login**: User session management
- **Flask-Bcrypt**: Secure password hashing
- **PyMongo**: MongoDB integration

### Database
- **MongoDB Atlas**: Cloud-hosted NoSQL database
- **SQLite**: Local database for chat sessions and messages
- **Hybrid Approach**: Combines MongoDB for agent management with SQLite for chat data

### Frontend
- **HTML5/CSS3**: Modern, responsive design
- **JavaScript**: Interactive client-side functionality
- **Socket.IO Client**: Real-time communication
- **Chart.js**: Data visualization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- OpenAI API key

### 1. Clone the Repository
```bash
git clone https://github.com/AryanSahu2805/Enterprise-Chatboard.git
cd Enterprise-Chatboard
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
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

### 5. Run the Application
```bash
python app.py
```

The application will be available at:
- **Public Client**: http://localhost:8000
- **Super Admin**: http://localhost:8000/admin
- **Agent Interface**: http://localhost:8000/agent

## 🔑 Default Credentials

### Super Admin
- **Username**: `superadmin`
- **Password**: `admin123`

*⚠️ Change these credentials immediately after first login*

## 📱 Usage

### For Customers (Public Interface)
1. Visit the main page at `/`
2. Start typing your question
3. AI will attempt to answer automatically
4. If escalation is needed, you'll be connected to a human agent
5. Provide feedback after human agent interaction

### For Super Admins
1. Login at `/admin` with super admin credentials
2. **Analytics Dashboard**: View system-wide statistics and performance
3. **User Management**: Create, edit, and delete agent accounts
4. **Performance Reports**: Monitor agent performance and response times
5. **System Settings**: Configure AI parameters, escalation rules, and system preferences
6. **Audit Logs**: Track all system activities and changes

### For Agents
1. Login at `/agent` with assigned credentials
2. **Overview**: View assigned issues and current status
3. **Active Issues**: Handle escalated customer queries
4. **Chat Interface**: Real-time communication with customers
5. **Performance**: Track your metrics and feedback
6. **Knowledge Base**: Access support resources and quick actions

## 🔧 Configuration

### AI Settings
- **Confidence Threshold**: Minimum confidence for AI responses
- **Escalation Keywords**: Words that trigger human escalation
- **Response Templates**: Customizable AI response patterns

### System Preferences
- **Port Configuration**: Change default port (currently 8000)
- **Debug Mode**: Enable/disable development features
- **Logging Level**: Configure system logging verbosity

### Security Settings
- **Session Timeout**: Configure user session duration
- **Password Policy**: Set minimum password requirements
- **Rate Limiting**: Configure API request limits

## 📊 API Endpoints

### Public APIs
- `POST /api/session` - Create new chat session
- `POST /api/chat` - Send chat message
- `GET /api/chat/<session_id>` - Get chat history

### Admin APIs
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create new user
- `GET /api/admin/agents` - List all agents
- `GET /api/admin/agent/<agent_id>` - Get agent details

### Agent APIs
- `POST /api/agent/status` - Update agent status
- `POST /api/agent/availability` - Update availability
- `GET /api/agent/hours/<agent_id>` - Get working hours
- `POST /api/agent/feedback` - Submit customer feedback

## 🗄️ Database Schema

### MongoDB Collections
- **agents**: Agent account information and credentials
- **agent_sessions**: Agent login/logout sessions
- **customer_feedback**: Customer ratings and feedback
- **agent_performance**: Performance metrics and analytics

### SQLite Tables
- **users**: User authentication and role information
- **sessions**: Chat session management
- **messages**: Individual chat messages
- **escalations**: Escalation tracking and assignment

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change the port in app.py
```

#### MongoDB Connection Issues
- Verify your MongoDB Atlas connection string
- Check network connectivity and firewall settings
- Ensure database user has proper permissions

#### OpenAI API Errors
- Verify your API key is correct
- Check API usage limits and billing
- Ensure internet connectivity

### Debug Mode
Enable debug mode by setting `FLASK_DEBUG=True` in your `.env` file for detailed error messages and automatic reloading.

## 🔒 Security Considerations

- **HTTPS**: Use HTTPS in production for secure communication
- **API Keys**: Never commit API keys to version control
- **Password Hashing**: All passwords are hashed using bcrypt
- **Session Management**: Secure session handling with Flask-Login
- **Input Validation**: All user inputs are validated and sanitized

## 🚀 Deployment

### Production Deployment
1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure reverse proxy (Nginx, Apache)
4. Set up SSL certificates
5. Configure MongoDB Atlas for production use

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Contact the development team
- Check the documentation and troubleshooting sections

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with AI chat and human escalation
- MongoDB integration for agent management
- Comprehensive admin dashboard
- Real-time chat functionality
- Responsive design for mobile and desktop

---

**Built with ❤️ using Flask, MongoDB, and OpenAI**

*Last updated: August 2025*
