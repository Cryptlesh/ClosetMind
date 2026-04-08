from google.adk.tools import AgentTool
from pydantic import BaseModel, Field
import uuid

class NotesInput(BaseModel):
    user_id: str = Field(description="The user ID requesting the document")
    packing_items: list[str] = Field(description="A list of packing items to add to the notes document")

class NotesDocsTool(AgentTool):
    """
    Mock AgentTool for generating a Notes/Docs packing list.
    """
    
    @property
    def name(self) -> str:
        return "notes_docs_service"

    @property
    def description(self) -> str:
        return "Generates a travel document containing a packing list and returns its URL."

    @property
    def schema(self) -> type[BaseModel]:
        return NotesInput

    async def execute(self, inputs: NotesInput) -> str:
        # Mocking document creation
        items_str = ", ".join(inputs.packing_items)
        doc_id = str(uuid.uuid4())
        doc_url = f"https://docs.google.com/document/d/{doc_id}/view"
        
        # Return structured string which the LLM agent will parse
        return f"Document created successfully with items: [{items_str}]. URL: {doc_url}"
