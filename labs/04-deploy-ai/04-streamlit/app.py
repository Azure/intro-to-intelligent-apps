import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain,LLMChain, RetrievalQA

import os
from dotenv import load_dotenv
import qdrant_client

load_dotenv()

openai_api_type = os.getenv("OPENAI_API_TYPE")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = os.getenv("OPENAI_API_BASE")
openai_api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("OPENAI_COMPLETION_DEPLOYMENT_NAME")
completion_model = os.getenv("OPENAI_COMPLETION_MODEL")
embedding_name = os.getenv("OPENAI_EMBEDDING_DEPLOYMENT_NAME")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_collection = os.getenv("QDRANT_COLLECTION")

st.set_page_config(page_title="Movie expert AI", page_icon="📺")

def settings():

    # Vectorstore
    from langchain.vectorstores import Qdrant
    from langchain.embeddings import OpenAIEmbeddings
    embeddings_model = OpenAIEmbeddings(
        deployment=embedding_name,
        chunk_size=1
    ) 

    client = qdrant_client.QdrantClient(
        qdrant_url
    )

    vector_store = Qdrant(
        client=client, collection_name=qdrant_collection, 
        embeddings=embeddings_model,
    )

    # LLM
    from langchain.llms import AzureOpenAI
    from langchain.chat_models import AzureChatOpenAI
    llm = AzureChatOpenAI(
        openai_api_type = openai_api_type,
        openai_api_version = openai_api_version,
        openai_api_base = openai_api_base,
        openai_api_key = openai_api_key,
        deployment_name = deployment_name,
        model_name=completion_model
    )

    retriever = vector_store.as_retriever(search_type="mmr")

    return retriever, llm

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.info(self.text)


class PrintRetrievalHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container.expander("Context Retrieval")

    def on_retriever_start(self, query: str, **kwargs):
        self.container.write(f"**Question:** {query}")

    def on_retriever_end(self, documents, **kwargs):
        # self.container.write(documents)
        for idx, doc in enumerate(documents):
            source = doc.metadata["source"]
            self.container.write(f"**Results from {source}**")
            self.container.text(doc.page_content)


st.sidebar.image("movieagent.jpg")
st.header("`Movie AI Agent`")
st.info("`I am an AI that can answer questions about all the movies you told me earlier.`")

# Make retriever and llm
if 'retriever' not in st.session_state:
    st.session_state['retriever'], st.session_state['llm'] = settings()
retriever = st.session_state.retriever
llm = st.session_state.llm

# User input 
question = st.text_input("`Ask a question:`")

if question:
    qa_sources_chain = RetrievalQAWithSourcesChain.from_chain_type(llm, retriever=retriever)
    retrieval_streamer_cb = PrintRetrievalHandler(st.container())
    answer = st.empty()
    stream_handler = StreamHandler(answer, initial_text="`Answer:`\n\n")
    result = qa_sources_chain({"question": question},callbacks=[retrieval_streamer_cb, stream_handler])
    print(result)
    answer.info('`Answer:`\n\n' + result['answer'])
    st.info('`Sources:`\n\n' + result['sources'])