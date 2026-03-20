"""
Broadcast router.

For MVP, email is real (if SMTP creds are set), everything else
generates AI content and simulates delivery with a log entry.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import get_db
from models import Favorite, BroadcastLog, NewsItem
from schemas import BroadcastRequest, BroadcastResult
from groq_service import groq_service
from config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


async def _get_favorite_with_item(favorite_id: int, db: AsyncSession) -> Favorite:
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.news_item))
        .where(Favorite.id == favorite_id)
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return fav


def _send_email(recipient: str, subject: str, body: str) -> bool:
    if not all([settings.smtp_host, settings.smtp_user, settings.smtp_password]):
        return False  # Fall through to simulation
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from or settings.smtp_user
        msg["To"] = recipient
        msg.attach(MIMEText(body, "html"))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from or settings.smtp_user, recipient, msg.as_string())
        return True
    except Exception as e:
        logger.warning("Email send failed: %s", e)
        return False


@router.post("", response_model=BroadcastResult)
async def broadcast(req: BroadcastRequest, db: AsyncSession = Depends(get_db)):
    fav = await _get_favorite_with_item(req.favorite_id, db)
    item = fav.news_item

    generated_content = None
    status = "sent"
    message = ""

    if req.platform == "email":
        caption = await groq_service.generate_newsletter_blurb(item.title, item.summary or "")
        body = f"""
        <h2>{item.title}</h2>
        <p>{caption or item.summary}</p>
        <p><a href="{item.url}">Read the full story →</a></p>
        """
        recipient = req.recipient or "user@example.com"
        sent = _send_email(recipient, f"[AI News] {item.title}", body)
        if sent:
            message = f"Email sent to {recipient}"
        else:
            message = f"[Simulated] Email would be sent to {recipient}"
        generated_content = body

    elif req.platform == "linkedin":
        caption = await groq_service.generate_linkedin_caption(item.title, item.summary or "", item.url)
        generated_content = caption
        message = "[Simulated] LinkedIn post generated — copy it to post manually or connect your LinkedIn token."
        status = "simulated"

    elif req.platform == "whatsapp":
        blurb = await groq_service.generate_newsletter_blurb(item.title, item.summary or "")
        generated_content = f"{blurb}\n\nRead more: {item.url}"
        message = "[Simulated] WhatsApp message ready — connect Twilio or WhatsApp Business API to send."
        status = "simulated"

    elif req.platform == "blog":
        summary = item.ai_summary or await groq_service.summarize(item.title, item.summary or "")
        generated_content = f"## {item.title}\n\n{summary}\n\n[Source]({item.url})"
        message = "[Simulated] Blog post snippet generated — integrate with your CMS to publish."
        status = "simulated"

    elif req.platform == "newsletter":
        blurb = await groq_service.generate_newsletter_blurb(item.title, item.summary or "")
        generated_content = blurb
        message = "[Simulated] Newsletter blurb generated — add this to your Mailchimp/Substack draft."
        status = "simulated"

    else:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {req.platform}")

    # Log the broadcast
    log = BroadcastLog(
        favorite_id=fav.id,
        platform=req.platform,
        status=status,
        payload={"recipient": req.recipient, "content_preview": (generated_content or "")[:200]},
        response=message,
    )
    db.add(log)
    await db.commit()

    return BroadcastResult(
        platform=req.platform,
        status=status,
        message=message,
        generated_content=generated_content,
    )
