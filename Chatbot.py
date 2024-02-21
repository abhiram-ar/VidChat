import streamlit as st
import whisper
from pytube import YouTube


from langchain.llms import OpenAI
import os

from langchain.document_loaders import YoutubeLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI



os.environ['OPENAI_API_KEY'] = "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" #college mail
os.environ['SERPAPI_API_KEY'] = "8fa5978d9eed2531ce372d539819973cf68b8ab39795f0bf624152da4019629f"



st.set_page_config(page_title="VidChat", page_icon=":books:")
#st.header("VidChat :books:")



model = whisper.load_model("base")  #its better to move this out of her for speed startup
#model.device
#CPU takes 10minutes to infrecnce
#while GPU infrence takes only 60s
#screenshots availaable in windows


with st.sidebar:
    st.subheader("Data Center")

    #link input and validation
    yt_link = st.text_input("Enter Video Link",placeholder="Video link",key="video_link", type="default")

    method = st.selectbox('Processing Method',('Captions', 'Audio'))

    if (st.button("process")):
      #implementing the spinner
      with st.spinner("Processing"):

        if("youtube.com" not in yt_link):
          #do regix match for validity of link
          #re = http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?
          st.error("invalid link")
          st.stop()

        #create the txt doc
        if(method == "Audio"):
          yt = YouTube(yt_link)
          audio = yt.streams.filter(only_audio=True).first()
          a = audio.download()  #path to file - sting class
          transcript = "text corpus"
          transcript = model.transcribe(a)['text']
          print(transcript)

          #mining metadata
          authur = yt.author
          title = yt.title
          thumbnail_link = yt.thumbnail_url

        else:
          url = yt_link
          loader = YoutubeLoader.from_youtube_url(url, add_video_info = True)
          documents = loader.load()
          transcript = " ".join([doc.page_content for doc in documents])
          
          #metadata object
          #  'source': 'fhgPzcJbyls', 
          #  'title': 'Full interview: Nikki Haley tells NBC News Trump is ‘not qualified to be president’', 
          #  'description': 'Unknown',
          #  'view_count': 40716, 
          #  'thumbnail_url': 'https://i.ytimg.com/vi/fhgPzcJbyls/hq720.jpg', 
          #  'publish_date': '2024-02-14 00:00:00', 
          #  'length': 1374, 
          #  'author': 'TODAY'}
        
          title = documents[0].metadata['title']
          authur = documents[0].metadata['author']
          thumbnail_link = documents[0].metadata['thumbnail_url']


        #st.image('https://i.ytimg.com/vi/fhgPzcJbyls/hq720.jpg')
        st.image(thumbnail_link)
        st.write( title)
        st.write("Uploaded by : " +authur)

        #converting documents to chunks
        text_spliter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        splits = text_spliter.split_text(transcript)

        #build vector store
        embeddings = OpenAIEmbeddings()
        vectordb = FAISS.from_texts(splits,embeddings)

        #building a QA chian
        #making sure the model dont reload on session refresh
        st.session_state.chatmodel = RetrievalQA.from_chain_type(
           llm= OpenAI(temperature=0),
           chain_type="stuff",
           retriever=vectordb.as_retriever(),
        )
        
        st.write(st.session_state.chatmodel.run("write a summary"))



    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"



st.title("💬 VidChat")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Enter the Video link to continue."}]

for msg in st.session_state.messages:
    #st.chat_message(msg["role"]).write(msg["content"])
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder = "Ask something about the article" ,disabled= not yt_link):
    if not openai_api_key:
        st.info("Key Error")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)