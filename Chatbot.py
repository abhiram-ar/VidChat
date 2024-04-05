import streamlit as st
import whisper
from pytube import YouTube
from dotenv import load_dotenv

from langchain.llms import OpenAI
import os

from langchain.document_loaders import YoutubeLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

load_dotenv()
#os.environ['OPENAI_API_KEY'] = "" #college mail
os.environ['SERPAPI_API_KEY'] = "8fa5978d9eed2531ce372d539819973cf68b8ab39795f0bf624152da4019629f"


st.set_page_config(page_title="VidChat", page_icon=":books:")
#st.header("VidChat :books:")

#if error remove comment
#llm = OpenAI(temperature=0)
#tools = load_tools(['serpapi'])
#agent = initialize_agent(tools, llm, agent='zero-shot-react-description')


model = whisper.load_model("base")  #its better to move this out of her for speed startup

#CPU takes 10minutes to infrecnce
#while GPU infrence takes only 60s
#screenshots availaable in windows

if "chatmodel" not in st.session_state:
   st.session_state.chatmodel = None
 
if "title" not in st.session_state:
   st.session_state.title = "Nill"

if "authur" not in st.session_state:
   st.session_state.authur = None
  
if "thumbnail_link" not in st.session_state:
   st.session_state.thumbnail_link = "/workspaces/VidChat/logo.png"

with st.sidebar:
    st.subheader("Data Center")

    #link input and validation
    yt_link = st.text_input("Enter Video Link",placeholder="Video link",key="video_link", type="default")
    model.device

    method = st.selectbox('Processing Method',('Captions', 'Audio'))

    col1, col2 = st.columns(2)

    if (col1.button("Process", use_container_width = True)):
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

          #addding metadata to the text-corpus
          title = f"Title of the video is '{yt.title}'"
          uploader = f"This video is uploaded by {yt.author}"
          published_date = f"This video is uploded on {yt.publish_date} in YYYY-MM-DD HH-MM-SS format"

          transcript += title
          transcript += uploader
          transcript +=published_date
          

          #mining metadata
          st.session_state.authur = yt.author
          st.session_state.title = yt.title
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

          #adding metadata to text-corpus
          title = f"Title of the video is '{documents[0].metadata['title']}'"
          uploader = f"This video is uploaded by {documents[0].metadata['author']}"
          published_date = f"This video is uploded on {documents[0].metadata['publish_date']} in YYYY-MM-DD HH-MM-SS format"

          transcript += title
          transcript += uploader
          transcript +=published_date

        
          st.session_state.title = documents[0].metadata['title']
          st.session_state.authur = documents[0].metadata['author']
          st.session_state.thumbnail_link = documents[0].metadata['thumbnail_url']


        #old video details
        #st.image('https://i.ytimg.com/vi/fhgPzcJbyls/hq720.jpg')
        #st.image(st.session_state.thumbnail_link)
        #st.write(st.session_state.title)
        #st.write("Uploaded by : " + st.session_state.authur)

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
        #st.write(st.session_state.chatmodel.run("write a summary"))

    if (col2.button("Reset Chat", use_container_width=True)):
      st.session_state.chatmodel = None
      st.session_state.chat_message = None
    
    

    if(st.session_state.thumbnail_link != '/workspaces/VidChat/logo.png'):
      st.divider()
      st.image(st.session_state.thumbnail_link)
      st.write(st.session_state.title)
      st.write("Uploaded by : " + str(st.session_state.authur))
      accuracy_mode = st.checkbox(label="Context Aware (Closed book mode)", value = False)



    


st.title("💬 Vision Verse")


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Enter the Video link to continue."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder = "Ask anything about this video" ,disabled= not yt_link):
    if not os.environ['OPENAI_API_KEY']:
        st.info("Key Error")
        st.stop()

    #client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    if(accuracy_mode == True):
      response = st.session_state.chatmodel.run(prompt + ", based on this Video only,else say you dont know the answer.")
    else:
      response = st.session_state.chatmodel.run(prompt)
    #msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
