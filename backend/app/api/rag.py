from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.rag.answer_service import answer_question
from app.rag.schemas import RagAnswerRequest, RagAnswerResponse
from app.services.data_loader import DataFileNotFoundError


router = APIRouter()


@router.post("/answer", response_model=RagAnswerResponse)
def answer_question_endpoint(request: RagAnswerRequest) -> RagAnswerResponse:
    try:
        response = answer_question(
            question=request.question,
            limit=request.limit,
            company_id=request.company_id,
            deal_id=request.deal_id,
            visibility=request.visibility,
            doc_type=request.doc_type,
            sector=request.sector,
            sentiment=request.sentiment,
            include_graph_context=request.include_graph_context,
            llm_provider=request.llm_provider,
        )

        return RagAnswerResponse(**response)

    except DataFileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
