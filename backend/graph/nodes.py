import logging 
from graph.state import ArchitectureState
from agents.parser import parse_user_input
from agents.architecture import enrich_architecture
from agents.layout import calculate_layout
from agents.style import apply_styles
from agents.validator import validate_diagram
from agents.repair import repair_graph
from agents.refinement import refine_graph


logger = logging.getLogger(__name__)

def parser_node(state: ArchitectureState) -> dict:
    """ 
        Node 1: Extracts structured intent from Raw Input Text.
    """
    
    logger.info(f"------Entering Parser Node--------")
    intent = parse_user_input(state["user_input"])
    return {
        "parsed_intent": intent, 
        "ambiguities": intent.ambiguities
    }
    

def clarification_node(state: ArchitectureState) -> dict:
    """  
        Node 2: Handle Ambiguities.
    """
    logger.info("------Entering Clarification Node-------")
    logger.warning(f"Ambiguities Detected: {state["ambiguities"]}. Pass for now")
    
    
def architecture_node(state: ArchitectureState) -> dict:
    """ 
        Node 3: Enriches the components with layers and protocols.
    """
    logger.info("------Entering Architecture Node-------")
    graph = enrich_architecture(state["parsed_intent"])
    return {
        "component_graph" : graph
    }
    
def layout_node(state: ArchitectureState) -> dict:
    """ 
        Node 4: Calculates X/Y coordinates using GraphViz
    """
    logger.info("------Entering Layout Node---------")
    positioned = calculate_layout(state["component_graph"])
    return {
        "positioned_graph": positioned
    }
    
def style_node(state: ArchitectureState) -> dict:
    """ 
        Node 5: Maps positioned graph to Excalidraw JSON.
    """
    logger.info(f"------Entering Stlye Node--------")
    payload = apply_styles(state["positioned_graph"])
    return {
        "excalidraw_payload": payload
    }
    
def validator_node(state: ArchitectureState) -> dict:
    """ 
        Node 6: Checks for Structural Errors.
    """
    logger.info("-------Entering Validator Node-------")
    errors = validate_diagram(state["excalidraw_payload"])
    return {
        "validation_errors": errors
    }
    

def repair_node(state: ArchitectureState) -> dict:
    """ 
        Node 7: Fixes the ComponentGraph based on validator errors.
    """
    
    logger.info(f"--------Entering Repair Node (Attempt {state['repair_attempts'] + 1})-----")
    fixed_graph = repair_graph(
        state["parsed_intent"],
        state["component_graph"],
        state["validation_errors"]
    )
    
    return {
        "component_graph": fixed_graph,
        "repair_attempts": state["repair_attempts"] + 1,
        "validation_errors": [] #Clear errors so the loop can re-evaluate
    }
    
def refinement_node(state: ArchitectureState) -> dict:
    """ 
        Node 8: Updates the ComponentGraph based on User instructions
    """
    
    logger.info("----Entering Refinement Node------")
    
    current_diagram = state['excalidraw_payload']
    instruction = state['refinement_instruction']
    
    if not current_diagram or not instruction:
        raise ValueError("Refinement Agent requires an Existing Diagram and an Instruction")
    
    refined_graph = refine_graph(current_diagram, instruction)
    
    return {
        "component_graph": refined_graph.model_dump(),
        "refinement_instruction": None
    }