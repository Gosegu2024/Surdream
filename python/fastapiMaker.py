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
        # loader = DirectoryLoader(".", glob="data/*.txt", show_progress=True)
        docs = loader.load()

        print(f"문서의 수: {len(docs)}")

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

        print(result)

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
        if topic == "제안배경 및 필요성":
            print("제안배경 실행!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return await agent_executor.ainvoke(
                {
                "input": f"""프로젝트 주제 {topic}에 대한 기획서의 {section}부분을 기획서 형식으로 작성해줘. 기획서에 들어가는 문장은 존댓말을 쓰면 안돼. 꼭! 업계 동향도 알려줘!
                최신 자료를 바탕으로 확실한 근거를 가지고 작성해주고 자료의 출처도 마지막에 적어줘. 출처는 a태그로 감싸주고 파란색으로 보이게 해줘. 결과물에는 개행표시는 쓰지말고 <br>태그를 넣어줘. 
                br태그의 위치는 소제목 다음에 있으면 좋겠어. 특수문자도 쓰지 마. 특히 ** 이 특수문자는 절대 쓰지마!
                소제목은 b태그로 감싸줘."""
                }
            )
        else:
            return await agent_executor.ainvoke(
                {
                "input": f"""프로젝트 주제 {topic}에 대한 기획서의 {section}부분을 기획서 형식으로 작성해줘. 기획서에 들어가는 문장은 존댓말을 쓰면 안돼. 
                최신 자료를 바탕으로 확실한 근거를 가지고 작성해주고 자료의 출처도 마지막에 적어줘. 출처는 a태그로 감싸주고 파란색으로 보이게 해줘. 결과물에는 개행표시는 쓰지말고 <br>태그를 넣어줘. 
                br태그의 위치는 소제목 다음에 있으면 좋겠어. 특수문자도 쓰지 마. 특히 ** 이 특수문자는 절대 쓰지마!
                소제목은 b태그로 감싸줘.
                예시를 알려줄게
                제안 배경
2023년은 LLM (대형 언어 모델) 분야에서 상당한 성장과 혁신이 이루어진 해였다. AI 기술의 빠른 발전과 함께, 오픈 소스 LLM의 등장은 기술과 상호 작용하는 방식을 재구성하고 있다. 특히, 오픈소스 LLM은 비용 절감, 시스템의 효율성 증대, 그리고 다양한 영역에서의 적용 가능성을 제공하며, 이는 기업과 스타트업에게 새로운 기회를 열어주고 있다.

필요성
오픈소스 LLM을 활용한 키오스크 사업은 여러 면에서 혁신적이다. 첫째, 사용자 경험을 극대화할 수 있다. AI 기반의 언어 모델을 통해 사용자의 요구를 더 정확하게 파악하고, 이에 맞는 응답을 제공함으로써 사용자 만족도를 높일 수 있다. 둘째, 기업의 운영 효율성을 증대시킬 수 있다. 오픈소스 LLM을 이용하면 개발 비용과 시간을 크게 절약할 수 있으며, 이는 특히 자본이 제한적인 중소기업이나 스타트업에게 큰 이점을 제공한다. 셋째, 키오스크 사업의 경쟁력을 강화할 수 있다. AI 기술을 통해 제공할 수 있는 서비스의 범위가 확장되며, 이는 소비자에게 보다 차별화된 서비스를 제공할 수 있는 기회를 의미한다.
                
개발 내용
본 프로젝트는 LLM을 활용한 키오스크 사업을 목표로 하며, 최신 오픈소스 LLM 모델을 기반으로 사용자 경험을 혁신하고, 기업 운영의 효율성을 극대화할 방안을 모색한다. 이를 위해 다음과 같은 개발 내용을 포함한다.

1. 오픈소스 LLM 모델의 선정 및 적용
2024년 최고의 오픈소스 LLM 중 하나인 라마 2를 주요 모델로 선정한다. 라마 2는 메타 AI에서 개발한 모델로, 다양한 크기와 용도에 맞춰 최적화된 성능을 제공한다. 이 모델을 키오스크 시스템에 적용하여, 사용자 질문에 대한 정확하고 빠른 응답을 가능하게 한다.

2. 사용자 인터페이스(UI) 개선
LLM의 자연어 처리 능력을 활용하여, 키오스크의 사용자 인터페이스를 개선한다. 이를 통해 사용자가 자연어로 질문하거나 명령을 할 수 있는 직관적인 UI를 제공하며, 사용자 경험을 대폭 향상시킨다.

3. 맞춤형 서비스 제공
사용자 데이터 분석을 통해 개인화된 서비스를 제공한다. LLM을 이용하여 사용자의 선호도와 이전 상호작용을 분석, 맞춤형 메뉴 추천이나 프로모션 정보를 제공함으로써 사용자 만족도를 높인다.

4. 효율적인 시스템 운영
오픈소스 LLM을 활용함으로써 개발 비용과 시간을 절약한다. 또한, 시스템 유지보수 및 업데이트를 용이하게 하여, 운영 효율성을 증대시킨다.
                """
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

    return JSONResponse(content=jsonable_encoder(result))


# 서버 on(실행되면 아래쪽 코드들이 실행이 안되기때문에 맨 아래 둬야할듯)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006)
