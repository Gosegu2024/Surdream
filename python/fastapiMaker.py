# pip install langchain
# pip install langchain-openai
# pip install -U langchain-community tavily-python
# pip install beautifulsoup4
# pip install langchainhub

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
from langchain_community.document_loaders import DirectoryLoader

# ---------- FastAPI -----------
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# cors 설정을 위해서 import
from fastapi.middleware.cors import CORSMiddleware
# json 반환을 위해서 import
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# ---------- Tavily ----------
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor

import haedream as hd


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

    llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

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

    async def retriver_rag():
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

        result = await tavily_search(retriever)
        return result

    # tavily api를 이용해서 search
    async def tavily_search(retriever):
        # Tavily search
        retriever_tool = create_retriever_tool(
        retriever,
        "information_search",
        "you must use this tool!",
        )

        # 도구 생성
        search = TavilySearchResults()
        tools = [retriever_tool, search]

        # Get the prompt to use - you can modify this!
        prompt = hub.pull("hwchase17/openai-functions-agent")

        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        result = await invoke_tavily(agent_executor)

        result = result["output"]

        # log test(오류남)
        # runner = hd.ModelRunner()
        # modelName = "test_model"
        # projectName = "테스트 프로젝트"
        # inputData = topic
        # apiKey = "857U1PNndKw*mNsj1GZK" # Test api
        # outputData = result

        # runner.run_model(modelName, projectName, inputData, apiKey, outputData)

        return result
        


    async def invoke_tavily(agent_executor):
        return await agent_executor.ainvoke(
                {
                "input": f"""프로젝트 주제 {topic}에 대한 기획서의 {section}부분을 기획서 형식으로 작성해줘. 기획서에 들어가는 문장은 존댓말을 쓰면 안돼. 
                최신 자료를 바탕으로 확실한 근거를 가지고 작성해주고 자료의 출처도 마지막에 적어줘. 출처는 a태그로 감싸줘. {section}이 제안배경 및 필요성이라면 {topic}에 대한 업계 동향도 넣어줘. 결과물에는 개행표시는 쓰지말고 <br>태그를 넣어줘. 
                br태그의 위치는 소제목 다음에 있으면 좋겠고 *표시도 빼주면 좋겠어.
                소제목은 b태그로 감싸줘."""
                }
            )
    

    async def invoke_rag():
        return await retrieval_chain.ainvoke(
            {
                "context": f"기획서 주제 : {topic}",
                "input": f"프로젝트 주제 {topic}에 대한 기획서의 {section}부분을 작성해줘",
            }
        )

    result = await retriver_rag()

    print(result)

    return JSONResponse(content=jsonable_encoder(result))


# 서버 on(실행되면 아래쪽 코드들이 실행이 안되기때문에 맨 아래 둬야할듯)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006)
