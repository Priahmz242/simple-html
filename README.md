# 🚀 Boijelux v7

## Unlimited AI Agent with Full Internet Access

### Features

- 🤖 **Self-Learning** - Learns from text and experience
- 🔧 **Self-Repairing** - Detects and fixes errors automatically
- ⬆️ **Self-Upgrading** - Improves performance over time
- 🔄 **Self-Replicating** - Creates new AI agents
- 🌐 **Internet Access** - Search web, fetch URLs, chat with internet
- 💻 **Code Generation** - Generate code in multiple languages
- 📊 **Dashboard** - Beautiful dark theme dashboard
- 📱 **Mobile Responsive** - Works on all devices

### Live Demo

[https://ai.taagc.site](https://ai.taagc.site)

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | Agent status |
| `/api/tasks` | GET | List tasks |
| `/api/task` | POST | Process task |
| `/api/create_bot` | POST | Create bot |
| `/api/learn` | POST | Learn from text |
| `/api/knowledge` | GET | Knowledge base |
| `/api/search` | POST | Search web |
| `/api/fetch` | POST | Fetch URL |
| `/api/chat` | POST | Chat with internet |
| `/api/generate_code` | POST | Generate code |
| `/api/metrics` | GET | System metrics |
| `/api/version` | GET | Version info |
| `/api/docs` | GET | API Documentation |

### Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn api.index:app --reload

# Deploy to Vercel
vercel --prod
