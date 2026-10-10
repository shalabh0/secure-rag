from fastapi import FastAPI
from app.services.llm import generate_response


app = FastAPI(
    title="Secure Enterprise RAG",
    description="Secure Enterprise RAG API",
    version="0.1.0",

)

@app.get("/")
async def root():

    response = generate_response(
        "Say helo from Secure Enterprise RAG"
    )
    return{

        "reponse" : response
    }