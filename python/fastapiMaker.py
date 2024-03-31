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
from typing import Dict
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
    topic : str

class Section(BaseModel):
    # 각 섹션의 필드 정의
    content: str

class DataItem(BaseModel):
    # 섹션을 담는 딕셔너리 형태의 필드 정의
    section1: Section
    section2: Section
    section3: Section
    section4: Section
    section5: Section
    section6: Section

@app.get("/")
def root():
    return {"root"}

# 전역변수 설정
received_topic = None

# 사용자가 입력한 topic을 받아오는 엔드포인트
@app.post("/receive_json")
async def receive_text(topic: Topic):
    # 전송된 텍스트를 출력
    print("Received text:", topic)
    # 전역변수에 저장
    received_topic = topic

    # 모델 실행
    llm_start()

    return {"message": "Text received successfully"}

# java에 데이터 전송(미완성)
# 서버가 돌아가면 그 아래 다른 코드들이 안돌아가서 
# 엔드포인트 안에 기능들을 넣어서 실행시키려고 시도중
# 일단 엔드포인트 밖에있는 함수와 코드들 안에 전부 집어넣음
@app.post("/send_data_to_java")
async def send_data_to_java(data_item: DataItem):
    java_application_url = "http://localhost:8087/receive_data"
    
    # FastAPI에서 생성된 데이터를 Java 애플리케이션에 전송
    response = requests.post(java_application_url, json=data_item.dict())
    
    # 응답 확인
    if response.status_code == 200:
        return {"message": "Data sent to Java application successfully"}
    else:
        return {"error": "Failed to send data to Java application"}

def on_event_occurred(data: DataItem):
    # 데이터 생성
    data_to_send = DataItem(name=data.name, description=data.description)
    
    # Java 애플리케이션에 데이터 전송
    send_data_to_java(data_to_send)

def llm_start():
    # ---------- opinai & langchain -----------
        
    llm = ChatOpenAI()
    # 출력 구문 분석기(채팅 메시지를 문자열로 변환)
    output_parser = StrOutputParser() 

    # 기획서 생성 함수
    def create_proposal(section):
        # prompt 설계
        prompt = ChatPromptTemplate.from_messages([
            ("system", "프로젝트 주제 user에 대한 기획서의 {system}부분을 작성해줘"),
            ("user", "{input}")
        ])

        # Chain으로 결합
        chain = prompt | llm | output_parser
        
        # gpt에 질의
        result = chain.invoke({"system":section,
                                "input": received_topic})
        
        return result

    # 각 section별 질의
    section_list = ['제안배경 및 필요성', '개발목표', '개발내용', '기대효과 및 활용방안', 'STP전략', '데이터 확보방안']
    cnt = 0

    for i in section_list:
        cnt+=1
        globals()[f'section{cnt}'] = create_proposal(i)

    data = {"section1":section1,
            "section2":section2,
            "section3":section3,
            "section4":section4,
            "section5":section5,
            "section6":section6} 

    on_event_occurred(data)

# 서버 on(실행되면 아래쪽 코드들이 실행이 안되기때문에 맨 아래 둬야할듯)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006)

