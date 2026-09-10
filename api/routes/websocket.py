"""Real-time WebSocket endpoint for streaming job progress events."""
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.jobs.manager import job_manager

router = APIRouter(tags=["Real-Time WebSockets"])


@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    """
    Stream live frame-by-frame progress updates directly to clients via WebSocket.
    Automatically closes when job completes, fails, or is cancelled.
    """
    await websocket.accept()
    q = job_manager.subscribe(job_id)

    try:
        while True:
            # Wait for next event update from JobManager worker thread
            data = await q.get()
            await websocket.send_json(data)
            
            # If terminal state reached, send final message and break
            if data.get("status") in ("completed", "failed", "cancelled"):
                # Give client time to receive final frame
                await asyncio.sleep(0.1)
                break

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        job_manager.unsubscribe(job_id, q)
        try:
            await websocket.close()
        except Exception:
            pass
