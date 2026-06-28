import logging 
import random 
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from models import PositionedGraph, ExcalidrawPayload, AnnotationOutput, RectangleElement, TextElement, ArrowElement


logger = logging.getLogger(__name__)

llm = ChatGroq(
    model = "llama-3.3-70b-versatile",
    temperature = 0.3,
    max_tokens = 2048
)

SYSTEM_PROMPT = """ 
You are an expert software architect reviewing a system design.
Given a positioned componenet graph, your task is to:
1. Identify 2 to 3 key architectural highlights, bottlenecks, or important decision. For each, provide the exact 'id' of the target node and a concise 1-sentence note.
2. Write a comprehensive Architecture Decision Record(ADR) in Markdown format. Include sections for: Context, Decision, Consequnces, and Alternatives Considered.

Output ONLY valid JSON matching the provided schema.
"""
PROMPT_TEMPLATE = """ 
POSITIONED GRAPH (JSON):
{graph_json}
"""

def generate_annotations(graph: PositionedGraph, current_payload: ExcalidrawPayload) -> ExcalidrawPayload:
    
    logger.info("Starting Annotation Agent....")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", PROMPT_TEMPLATE)
    ])
    
    chain = prompt | llm.with_structured_output(AnnotationOutput)
    
    try:
        
        result = chain.invoke({"graph_json": graph.model_dump_json()})
        logger.info(f"Annotation Agent Generated {len(result.annotations)} notes and an ADR.")
        
        #------Deterministic Mapping: Convert Annotations to Excalidraw Elements----
        new_elements = list(current_payload.elements) 
        node_map = {n.id : n for n in graph.nodes}
        
        for note in result.annotations:
            
            #Convert the 'note' to dict for safely_accessing the fields 
            note_dict = note.model_dump() if hasattr(note, 'model_dump') else dict(note)
            
            #THE LLM can response using multiple field_names for target_note_id so check for it
            target_id = note_dict.get('target_node_id') or note_dict.get('node_id') or note_dict.get('target_id') or note_dict.get('target_node')
            note_text = note_dict.get('note_text') or note_dict.get('text') or note_dict.get('note')
            
            if not target_id or not note_text:
                logger.warning(f"Skipping annotation due to missing fields: {note_dict}")
                continue 
            
            target_node = node_map.get(target_id)
            if not target_node:
                logger.warning(f"Annotation target '{target_id}' not found in graph.")
                continue
            
            
            #Position sticky note above the target node
            note_x = target_node.x
            note_y = target_node.y - 120
            note_width = 160
            note_height = 60
            
            note_id = f"note-{target_id}"
            text_id = f"text-{note_id}"
            arrow_id = f"arrow-{note_id}"
            
            #Sticky Note Rectangle 
            new_elements.append(RectangleElement(
                id = note_id, x = note_x, y = note_y, width = note_width, height = note_height,
                strokeColor="#ca8a04", backgroundColor = "#fef9c3",
                roughness = 1, strokeStyle = "dashed",
                boundElements = [{"id": text_id, "type": "text"}, {"id": arrow_id, "type": "arrow"}],
                seed = random.randint(100000000, 999999999), versionNonce = random.randint(100000000, 999999999)
            ))
            
            #Text Inside Sticky Node
            new_elements.append(TextElement(
                id = text_id, x = note_x + 10, y = note_y + 15, width = note_width - 20, height = 30,
                text = note.note_text, originalText = note.note_text, containerId = note_id,
                strokeColor = "#713f12", fontSize = 12,
                seed = random.randint(100000000, 999999999), versionNonce=random.randint(100000000, 999999999)
            ))
            
            #Dashed Arrow pointing to the target node
            target_cx = target_node.x + 90
            target_cy = target_node.y
            note_cx = note_x + (note_width / 2)
            note_cy = note_y + note_height
            
            new_elements.append(ArrowElement(
                id=arrow_id, x=note_cx, y=note_cy,
                width=abs(target_cx - note_cx), height=abs(target_cy - note_cy),
                strokeColor="#ca8a04", backgroundColor="transparent", strokeStyle="dashed", roughness=1,
                points=[[0, 0], [target_cx - note_cx, target_cy - note_cy]],
                startBinding={"elementId": note_id, "focus": 0, "gap": 1},
                endBinding={"elementId": f"rect-{note.target_node_id}", "focus": 0, "gap": 1},
                seed=random.randint(100000000, 999999999), versionNonce=random.randint(100000000, 999999999)
            ))
            
        #Update the Payload
        current_payload.elements = new_elements
        current_payload.adr_markdown = result.adr_markdown 
        return current_payload
    
    except Exception as e:
        logger.error(f"Annotation Agent Failed: {e}")
        return current_payload #return original payload if it fails 
        