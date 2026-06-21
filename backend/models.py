from pydantic import BaseModel, Field
from typing import Dict,Any, Optional, Literal, List, Union

class GenerateRequest(BaseModel):
    """  
        Payload schema for initial diagram generation request
    """
    user_input: str = Field(
        ...,
        min_length = 10,
        max_length = 2000,
        description = "Plain english description of the software system to architect."
    )
    
class ClarifyRequest(BaseModel):
    """  
        Payload schema for answering follow-up  questions from the Clarification Agent.
    """
    
    session_id: str = Field(..., description = "The session ID returned in the clarification_needed event.")
    answers:    Dict[str,str] = Field(..., description = "Key-Value pairs of question IDs and user answers")
   
class RefineRequest(BaseModel):
    """ 
        Payload schema for making edits to an existing diagram.
    """ 
    
    diagram_payload: Dict[str, Any] = Field(..., description = "The current Excalidraw JSON payload")
    edit_instruction: str = Field(..., min_length=1, description = "Plain English instruction on how to modify the  diagram")
    
class ExportRequest(BaseModel):
    """  
        Payload schema for exporting the diagram to different formats.
    """
    
    diagram_payload: Dict[str, Any]
    format:   str = Field(..., pattern = "^(excalidraw|png|svg|mermaid|markdown)$")
    
    
#---------Agent Pipeline Models--------------
class Component(BaseModel):
    name: str = Field(..., description = "The name of the component( e.g, 'User Service', 'Redis Cache')")
    type: str = Field(..., description = "The logical type(ex: 'frontend', 'backend', 'api')")
    tech_hint: Optional[str] = Field(None, description = "Specific technology mentioned")
    
class Relationship(BaseModel):
    source: str = Field(..., description = "The ID or exact name of the source component")
    target: str = Field(..., description = "The ID or exact name of the target component")
    label: Optional[str] = Field(None, description = "The nature of the connection")
    
class ParsedIntent(BaseModel):
    system_type: Literal["microservices", "monolith", "event-driven", "serverless", "unknown"] = Field(..., description = "The high-level architectural pattern")
    components: List[Component] = Field(..., description = "List of distinct system components")
    relationships: List[Relationship] = Field(..., description= "List of connections between systems.")
    ambiguities: List[str] = Field(default_factory = list, description = "List of clarifying questions to ask the user if the input is vague")
    confidence: float = Field(..., ge=0.0, le=1.0, description = "Confidence score of the parsed intent")
    
#-----------Architecture  Agent Models---------------
class Node(BaseModel):
    id: str = Field(..., description="Unique ID for the node, derived from name (e.g, 'api-gateway')")
    name: str = Field(..., description = "The display name of the component")
    type: str = Field(..., description = "The LOGICAL component type(e.g. 'frontend-app', 'api-gateway', 'web-server', 'database', 'cache', 'message-queue').Do NOT use the technology name.")
    layer: Literal["frontend", "api", "service", "data", "infra"] = Field(..., description = "The architectural layer this component belong to")
    description: str = Field(..., description="A brief 1-sentence description of the component's role")
    
class Edge(BaseModel):
    source: str = Field(..., description = "The ID of the source node")
    target: str = Field(..., description = "The ID of the target node")
    label: str = Field(..., description = "The action or protocol (e.g., 'REST API', 'Queris')")
    protocol: str = Field(..., description = "The communicatoin protocol (e.g.,  'HTTP', 'TCP', 'gRPC')")
    
class ComponentGraph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    pattern: str = Field(..., description = "The identified architectural pattern (e.g., '3-tier microservices')")
    warnings: List[str] = Field(default_factory=list, description = "Architectural warnings or suggestions")
    
#--------------Layout Agent Models-------------
class PositionedNode(Node):
    x: float = Field(..., description = "X coordinate on the canvas")
    y: float = Field(..., description = "Y coordinate on the canvas")
    
class PositionedGraph(BaseModel):
    nodes: List[PositionedNode]
    edges: List[Edge]
    pattern: str
    warnings: List[str] = Field(default_factory=list)
    
#--------------Stlye Agent Models---------------
class ExcalidrawElement(BaseModel):
    id:     str
    type:   str
    x:      float
    y:      float
    width:  float
    height: float
    angle:  float = 0
    strokeColor:  str 
    backgroundColor:  str
    fillStyle:    str = "solid"
    strokeWidth:   int = 2
    strokeStyle:   str = "solid"
    roughness:     int = 0
    opacity:       int = 100
    seed:          int = 123456789
    version:       int = 1
    versionNonce:  int = 987654321
    isDeleted:     bool = False 
    boundElements: Optional[List[Dict[str,str]]] = None 
    updated:       int = 1690000000000
    link:          Optional[str] = None 
    locked:        bool = False 
    
class RectangleElement(ExcalidrawElement):
    type:       Literal["rectangle"] = "rectangle"
    roundness:  Dict[str, int] = {"type": 3}
    
class TextElement(ExcalidrawElement):
    type:       Literal["text"] = "text"
    text:       str 
    fontSize:   int = 16
    fontFamily: int = 1
    textAlign:  str = "center"
    verticalAlign: str = "middle"
    containerId:   Optional[str] = None 
    originalText:  str 
    autoResize:  bool = True 
    lineHeight:  float = 1.25
    roundness:  Optional[Any] = None 
    strokeColor:  str = "#1e1e1e"
    backgroundColor: str = "transparent"
    
class ArrowElement(ExcalidrawElement):
    type:       Literal["arrow"] = "arrow"
    points:     List[List[float]]
    startBinding:  Optional[Dict[str,Any]] = None 
    endBinding:    Optional[Dict[str,Any]] = None 
    startArrowhead:  Optional[str] = None 
    endArrowhead:    str = "arrow"
    roundness:      Dict[str, int] = {"type": 2}
    lastCommittedPoint:  Optional[Any] = None
    
class ExcalidrawPayload(BaseModel):
    elements:   List[Union[RectangleElement, TextElement,ArrowElement]]
    appState:   Dict[str, Any] = {"viewBackgroundColor": "#09090b", "theme":"dark"}

    