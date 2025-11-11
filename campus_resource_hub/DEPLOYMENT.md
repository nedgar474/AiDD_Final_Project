# Deployment Guide - Resource Concierge

## Deployment Architecture Options

The Resource Concierge uses **Ollama with Llama 3.1 8B** as the LLM backend. The deployment requirements depend on your deployment model:

---

## Option 1: Server-Side Deployment (Recommended for Web Applications)

**Who needs Ollama:** Only the server/host machine

**How it works:**
- Ollama runs on the server where Flask is deployed
- Users access the website through their browser
- All LLM processing happens on the server
- Users don't need to install anything locally

**Deployment Steps:**
1. **On the server:**
   ```bash
   # Install Ollama
   # Windows: Download from https://ollama.com/download
   # Linux: curl -fsSL https://ollama.com/install.sh | sh
   # macOS: brew install ollama
   
   # Download the model
   ollama pull llama3.1:8b
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Run Flask app
   python run.py
   # Or use a production server like gunicorn
   ```

2. **Users:**
   - Just visit the website URL in their browser
   - No installation required

**Pros:**
- ✅ Users don't need to install anything
- ✅ Centralized model management
- ✅ Consistent experience for all users
- ✅ Easier to update/maintain

**Cons:**
- ❌ Server needs sufficient RAM (8GB+ recommended for Llama 3.1 8B)
- ❌ All users share server resources
- ❌ May need to scale server for high traffic

**Best for:** Production web applications, shared campus resources

---

## Option 2: Local/Desktop Deployment

**Who needs Ollama:** Each user's computer

**How it works:**
- Each user runs Flask locally on their machine
- Each user installs Ollama locally
- Each user downloads the model locally
- All processing happens on user's machine

**Deployment Steps:**
1. **For each user:**
   ```bash
   # Install Ollama (see OLLAMA_SETUP.md)
   # Download model
   ollama pull llama3.1:8b
   
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Run Flask app
   python run.py
   ```

**Pros:**
- ✅ No server costs
- ✅ Privacy (data stays on user's machine)
- ✅ No server resource sharing

**Cons:**
- ❌ Each user must install Ollama (~500MB) and model (~4.7GB)
- ❌ Each user needs sufficient RAM (8GB+)
- ❌ More complex distribution/setup

**Best for:** Personal use, development, offline applications

---

## Option 3: Docker Deployment (Recommended for Production)

**Who needs Ollama:** The Docker container/server

**How it works:**
- Ollama runs inside a Docker container
- Model is included in the container or mounted as volume
- Users access via browser

**Dockerfile Example:**
```dockerfile
FROM python:3.11-slim

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Download model (or do this at runtime)
RUN ollama pull llama3.1:8b

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "run.py"]
```

**docker-compose.yml Example:**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
      - ~/.ollama:/root/.ollama  # Persist models
    environment:
      - FLASK_ENV=production
```

**Pros:**
- ✅ Consistent deployment across environments
- ✅ Easy to scale with Docker Compose/Kubernetes
- ✅ Isolated dependencies

**Cons:**
- ❌ Larger container size (~5GB+ with model)
- ❌ Requires Docker knowledge

**Best for:** Production deployments, cloud hosting (AWS, Azure, GCP)

---

## Option 4: Cloud/API-Based LLM (Alternative)

**Who needs Ollama:** No one (uses cloud API instead)

**How it works:**
- Replace Ollama with cloud LLM API (OpenAI, Anthropic, etc.)
- Users access website, API calls go to cloud service
- Requires API keys and may have costs

**Implementation:**
- Modify `llm_client.py` to use API instead of Ollama
- Add API key configuration
- Handle rate limits and costs

**Pros:**
- ✅ No local installation needed
- ✅ No server RAM requirements
- ✅ Always up-to-date models
- ✅ Scalable

**Cons:**
- ❌ Requires API keys
- ❌ May have usage costs
- ❌ Data sent to third-party service
- ❌ Requires internet connection

**Best for:** Production with budget for API costs, when privacy isn't critical

---

## Recommended Deployment Strategy

### For Development/Testing:
- **Option 2 (Local)**: Each developer installs Ollama locally

### For Production Web Application:
- **Option 1 (Server-Side)**: Install Ollama on production server
- **Option 3 (Docker)**: Use Docker for easier deployment

### For Distribution to End Users:
- **Option 1 (Server-Side)**: Host on a server, users access via browser
- **Option 2 (Local)**: Provide setup instructions (OLLAMA_SETUP.md)

---

## System Requirements

### Server/Host Machine:
- **RAM**: 8GB minimum, 16GB+ recommended for Llama 3.1 8B
- **Storage**: 5GB+ for Ollama and model
- **CPU**: Multi-core recommended for better performance
- **OS**: Windows, macOS, or Linux

### User's Browser:
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- No special requirements

---

## Making Ollama Optional

If you want to make the concierge feature optional (graceful degradation):

1. **Check if Ollama is available:**
   ```python
   # In concierge_controller.py
   @concierge_bp.route('/health', methods=['GET'])
   def health():
       from .llm_client import LLMClient
       llm_client = LLMClient()
       is_available = llm_client.is_available()
       return jsonify({'available': is_available})
   ```

2. **Hide chatbot if unavailable:**
   ```javascript
   // In base.html
   fetch('/concierge/health')
       .then(response => response.json())
       .then(data => {
           if (!data.available) {
               document.getElementById('concierge-toggle').style.display = 'none';
           }
       });
   ```

3. **Show message if unavailable:**
   - Display a message: "AI Concierge requires Ollama to be installed on the server"

---

## FAQ

**Q: Can users use the website without Ollama?**
A: Yes, all other features work. Only the Resource Concierge chatbot requires Ollama.

**Q: Can I use a different model?**
A: Yes, change the model name in `llm_client.py`. Smaller models (like `llama3.1:3b`) require less RAM.

**Q: Can I use Ollama on a different server?**
A: Yes, modify `llm_client.py` to connect to a remote Ollama instance:
   ```python
   import ollama
   client = ollama.Client(host='http://remote-server:11434')
   ```

**Q: What if the server doesn't have enough RAM?**
A: Use a smaller model (`llama3.1:3b`) or use a cloud API instead.

---

## Summary

- **For web applications**: Only the server needs Ollama installed
- **For local applications**: Each user needs Ollama installed
- **Users accessing via browser**: No installation needed (server-side deployment)
- **The concierge is optional**: Website works without it, just hides the chatbot button

