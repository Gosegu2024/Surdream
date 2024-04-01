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
import asyncio

# cors 설정을 위해서 import
from fastapi.middleware.cors import CORSMiddleware

# requests를 써서 java로 output 보내기 위해서 import
import requests

app = FastAPI()

# cors 설정(get, post로 설정해주기 위해서 씀)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class Topic(BaseModel):
    topic: str


@app.get("/")
def root():
    return {"root"}


# 각 section별 질의
section_list = [
    "제안배경 및 필요성",
    "개발목표",
    "개발내용",
    "기대효과 및 활용방안",
    "STP전략",
    "데이터 확보방안",
]


# 사용자가 입력한 topic을 받아오는 엔드포인트
@app.post("/receive_json")
async def receive_text(topic: Topic):
    # 전송된 텍스트를 출력
    print("Received text:", topic)

    llm = ChatOpenAI(model="gpt-3.5-turbo")

    # 출력 구문 분석기(채팅 메시지를 문자열로 변환)
    output_parser = StrOutputParser()

    # prompt 설계
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "프로젝트 주제 {input}에 대한 기획서의 {system}부분을 작성해줘",
            )
        ]
    )

    # Chain으로 결합
    chain = prompt | llm | output_parser

    async def invoke(section, results):
        result = await chain.ainvoke({"system": [section], "input": topic})
        results.append({"section": section, "result": result})
        print(section, result)

    async def invoke_parallel(section_list):
        results = []
        tasks = [invoke(section, results) for section in section_list]
        await asyncio.gather(*tasks)
        return results

    results = await invoke_parallel(section_list)

    print(results)


# 서버 on(실행되면 아래쪽 코드들이 실행이 안되기때문에 맨 아래 둬야할듯)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006)
