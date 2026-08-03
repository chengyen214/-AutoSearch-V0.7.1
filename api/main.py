"""
AutoSearch V3

FastAPI API Layer

功能：

    API Entry Point

    V2.5 Article API

    V3 AI Retrieval API

"""


from fastapi import FastAPI


from api.routes import articles





# uvicorn api.main:app
#
# http://127.0.0.1:8000/docs



app = FastAPI(

    title="AutoSearch V3 API",

    version="3.0"

)





# ==========================
# Router Register
# ==========================


app.include_router(

    articles.router

)





# ==========================
# Root
# ==========================


@app.get("/")
def root():


    return {


        "project":

        "AutoSearch V3",



        "status":

        "running"



    }