⚖️ FastAPI Full-Stack Legal RAG Bot + ML/DL Models

This project is a production-ready FastAPI backend deployed on Google Cloud Run, integrating:

Legal RAG Bot – AI-powered legal assistant using LLMs, LangChain, LangGraph, Pinecone, and Redis.

Machine Learning Model – Heart disease prediction using XGBoost (92% accuracy).

Deep Learning Model – Image classification (Intel dataset) using EfficientNet + PyTorch (95% training accuracy, 93% testing accuracy).

Deployed with PostgreSQL, JWT authentication, secure password handling, cloud storage for ML/DL models, and scalable architecture.

🔑 Features
🔹 Core FastAPI Backend

JWT-based authentication: login, register, password reset

PostgreSQL database for user & session management

Cloud storage for ML & DL models

Deployed on Google Cloud Run

Error handling and production-grade scalability

⚖️ Legal RAG Bot (AI Assistant)

A multi-agent legal assistant designed with LangChain + LangGraph for dynamic query resolution.

Flow:

User submits a query

Master LLM decides the path:

Direct Answer → Returns structured answer (graph ends)

Web Search Tool → Searches web docs → 2-round relevancy check → fallback to AI-generated summary with disclaimer

RAG Tool (Internal Docs) → Fetches from Pinecone vector DB (70 AI-generated docs) → Multi-round relevancy checks → fallback to web search → final AI response with disclaimer

LLMs used:

Groq LLM → lightweight tasks

OpenAI LLM → master decision-making

Redis → stores conversation history

✅ Context-aware
✅ Handles missing information gracefully
✅ Proper fallbacks with disclaimers
✅ Optimized for real-world legal assistance

❤️ Machine Learning Model – Heart Disease Prediction

Algorithm: XGBoost

Accuracy: 92%

Preprocessing included

Model saved as joblib and stored in cloud storage

Integrated into FastAPI API endpoints

🖼️ Deep Learning Model – Intel Image Classification

Dataset: Intel Image Classification Dataset

Pretrained Model: EfficientNet (fine-tuned)

Accuracy: 95% (train), 93% (test)

Framework: PyTorch

Model exported to ONNX format and stored in cloud storage

FastAPI endpoints for inference

🛠️ Tech Stack

Backend: FastAPI

Database: PostgreSQL

Authentication: JWT

Deployment: Google Cloud Run, Docker, CI/CD pipline

Storage: Google Cloud Storage

Vector DB: Pinecone

Memory Store: Redis

AI Orchestration: LangChain + LangGraph

ML Model: XGBoost (joblib)

DL Model: PyTorch + EfficientNet (ONNX)

📌 Project Status

✅ Stable and deployed
🛠️ Continuously improving with better orchestration, retrieval accuracy, and model optimizations.



🌐 Live App: https://legalbot-887418779704.us-central1.run.app


⚡ FastAPI + LLMs + ML/DL integration → building scalable, intelligent real-world AI systems.
