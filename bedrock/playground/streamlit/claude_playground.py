import streamlit as st
from langchain.llms import OpenAI
import logging
import sys
import boto3


st.title('Fruitstand Support App - Using Claude/Bedrock')

from typing import List
from typing import Dict
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.chains.question_answering import load_qa_chain
from langchain.retrievers import AmazonKendraRetriever
from langchain import LLMChain
from langchain.llms.bedrock import Bedrock

import json

from langchain.docstore.document import Document

kendraIndexId = "063e46f7-1953-4503-a46c-72aa1ddf826f"
region = "us-east-1"

kendra_retriever = AmazonKendraRetriever(
    index_id= kendraIndexId
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler = logging.FileHandler('kendra-queries-claude.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)


def generate_response(input_text):
    
  llm2 = Bedrock(
    model_id="anthropic.claude-v1",
    model_kwargs={'max_tokens_to_sample': int(maxTokensToSample), 'temperature':float(temp), "top_k":int(topK),"top_p": float(topP),"stop_sequences":[]}
    )
    
  
  llm_query= input_text

  prompt_template = """
  {context}
  use the information above to answer the question {question}"""
  
  PROMPT = PromptTemplate(
      template=prompt_template, input_variables=["context", "question"]
  )
  
  chain = load_qa_chain(llm=llm2, prompt=PROMPT)
  
  docs = ""
  
  if doRag:
    docs = kendra_retriever.get_relevant_documents(llm_query)
  
  #logger.info(docs)
  logger.info("query:" + llm_query)
  logger.info("params "+ maxTokensToSample + " " + temp + " " + topK + " " + topP )
  
  output = chain({"input_documents":docs, "question": llm_query}, return_only_outputs=False)
  #logger.info(output)
  st.info(output['output_text'])
  st.subheader("RAG data obtained from Kendra")
  #st.info(output['input_documents'])
  
  for doc in output['input_documents']:
    st.info(doc)
  

with st.form('my_form'):
  doRag = st.checkbox("RAG - Kendra" , value=True)
  
  maxTokensToSample = st.text_input("max tokens to sample", 300)
  temp = st.text_input("temperature", 0.5)
  topK = st.text_input("top_k", 250)
  topP = st.text_input("top_p", 0.5)
  text = st.text_area('Enter your query:', 'How do I charge my iPhone?')
  submitted = st.form_submit_button('Submit')
  if submitted:
    generate_response(text)
    

with st.sidebar:
  add_markdown= st.subheader('About the demo')
  add_markdown= st.markdown('This is a sample application that uses **Bedrock** with RAG using Kendra. Data for RAG is from the Apple support pages')
  add_markdown= st.markdown('You can ask questions like **:blue["my iphone screen is broken, how can I fix it"]** or **:blue["how do I change the wallpaper on my iphone"]**')
  add_markdown= st.markdown('**WARNING** This website is for demo purposes only and only publicly available information should be shared in the input prompts')
