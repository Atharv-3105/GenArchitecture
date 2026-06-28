import uuid 
import time 
import logging 
from logging_config import setup_logging
import json 
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import GenerateRequest, ClarifyRequest, RefineRequest, ExportRequest

from graph.graph import app as graph_app
from auth import get_current_user
from database import init_db, check_rate_limits, increment_rate_limit


#Initialize logging at the very start of the application
setup_logging()
logger = logging.getLogger(__name__)

#Define LifeSpan context mananger for initialization of DB at Startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield 

#Intialize FastAPI app
app = FastAPI(
    title = "Architecture AI Backend",
    description = "Diagram Generation from Natural Language input",
    version = "0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status" : "healthy",
        "service" : "archigen-backend",
        "version" : "0.1.0"
    }
    
@app.post("/generate")
async def generate_diagram(request: GenerateRequest, user_id: str = Depends(get_current_user)):
    """  
        Starts the Agent pipeline for Parser,Architecture Agent. 
    """
    
    #Check rate limit
    if not await check_rate_limits(user_id, limit=5):
        raise HTTPException(status_code=429, detail="Daily limit of 5 diagrams reached.")
    
    #Increment Count
    await increment_rate_limit(user_id)
    
    session_id = str(uuid.uuid4())
    logger.info(f"--- Starting generation for user {user_id}, session {session_id} ---")
    total_start = time.time()
    
    #Define Initial State
    initial_state = {
        "user_input" : request.user_input,
        "parsed_intent": None,
        "ambiguities": [],
        "clarification_answers": {},
        "component_graph" : None,
        "positioned_graph": None,
        "excalidraw_payload": None,
        "validation_errors": [],
        "repair_attempts": 0,
        "final_output": None,
        "refinement_instruction": None
    }
    
    #Define a thread_id in the Config to track state across stream chunks
    config = {"configurable": {"thread_id": session_id}}
    
    async def event_generator():
        try:
            
            #Stream updates from Graph as each node completes
            async for chunk in graph_app.astream(initial_state, config = config, stream_mode = "updates"):
                #Chunk is like a dict {"parser": {"parsed_intent": ...}}
                node_name = list(chunk.keys())[0]
                
                #Add 50ms delay to ensure NO RACE CONDITIONS BETWEEN FRONTEND AND BACKEND
                await asyncio.sleep(0.05)
                
                #Format a SSE event
                event_data = {
                    "event": "node_complete",
                    "node": node_name,
                    "status": "done"
                }
                
                yield f"data: {json.dumps(event_data)}\n\n"
            
            #Retrieve the final stage to get the Payload
            final_state_snapshot = graph_app.get_state(config)
            final_state = final_state_snapshot.values
            
            #Check if pipeline failed due to Max-Repair Steps
            if final_state.get("validation_errors"):
                error_event = {
                    "event": "error",
                    "message": f"Pipeline failed after max repair attempts. Erros: {final_state['validation_errors']}"
                }
                yield f"data: {json.dumps(error_event)}\n\n"  
                return  
            
            #Check to ensure diagram is generated or Not
            payload = final_state.get("excalidraw_payload")
            if not payload:
                error_event = {
                    "event": "error",
                    "message": "Pipeline finished but no diagram was generated."
                } 
                yield f"data: {json.dumps(error_event)}\n\n"
                return 
            
            
            #Send the final diagram payload
            diagram_event = {
                "event": "diagram_ready",
                "payload": payload.model_dump() if hasattr(payload, "model_dump") else payload
            }
            yield f"data: {json.dumps(diagram_event)}\n\n"
            logger.info("----- LangGraph pipeline completed successfully---")
                
        except Exception as e:
            logger.exception("Pipeline failed with an unhandled exception")
            error_event = {
                "event": "error",
                "message": f"Pipeline failed: {str(e)}"
            }
            
            yield f"data: {json.dumps(error_event)}\n\n"
            
    #Return a StreamingResponse with SSE content type
    return StreamingResponse(
        event_generator(),
        media_type = "text/event-stream",
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"   #This prevents Nginx from buffering the stream
        }
    )
                
@app.post("/clarify")
async def clarify_diagram(request: ClarifyRequest):
    """ 
        Resume an interrupted Graph with user clarification answers.
    """
    
    return {
        "status": "skeleton",
        "session_id": request.session_id,
        "message": "Clarification answers received."
    }
    
@app.post("/refine")
async def refine_diagram(request: RefineRequest, user_id: str = Depends(get_current_user)):
    """  
        Runs the refinement Agent to make surgical updates to an existing diagram.
    """
    
    #Check for Rate Limit
    if not await check_rate_limits(user_id, limit = 5):
        raise HTTPException(status_code=429, detail = "Daily limit reached.")
    await increment_rate_limit(user_id)
    
    
    session_id = str(uuid.uuid4())
    logger.info(f"-------Starting Refinement Pipeline for User: {user_id}, Session: {session_id}---------")
    
    initial_state = {
        "user_input" : "",
        "parsed_intent": None,
        "ambiguities": [],
        "clarification_answers": {},
        "component_graph": None,
        "positioned_graph": None, 
        "excalidraw_payload": request.diagram_payload,
        "validation_errors": [],
        "repair_attempts": 0,
        "final_output": None,
        "refinement_instruction": request.edit_instruction
    }
    
    config = {"configurable": {"thread_id": session_id}}
    
    async def event_generator():
        try:
            async for chunk in graph_app.astream(initial_state, config = config, stream_mode = "updates"):
                node_name = list(chunk.keys())[0]
                
                await asyncio.sleep(0.05)
                yield f"data: {json.dumps({'event': 'node_complete', 'node': node_name, 'status': 'done'})}\n\n"
                
            final_state_snapshot = graph_app.get_state(config)
            final_state = final_state_snapshot.values 
            
            if final_state.get("validation_errors"):
                yield f"data: {json.dumps({'event':'error', 'message': str(final_state['validation_errors'])})}\n\n"
                return 
            
            payload = final_state.get('excalidraw_payload')
            
            if payload:
                serializable_payload = payload.model_dump() if hasattr(payload, 'model_dump') else payload
                yield f"data: {json.dumps({'event': 'diagram_ready', 'payload': serializable_payload})}\n\n"
            else:
                yield f"data: {json.dumps({'event':'error', 'message': 'Refinement Failed'})}\n\n"
                
        except Exception as e:
            logger.exception("Refinement pipeline failed with an unhandled exception")
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event_stream", headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
    
@app.post("/export")
async def export_diagram(request: ExportRequest):
    """ 
        Exports the diagram in the requested format.
    """
    
    return {
        "status": "UNIMPLEMENTED",
        "format": request.format,
        "message": "Export functionality will be  implemented  in Phase 4."
    }


