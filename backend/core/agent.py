import os
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from .ingestion import DB_DIR

# Initialize models
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Router Prompt
router_prompt = ChatPromptTemplate.from_template(
    """You are an expert router. Determine if the following user query requires searching a database of technical documents or if it is a general greeting/question that can be answered directly.
    Respond with ONLY 'retrieve' or 'generate'.
    
    Query: {query}
    Choice:"""
)

# Generation Prompt
rag_prompt = ChatPromptTemplate.from_template(
    """You are an intelligent assistant. Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say you don't know. 
    Keep the answer concise.
    
    Context: {context}
    
    Question: {query}
    
    Answer:"""
)

direct_prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the user's question directly.
    
    Question: {query}
    
    Answer:"""
)

def get_llm():
    """Returns an LLM instance. Using Ollama as the local provider."""
    return ChatOllama(model="deepseek-r1:7b", temperature=0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

class AgenticRAG:
    def __init__(self):
        self.llm = get_llm()
        self.router_chain = router_prompt | self.llm | StrOutputParser()
        self.rag_chain = (
            {"context": retriever | format_docs, "query": RunnablePassthrough()}
            | rag_prompt
            | self.llm
            | StrOutputParser()
        )
        self.direct_chain = direct_prompt | self.llm | StrOutputParser()

    def run(self, query: str):
        print(f"Routing query: {query}")
        route = self.router_chain.invoke({"query": query}).strip().lower()
        print(f"Decided route: {route}")

        if "retrieve" in route:
            return {
                "answer": self.rag_chain.invoke(query),
                "route": "retrieval",
                "sources": [doc.metadata.get("source") for doc in retriever.invoke(query)]
            }
        else:
            return {
                "answer": self.direct_chain.invoke(query),
                "route": "direct_generation",
                "sources": []
            }

if __name__ == "__main__":
    # For testing
    agent = AgenticRAG()
    print(agent.run("What is in my documents?"))
