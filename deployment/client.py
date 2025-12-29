import asyncio
from a2a.client import ClientFactory, ClientConfig
from a2a.client.helpers import create_text_message_object
from a2a.types import TaskState, Task
import httpx

async def main():
    print("Connecting to agent server at http://localhost:8000...")
    
    try:
        # ClientFactory.connect automatically resolves the AgentCard
        # Configure timeout via httpx client
        timeout_config = httpx.Timeout(300.0, connect=60.0)
        async_client = httpx.AsyncClient(timeout=timeout_config)
        config = ClientConfig(httpx_client=async_client)
        
        # Connect to the specific agent endpoint
        client = await ClientFactory.connect("http://localhost:8000/a2a/bug_analyze_agent", client_config=config)

        
        input_text = "Please deploy the fix 'Critical Security Patch'."
        print(f"User: {input_text}\n")
        
        # Helper to create the expected Message object
        message = create_text_message_object(content=input_text)
        
        # Send message and listen to events
        # Note: If this fails with arguments error, we might need to check BaseClient.send_message_streaming signature
        async for event in client.send_message(message):
            # event is typically (Task, Update) or just Task/Message
            task = event[0] if isinstance(event, tuple) else event
            
            if isinstance(task, Task):
                print(f"[DEBUG] Task Status State: {task.status.state}")
                if task.status.state == TaskState.input_required:
                    # Check for confirmation request
                    last_msg = task.status.message
                    if last_msg and last_msg.parts:
                        for part in last_msg.parts:
                            if hasattr(part.root, 'name') and part.root.name == 'adk_request_confirmation':
                                hint = part.root.args.get('toolConfirmation', {}).get('hint', 'Confirmation needed')
                                print(f"\n[SYSTEM] CONFIRMATION REQUESTED: {hint}")
                                print("[SYSTEM] (To allow, the client would now send a FunctionResponse)")
                                break
            
            # Print raw event for debugging
            # print(f"Event: {event}")
            
    except Exception as e:
        print(f"Client Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
