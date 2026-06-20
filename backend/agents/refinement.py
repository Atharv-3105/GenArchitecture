import logging 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models import ComponentGraph
from typing import Dict, Any 

logger = logging.getLogger(__name__)

llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature = 0.2,
    max_tokens = 2048
)

SYSTEM_PROMPT = """ 
You are an expert software architect refining an architecture diagram.

You will receive:
1. The current diagram in Excalidraw JSON format.
   - 'rectangle' elements are COMPONENTS (Nodes). Their 'id' is the unique identifier.
   - 'arrow' elements are CONNECTIONS (Edges). 'startBinding.elementId' is the source, 'endBinding.elementId' is the target.
2. A user instruction to modify the diagram.

TASK:
1. Analyze the current nodes and edges.
2. Apply the instruction (e.g., add a node, remove a node, change a connection).
3. Return the UPDATED ComponentGraph JSON.
   - Ensure all Node IDs are unique and consistent.
   - If adding a node, assign a logical 'layer' (frontend, api, service, data, infra).
   - If removing a node, remove it from 'nodes' and delete all associated 'edges'.
   - Ensure 'source' and 'target' in edges match existing Node IDs.

OUTPUT: ONLY valid ComponentGraph JSON.
"""

PROMPT_TEMPLATE = """ 
CURRENT DIAGRAM JSON:
{diagram_json}

INSTRUCTION:
{instruction}
"""


def refine_graph(diagram_json: Dict[str, Any], instruction: str) -> ComponentGraph:
    
    logger.info(f"Starting Refinement Agent with instruction: {instruction}")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", PROMPT_TEMPLATE)
    ])
    
    chain = prompt | llm.with_structured_output(ComponentGraph)
    
    try:
        
        result = chain.invoke({
            "diagram_json": diagram_json,
            "instruction": instruction
        })
        
        logger.info("Refinement Agent successfully updated the Graph.")
        return result 
    
    except Exception as e:
        logger.error(f"Refinement Agent failed: {e}")
        raise e
    
    