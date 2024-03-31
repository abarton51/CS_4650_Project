from typing import Any
from abc import abstractmethod
from langchain_core.vectorstores import VectorStore
from langchain.prompts import PromptTemplate

class RALM:
    '''Generic class wrapping retrieval augmented langauge models'''

    def __init__(self, vector_db : VectorStore):
        self.vector_db = vector_db
        self.provide_no_context = False
    
    def retrieve_context(self, question : str, k : int) -> list[str]:
        '''Retrieve the top-k most relevant context to the prompt'''
        if self.provide_no_context is False: # Remove after we have context vectors
            relevant_context_chunks = self.vector_db.similarity_search(question, k)

            return [context_chunk.page_content for context_chunk in relevant_context_chunks]
        else:
            return ["There is no context."]
        
    def generate_prompt(self, question : str, k : int = 4) -> str:
        '''Generates an LLM prompt (context, question, specifications), provided the question, utilizing k context chunks'''
        context = " , ".join(self.retrieve_context(question, k))
        
        prompt = PromptTemplate.from_template("""<|user|>
            CONTEXT: {context}

            QUESTION: {question}

            Given CONTEXT, respond to the QUESTION. If the selected CONTEXT is relevant and informative, provide a detailed answer to the QUESTION based on its content. However, if the selected CONTEXT does not offer useful information regarding the QUESTION or is not applicable to the QUESTION, simply state 'No answer found'.
        """)

        return prompt.format(context=context, question=question)

    @abstractmethod
    def format_output(self, output : Any) -> str:
        '''Trims or performs other operations on the LM's output to convert to a readable string'''
        pass

    @abstractmethod
    def predict(self, question : str) -> str:
        '''Computes the response of the LM given the appropriate prompt generated by the question'''
        pass