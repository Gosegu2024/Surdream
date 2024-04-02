# LangChain 설치
# pip install langchain
# LangChain x OpenAI 통합 패키지 인스톨
# pip install langchain-openai

###

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ---------- FastAPI -----------
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# cors 설정을 위해서 import
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

## os를 이용해서 환경변수 설정해주기!!

app = FastAPI()

# cors 설정(get, post로 설정해주기 위해서 씀)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class TopicSection(BaseModel):
    topic: str
    section: str

# 결과를 저장할 클래스 정의
class Result(BaseModel):
    section: str
    result: str

@app.get("/")
def root():
    return {"root"}

# 사용자가 입력한 topic을 받아오는 엔드포인트
@app.post("/receive_json")
async def receive_text(topic_section:TopicSection):

    topic = topic_section.topic
    section = topic_section.section
    
    # 전송된 텍스트를 출력
    print("Received text:", topic , section)

    llm = ChatOpenAI(model="gpt-4-turbo-preview")

    # 출력 구문 분석기(채팅 메시지를 문자열로 변환)
    output_parser = StrOutputParser()

    # prompt 설계
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "프로젝트 주제 {topic}에 대한 기획서의 {section}부분을 작성해주고 html에 바로 삽입할거라서 ###나 **같은 기호는 사용하지 말고 \n으로 줄바꿈을 나타내줘"
            )
        ]
    )

    # Chain으로 결합
    chain = prompt | llm | output_parser

    async def invoke():
        result = await chain.ainvoke({"section": section, "topic": topic})
        return result

    result = await invoke()
    print(result)

    return JSONResponse(content=jsonable_encoder(result))

# 서버 on(실행되면 아래쪽 코드들이 실행이 안되기때문에 맨 아래 둬야할듯)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006)
