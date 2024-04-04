# pip install langchain
# pip install langchain-openai

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

# ---------- FastAPI -----------
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# cors 설정을 위해서 import
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


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
    input_link: str


# 결과를 저장할 클래스 정의
class Result(BaseModel):
    section: str
    result: str


@app.get("/")
def root():
    return {"root"}


# 사용자가 입력한 topic을 받아오는 엔드포인트
@app.post("/receive_json")
async def receive_text(topic_section: TopicSection):

    topic = topic_section.topic
    section = topic_section.section

    # 전송된 텍스트를 출력
    print("Received text:", topic, section)

    llm = ChatOpenAI(model="gpt-4-turbo-preview")

    # 출력 구문 분석기(채팅 메시지를 문자열로 변환)
    output_parser = StrOutputParser()

    # prompt 설계
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "프로젝트 주제 {topic}에 대한 기획서의 {section}부분을 작성해주고 html에 바로 삽입할거라서 ###나 **같은 기호는 사용하지 말고 \n으로 줄바꿈을 나타내줘",
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


# rag 적용해서 돌리기
@app.post("/receive_rag")
async def execute_retrival(topic_section: TopicSection):
    print("rag 시작시작~")

    llm = ChatOpenAI(model="gpt-4-turbo-preview")

    topic = topic_section.topic
    section = topic_section.section
    url = topic_section.input_link

    print("Received text:", topic, section, url)

    loader = WebBaseLoader(url)
    docs = loader.load()
    embeddings = OpenAIEmbeddings()
    print("web base loader 실행 완료")

    # 모델 토큰 수 제한 문제 해결 위해 분할
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)

    # 텍스트 → 벡터 임베딩 변환
    vector = FAISS.from_documents(documents, embeddings)
    print("텍스트 벡터 임베딩 변환 완료")

    # 검색 체인 생성
    prompt = ChatPromptTemplate.from_template(
        """context:<context>{context}</context>
                                                Question: {input}"""
    )
    document_chain = create_stuff_documents_chain(llm, prompt)

    # 가장 관련성이 높은 문서를 동적으로 선택하고 전달
    retriever = vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    async def invoke_rag():
        return await retrieval_chain.ainvoke(
            {
                "context": f"기획서 주제 : {topic}",
                "input": f"프로젝트 주제 {topic}에 대한 기획서의 {section}부분을 작성해줘",
            }
        )

    result = await invoke_rag()

    result = result["answer"]

    print(result)

    return JSONResponse(content=jsonable_encoder(result))


# 서버 on(실행되면 아래쪽 코드들이 실행이 안되기때문에 맨 아래 둬야할듯)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006)
