from typing import TypedDict, Optional, List, Dict, Any 
from models import ParsedIntent, ComponentGraph, PositionedGraph, ExcalidrawPayload

class ArchitectureState(TypedDict):
    """  
        The shared state object passed between all nodes in the LangGraph pipeline
        This Acts as the Brain that every agent will read from and write to
    """
    
    user_input:        str
    parsed_intent:     Optional[ParsedIntent]
    ambiguities:       List[str]
    clarification_answers:  Dict[str, str]
    component_graph:      Optional[ComponentGraph]
    positioned_graph:     Optional[PositionedGraph]
    excalidraw_payload:   Optional[ExcalidrawPayload]
    validation_errors:    List[str]
    repair_attempts:      int 
    final_output:         Optional[Dict[str, Any]]
    refinement_instruction: Optional[str]
    
    