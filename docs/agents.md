# Agent Workflow (LangGraph)

The backend utilizes **LangGraph** to build a multi-agent system. This allows complex tasks to be broken down and routed to specialized sub-agents. The graph definition lives in `backend/app/agents/graph.py`.

## The StateGraph
The core of the system is the `StateGraph` built around a global `AgentState`. The state contains the conversation history (`messages`) and a routing key (`next_agent`). 
The graph utilizes a `PostgresSaver` to persist memory across interactions automatically.

## 1. Supervisor Node
- **Location:** `backend/app/agents/supervisor.py`
- **Role:** Acts as the traffic controller. It evaluates the current conversation state and decides whether the workflow is finished, or if a specific worker agent needs to be invoked.
- **Logic:** It relies on a structured LLM output to pick the next step: `FINISH`, `policy_expert`, or `ingestion_worker`.

## 2. Policy Expert Node
- **Location:** `backend/app/agents/policy_expert.py`
- **Role:** Answers questions based on the enterprise policies.
- **Logic:** It acts as a Retrieval-Augmented Generation (RAG) agent. If the user asks a policy question, this node uses vector similarity search against the `pgvector` database to find relevant document chunks and synthesizes an accurate answer. Once done, it returns control to the Supervisor.

## 3. Ingestion Worker Node
- **Location:** `backend/app/agents/ingestion_worker.py`
- **Role:** Processes new policy documents.
- **Logic:** When the user indicates they have uploaded a document and want it processed, the supervisor routes to this node. The Ingestion Worker calls the `document_parser.py` service, which extracts text from PDFs in `data/input`, splits it into chunks, generates embeddings, and inserts them into the database. Once done, it reports success back to the user and returns control to the Supervisor.
