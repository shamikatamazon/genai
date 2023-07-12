import streamlit as st
from langchain.llms import OpenAI
import logging
import sys
import boto3


st.title('Fruitstand Support App - Using Falcon for Summarization')

from typing import List
from typing import Dict
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain import SagemakerEndpoint
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain


import json

from langchain.docstore.document import Document

region = "us-east-1"

class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf-8"))
#        return response_json["vectors"]
        return response_json[0]["generated_text"]


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler = logging.FileHandler('kendra-queries.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)

content_handler = ContentHandler()

def generate_response(input_text):
  llm2 = SagemakerEndpoint(
    endpoint_name="hf-llm-falcon-40b-instruct-bf16-2023-06-23-19-34-33-102",
    #endpoint_name="hf-llm-falcon-7b-bf16-2023-06-24-20-08-14-262",
    #endpoint_name="hf-llm-falcon-40b-bf16-2023-06-24-20-20-44-608",
    model_kwargs={
         "parameters" : {"do_sample": False,
        "top_p": 0.9,
        "temperature": 0.1,
        "max_new_tokens": 200
                  }},
    region_name="us-east-1",
    content_handler=content_handler
  )
  
  chunkSize = int(chunk_size)
  
  text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size = chunkSize,
    chunk_overlap  = 100,
    length_function = len,
    )
  
  docs = text_splitter.create_documents([input_text])
  #st.info(docs)
  
  map_prompt_template = """Write a short sentence single line summary for following text:
    {text}
    Summary:"""

  reduce_prompt_template = """Write a summary paragraph of the following:
    {text}
    Summary:"""
  
  MAP_PROMPT = PromptTemplate(template=map_prompt_template, input_variables=["text"])
  REDUCE_PROMPT = PromptTemplate(template=reduce_prompt_template, input_variables=["text"])



  chain = load_summarize_chain(llm2, chain_type="map_reduce", return_intermediate_steps=True, map_prompt=MAP_PROMPT,  combine_prompt=REDUCE_PROMPT)
  #chain.run(docs)
  output = chain({"input_documents": docs}, return_only_outputs=True)
  
  logger.info(output)
  st.info(output['output_text'])
  

with st.form('my_form'):
  chunk_size = st.text_input("Document Chunk size ", value="4000")    
  text = st.text_area('Enter text for summarization')
  submitted = st.form_submit_button('Submit')
  if submitted:
    generate_response(text)
    

with st.sidebar:
  add_markdown= st.subheader('About the demo')
  add_markdown= st.markdown('This page will summarize a document using the map-reduce chain')
  add_markdown= st.markdown('You can enter a blurb of text and then play around with the document chunk size.')
  add_markdown= st.markdown('Since the token size for Falcon is only 1024 input tokens, the document is split into multiple chunks, each chunk is summarized and then there is an overall summary presented to the user')
  
  
