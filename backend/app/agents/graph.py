import operator
from loguru import logger
from langgraph.graph import StateGraph, START, END

from backend.app.agents.state import AgentState
from backend.app.agents.supervisor import supervisor_node
from backend.app.agents.policy_expert import policy_expert_node
from backend.app.agents.ingestion_worker import ingestion_worker_node

logger.info("Compiling the Main Agent Graph...")

# Initialize the StateGraph with our global AgentState
workflow = StateGraph(AgentState)

# Add all our nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("policy_expert", policy_expert_node)
workflow.add_node("ingestion_worker", ingestion_worker_node)

# The conversation always starts at the supervisor
workflow.add_edge(START, "supervisor")

# Conditional routing from the supervisor based on 'next_agent' state key
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next_agent"],
    {
        "policy_expert": "policy_expert",
        "ingestion_worker": "ingestion_worker",
        "FINISH": END
    }
)

# Return edges: whenever a worker finishes its sub-graph, return control to the supervisor
workflow.add_edge("policy_expert", "supervisor")
workflow.add_edge("ingestion_worker", "supervisor")

# Compile the final application
app = workflow.compile()
logger.success("Main Agent Graph compiled successfully!")
