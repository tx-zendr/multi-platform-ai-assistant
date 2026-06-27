# 🧠 AI Multi-Platform Assistant

A full-stack AI-powered assistant integrated with **Discord** and **Telegram**, powered by **Google Gemini**.  
The system combines persistent memory, multimodal input support, and Retrieval-Augmented Generation (RAG) using vector search.



## 🚀 Features

- 🤖 Discord & Telegram bot integration  
- 🧠 Google Gemini LLM for intelligent responses  
- 📄 Multimodal support (text, image, audio, PDF)  
- 💾 Persistent memory using MySQL  
- 🔍 RAG system using ChromaDB + embeddings  
- 📚 Document-based question answering  
- ⚙️ Modular backend architecture  



## 🏗️ Architecture


- User (Discord / Telegram)
-        │
-          ▼
-   Bot Layer (Python)
-          │
-          ▼
- Backend Orchestrator (Gemini Service)
-          │
-   ┌──────┴─────────┐
-   ▼                ▼
- MySQL           ChromaDB
- (Chat Memory)   (Vector Search)
-   │                │
-   └──────┬─────────┘
-          ▼
-   Google Gemini LLM
-          │
-          ▼
-     AI Response

     
## ⚙️ Tech Stack
- Python
- Google Gemini API
- ChromaDB (Vector Database)
- MySQL
- Discord API (discord.py)
- Telegram Bot API
- LangChain (optional integration)


## 🧠 System Workflow
- User sends message via Discord/Telegram
- Bot forwards request to backend
- System retrieves chat history (MySQL)
- If needed, performs semantic search (ChromaDB)
- Relevant context is added to prompt
- Gemini generates response
- Response is returned & stored in memory




## 📄 RAG Pipeline
Document → Chunking → Embedding → ChromaDB Storage
User Query → Embedding → Similarity Search → Context → Gemini

##📦 Installation
- git clone https://github.com/tx-zendr/multi-platform-ai-assistant
- cd ai-assistant
- pip install -r requirements.txt




## 🔑 Environment Variables

- Create a .env file:

- GEMINI_API_KEY=your_api_key
- DISCORD_TOKEN=your_token
- TELEGRAM_TOKEN=your_token
- MYSQL_HOST=localhost
- MYSQL_USER=root
- MYSQL_PASSWORD=your_password
- MYSQL_DB=bot
- ▶️ Run Project
- python main.py



## 📌 Project Structure
- bots/
- backend/
- database/
- vector_db/
- documents/
- main.py



## 🚀 Future Improvements
- Improved RAG chunking strategy
- Deployment on cloud (AWS / GCP)
- Advanced memory summarization
- Rate limiting & caching
- Web dashboard for monitoring

## 📜 License

This project is open-source and available for learning and educational purposes.
