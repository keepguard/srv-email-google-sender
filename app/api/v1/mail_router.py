
from fastapi import APIRouter, HTTPException
from app.domain.models import EmailPayload
from app.application.usecases.send_email_usecase import SendEmailUseCase
from app.domain.errors import EmailSendError

def build_mail_router(usecase: SendEmailUseCase) -> APIRouter:
    router = APIRouter()

    @router.post("/send/mail")
    def send_mail(payload: EmailPayload):
        try:
            message_id = usecase.execute(payload)
            return {"messageId": message_id}
        except EmailSendError as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
