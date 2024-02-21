import streamlit as st
import whisper
from pytube import YouTube

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
import os

from langchain.document_loaders import YoutubeLoader

os.environ['OPENAI_API_KEY'] = "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" #college mail
os.environ['SERPAPI_API_KEY'] = "8fa5978d9eed2531ce372d539819973cf68b8ab39795f0bf624152da4019629f"

llm = OpenAI(temperature=0)
tools = load_tools(['serpapi'])
agent = initialize_agent(tools, llm, agent='zero-shot-react-description')



st.set_page_config(page_title="VidChat", page_icon=":books:")
#st.header("VidChat :books:")



model = whisper.load_model("base")  #its better to move this out of her for speed startup
#model.device
#CPU takes 10minutes to infrecnce
#while GPU infrence takes only 60s
#screenshots availaable in windows
#fecting the audio





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
          result = "text corpus"
          #result = model.transcribe(a)

          #mining metadata
          authur = yt.author
          title = yt.title

        else:
          url = yt_link
          loader = YoutubeLoader.from_youtube_url(url, add_video_info = True)
          documents = loader.load()
          transcript = " ".join([doc.page_content for doc in documents])

          title = documents[0].metadata['title']
          authur = documents[0].metadata['author']
          #thumbnail_link = documents[0].metadata['thumbnail']


        #st.image('https://i.ytimg.com/vi/fhgPzcJbyls/hq720.jpg')
        st.image(thumbnail_link)
        st.write( title)
        st.write("Uploaded by : " +authur)


    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"



st.title("💬 VidChat")


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Enter the Video link to continue."}]

for msg in st.session_state.messages:
    #st.chat_message(msg["role"]).write(msg["content"])
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder = "Ask something about the article" ,disabled= not yt_link):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)