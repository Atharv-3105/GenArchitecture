import logging 
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from graph.state import ArchitectureState
from graph.nodes import parser_node, clarification_node, architecture_node, layout_node, style_node, validator_node, repair_node, refinement_node
from models import ParsedIntent, ComponentGraph, PositionedGraph, ExcalidrawPayload

# Define serializer with custom types allowlisted for security and warning suppression
serde = JsonPlusSerializer(
    allowed_msgpack_modules=[
        (ParsedIntent.__module__, ParsedIntent.__name__),
        (ComponentGraph.__module__, ComponentGraph.__name__),
        (PositionedGraph.__module__, PositionedGraph.__name__),
        (ExcalidrawPayload.__module__, ExcalidrawPayload.__name__),
    ]
)

logger = logging.getLogger(__name__)

def route_start(state: ArchitectureState):
    """ 
        Routes to Refinement if instruction exists, else continues to Parser.
    """
    if state.get("refinement_instruction"):
        logger.info("Routing to Refinement Node.")
        return "refinement"
    
    return "parser"

def route_after_parser(state: ArchitectureState):
    """ 
        A conditional Route which the Agent will take IF AMBIGUITIES -> GO TO Clarification node. 
                                                      ELSE -> GO TO Architecture Node
    """
    
    if state.get('ambiguities'):
        logger.info("Routing to Clarification node due to ambiguities")
        return "clarification"
    
    return "architecture"

def route_after_validator(state: ArchitectureState):
    """ 
        A conditional edge: IF errors exist and we haven't maxed out repairs, loop to repair. ELSE FINISH
    """
    
    errors = state.get("validation_errors", [])
    attempts = state.get("repair_attempts", [])
    
    if errors and attempts < 3:
        logger.info(f"Routing to Repair Node. Errors: {errors}")
        return "repair"
    
    if errors and attempts >= 3:
        logger.error("Max repair attempts reached. Failing Pipeline")
        return "end"
    
    logger.info("Validation passed. Routing to END")
    return "end"

#1. Initialize the StateGraph 
workflow = StateGraph(ArchitectureState)

#2. Add Nodes in the WorkFlow
workflow.add_node("parser", parser_node)
workflow.add_node("clarification", clarification_node)
workflow.add_node("architecture", architecture_node)
workflow.add_node("refinement", refinement_node) 
workflow.add_node("layout", layout_node)
workflow.add_node("style", style_node)
workflow.add_node("validator", validator_node)
workflow.add_node("repair", repair_node)

#3. Define Edges
workflow.add_conditional_edges(
    START,
    route_start,
    {
        "refinement": "refinement",
        "parser": "parser"
    }
)

# Conditional Routing adter Parser
workflow.add_conditional_edges(
    "parser", route_after_parser,
    {
        "clarification": "clarification",
        "architecture" : "architecture"
    }
)

# Linear Flow (Clarification-> Architecture -> Layout -> Style -> Validator)
workflow.add_edge("clarification", "architecture")

workflow.add_edge("refinement","layout") 

workflow.add_edge("architecture", "layout")
workflow.add_edge("layout", "style")
workflow.add_edge("style", "validator")

# Conditional Routing After Validator
workflow.add_conditional_edges(
    "validator",route_after_validator,
    {
        "repair": "repair", 
        "end": END
    }
)

# Repair loops back to layout
workflow.add_edge("repair", "layout")

# 4. Compile the Graph 
# Add memory saver checkpoint so that get_state() can recognize the last_checkpoint
memory = MemorySaver(serde=serde)
app = workflow.compile(checkpointer=memory)




