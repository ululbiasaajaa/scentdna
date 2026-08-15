import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from src.search import ScentSearchEngine
from src.services.advisor import FragranceAdvisor
from src.api.schemas import (
    SearchRequest, SearchResponse, ProductResult,
    RecommendRequest, RecommendResponse
)

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scentdna_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ScentSearchEngine & FragranceAdvisor...")
    app.state.search_engine = ScentSearchEngine()
    app.state.advisor = FragranceAdvisor()
    logger.info("ScentDNA API Layer initialized successfully!")
    yield
    logger.info("Shutting down ScentDNA API Layer...")

app = FastAPI(
    title="ScentDNA API Engine",
    description="REST API Layer untuk Semantic Fragrance Search & RAG AI Consultant ScentDNA",
    version="1.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "online", "version": "1.1.0"}

@app.post("/search", response_model=SearchResponse, tags=["Search Engine"])
def search_perfumes(payload: SearchRequest):
    try:
        engine: ScentSearchEngine = app.state.search_engine
        
        raw_results = engine.search_similar_perfumes(
            query_text=payload.query,
            top_k=payload.limit,
            min_price=payload.min_price,
            max_price=payload.max_price,
            brand=payload.brand
        )

        mapped_results = [
            ProductResult(
                product_name=item["product_name"],
                similarity=item["score"],
                price=item.get("price"),
                source_url=item["source_url"],
                top_notes=item.get("top_notes", []),
                middle_notes=item.get("middle_notes", []),
                base_notes=item.get("base_notes", [])
            )
            for item in raw_results
        ]

        return SearchResponse(query=payload.query, total_results=len(mapped_results), results=mapped_results)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error.")

@app.post("/recommend", response_model=RecommendResponse, tags=["AI Fragrance Advisor"])
def recommend_perfumes(payload: RecommendRequest):
    try:
        advisor: FragranceAdvisor = app.state.advisor
        
        rag_output = advisor.recommend_perfume(
            query=payload.query,
            top_k=payload.limit,
            min_price=payload.min_price,
            max_price=payload.max_price,
            brand=payload.brand
        )

        mapped_products = [
            ProductResult(
                product_name=item["product_name"],
                similarity=item["score"],
                price=item.get("price"),
                source_url=item["source_url"],
                top_notes=item.get("top_notes", []),
                middle_notes=item.get("middle_notes", []),
                base_notes=item.get("base_notes", [])
            )
            for item in rag_output["retrieved_products"]
        ]

        return RecommendResponse(
            query=rag_output["query"],
            ai_recommendation=rag_output["ai_recommendation"],
            retrieved_products=mapped_products
        )
    except Exception as e:
        logger.error(f"RAG Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI recommendation failed.")