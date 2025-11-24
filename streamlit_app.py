import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="GPT-5-mini Chat")

st.title("GPT-5-mini 챗봇")

st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",
    key="api_key"  
)

api_key = st.session_state.get("api_key", "")

user_question = st.text_input("질문을 입력하세요")


@st.cache_data
def get_answer(api_key: str, user_question: str) -> str:
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
        ],
    )

    answer = response.choices[0].message.content
    return answer


if st.button("질문 보내기"):
    if not api_key:
        st.error("먼저 OpenAI API Key를 입력하세요.")
    elif not user_question:
        st.error("질문을 입력하세요.")
    else:
        try:
            answer = get_answer(api_key, user_question)

            st.subheader("답변:")
            st.write(answer)

        except Exception as e:
            st.error(f"에러 발생: {e}")