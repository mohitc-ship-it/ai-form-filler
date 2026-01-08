# MidAmerica Phase 2 Demo: AI Form Filler

**Client:** MidAmerica  
**Phase:** 2 (Demo)  
**Current Focus:** Automated Document & Excel Form Filling (Evolved from Dashboard + Chatbot)

---

## 📖 Project Overview

This project is a **Phase 2 Demo** for **MidAmerica**. The requirements have evolved from a simple Dashboard and Chatbot interface to a specialized **AI-powered Form Filling Wizard**.

The application allows users to upload "Context Files" (source documents like PDFs, contracts, financial reports) and a "Target Form" (Excel or Word document). The system then uses an advanced **Unstructured-based Multimodal Graph RAG** pipeline to intelligently extract relevant information from the context files and populate the target form automatically.

### Key Problem Statement
Manual data entry from various unstructured source documents into structured forms (Excel/Word) is time-consuming and error-prone. The goal is to automate this process using Generative AI to understand the context and map it to the specific fields in the target forms.

---

## 🏗 Architecture & Approach

The solution follows a **Client-Server** architecture:

1.  **Frontend (The Wizard):** A modern, step-by-step React interface that guides the user through uploading files and reviewing the process.
2.  **Backend (The Brain):** A FastAPI-based server that handles file processing, RAG indexing, and document manipulation.

### The RAG Engine: Multimodal Graph RAG
We utilize a cutting-edge **Multimodal Graph RAG** approach.
-   **Unstructured Data Processing:** We use the `unstructured` library to parse complex documents, including tables and images.
-   **Graph RAG (LightRAG):** Unlike simple vector search, we use a Graph RAG approach (via `LightRAG`) to understand relationships between entities across documents, ensuring higher accuracy for complex queries.
-   **Multimodal Capabilities:** The system can process text, tables, and images to answer queries required for form filling.

### Workflow
1.  **Upload:** User uploads Context Files (Sources) and a Form File (Target) via the Frontend.
2.  **Ingestion:** Backend receives files and creates a unique session.
3.  **Indexing:** Context files are processed and indexed into the Graph RAG vector store.
4.  **Structure Extraction:** The system analyzes the Target Form to understand what fields need to be filled.
5.  **Retrieval & Generation:** For each field, the system queries the RAG engine to find the correct value.
6.  **Filling:** The extracted values are written back into the Excel or Word file.
7.  **Download:** The user downloads the completed form.

---

## 🛠 Tech Stack

### Frontend (`/ai-formfill-wizard-main`)
-   **Framework:** React (Vite)
-   **Language:** TypeScript
-   **Styling:** Tailwind CSS, Shadcn UI, Lucide React
-   **State/Data Fetching:** TanStack Query
-   **Forms:** React Hook Form + Zod

### Backend (`/backend`)
-   **Framework:** FastAPI (Python)
-   **AI/RAG:**
    -   `LightRAG` (Graph RAG implementation)
    -   `LangChain` (Orchestration)
    -   `Unstructured` (Document Parsing)
    -   `OpenAI` (LLM & Embeddings)
-   **Document Manipulation:**
    -   `openpyxl` (Excel)
    -   `python-docx` (Word)
-   **Vector Store:** ChromaDB / Local Storage

---

## 📂 File Structure & Key Files

### Root Directory
-   `ai-formfill-wizard-main/`: Frontend source code.
-   `backend/`: Backend source code.

### Backend (`/backend`)
-   **`app.py`**: The main entry point for the FastAPI server. Handles file uploads (`/api/process`) and downloads (`/api/download`).
-   **`ragAnything.py`**: The core RAG engine wrapper. Configures `LightRAG` and handles document indexing and querying.
-   **`fill.py` / `fillData.py`**: Logic for mapping extracted data to Excel/Word files.
-   **`requirements.txt`**: Python dependencies.
-   **`uploaded_files/`**: Temporary storage for user uploads (organized by session ID).
-   **`rag_storage/`**: Persistent storage for the RAG vector database.

### Frontend (`/ai-formfill-wizard-main/src`)
-   **`App.tsx`**: Main application component.
-   **`components/`**: Reusable UI components (Shadcn UI).
-   **`pages/`**: Page layouts (likely the main Wizard flow).

---

## 🚀 Getting Started

### Prerequisites
-   Node.js & npm/bun
-   Python 3.10+
-   OpenAI API Key

### Backend Setup
1.  Navigate to the backend folder:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up your environment variables (create a `.env` file or set `OPENAI_API_KEY`).
5.  Run the server:
    ```bash
    uvicorn app:app --reload
    ```

### Frontend Setup
1.  Navigate to the frontend folder:
    ```bash
    cd ai-formfill-wizard-main
    ```
2.  Install dependencies:
    ```bash
    npm install
    # or
    bun install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```

---

## ⚠️ Important Notes for Developers
-   **RAG Indexing:** The indexing process can be time-consuming for large files. Ensure the backend timeout settings are appropriate.
-   **Session Management:** Files are stored locally in `uploaded_files`. A cron job or cleanup script is recommended for production to clear old sessions.
-   **Graph RAG:** If you modify `ragAnything.py`, be aware that `LightRAG` maintains its own state on disk (`rag_storage`). You might need to clear this folder if you change embedding models or core configurations.
