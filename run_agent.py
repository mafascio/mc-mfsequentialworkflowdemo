# Before running the sample:
#    pip install --pre azure-ai-projects>=2.0.0b1
#    pip install azure-identity

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ResponseStreamEventType


project_client = AIProjectClient(
    endpoint="https://lab511-ai-services-zs5h7nhajqqmo.services.ai.azure.com/api/projects/lab511-prj",
    credential=DefaultAzureCredential(),
)

with project_client:

    workflow = {
        "name": "SequentialWorkflowDemo20251217",
        "version": "1",
    }
    
    openai_client = project_client.get_openai_client()

    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    stream = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": workflow["name"], "type": "agent_reference"}},
        input="create a social media campaign for the contoso electronics noise canceling wireless earbuds",
        stream=True,
        metadata={"x-ms-debug-mode-enabled": "1"},
    )

    # Variable to store the final output
    final_output = None

    for event in stream:
        if event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
            print("\t", event.text)
            final_output = event.text  # Capture the final output
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and event.item.type == "workflow_action":
            print(f"********************************\nActor - '{event.item.action_id}' :")
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED and event.item.type == "workflow_action":
            print(f"Workflow Item '{event.item.action_id}' is '{event.item.status}' - (previous item was : '{event.item.previous_action_id}')")
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE and event.item.type == "workflow_action":
            print(f"Workflow Item '{event.item.action_id}' is '{event.item.status}' - (previous item was: '{event.item.previous_action_id}')")
        elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA:
            print(event.delta)
        else:
            print(f"Unknown event: {event}")

    # Save the final output to markdown file
    if final_output:
        output_path = os.path.join(os.path.dirname(__file__), "social-media-campaign-test.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_output)
        print(f"Final output saved to: {output_path}")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")
