from pydantic import BaseModel
from typing import Optional, List

class ChatState(BaseModel):
    user_input : str
    chat_history : List[str] = []
    selected_subject : Optional[str] = None
    retreived_chunks : Optional[List[str]] = None
    rag_response : Optional[str] =None
    subject_info : Optional[str] = None
    next_node : Optional[str] = None