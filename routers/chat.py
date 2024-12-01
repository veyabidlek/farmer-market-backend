from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas, crud
from dependencies import get_current_user

router = APIRouter()

@router.get('/conversations', response_model=List[schemas.ConversationResponse])
def get_conversations(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = crud.get_conversations_for_user(db, current_user.id)
    return conversations

@router.post('/conversations', response_model=schemas.ConversationResponse)
def create_conversation(conversation_data: schemas.ConversationCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate that the current user is part of the conversation
    if current_user.is_farmer:
        farmer = crud.get_farmer_by_user_id(db, current_user.id)
        if farmer.id != conversation_data.farmer_id:
            raise HTTPException(status_code=403, detail="You can only create conversations involving yourself.")
    elif current_user.is_buyer:
        buyer = crud.get_buyer_by_user_id(db, current_user.id)
        if buyer.id != conversation_data.buyer_id:
            raise HTTPException(status_code=403, detail="You can only create conversations involving yourself.")
    else:
        raise HTTPException(status_code=403, detail="Invalid user type.")

    conversation = crud.get_or_create_conversation(db, conversation_data.farmer_id, conversation_data.buyer_id)
    return conversation


@router.post('/conversations/{conversation_id}/messages', response_model=schemas.MessageResponse)
def send_message(conversation_id: int, message_data: schemas.MessageCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user = current_user
    if user.is_farmer:
        farmer = crud.get_farmer_by_user_id(db, user.id)
        if conversation.farmer_id != farmer.id:
            raise HTTPException(status_code=403, detail="Not part of this conversation")
    elif user.is_buyer:
        buyer = crud.get_buyer_by_user_id(db, user.id)
        if conversation.buyer_id != buyer.id:
            raise HTTPException(status_code=403, detail="Not part of this conversation")
    else:
        raise HTTPException(status_code=403, detail="Invalid user type")

    message = crud.create_message(db, conversation_id, user.id, message_data.content)
    return message

@router.get('/conversations/{conversation_id}/messages', response_model=List[schemas.MessageResponse])
def get_messages(conversation_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = crud.get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user = current_user
    if user.is_farmer:
        farmer = crud.get_farmer_by_user_id(db, user.id)
        if conversation.farmer_id != farmer.id:
            raise HTTPException(status_code=403, detail="Not part of this conversation")
    elif user.is_buyer:
        buyer = crud.get_buyer_by_user_id(db, user.id)
        if conversation.buyer_id != buyer.id:
            raise HTTPException(status_code=403, detail="Not part of this conversation")
    else:
        raise HTTPException(status_code=403, detail="Invalid user type")
    return conversation.messages
