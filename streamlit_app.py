import streamlit as st
from openai import OpenAI

st.title("GPT-5-mini 웹앱")

st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",
    key="api_key"  
)
api_key = st.session_state.get("api_key", "")

with open("library_rules.txt", "r", encoding="utf-8") as f:
    LIB_RULES = f.read()

page = st.sidebar.radio("페이지 선택", ["Q&A", "Chat", "Chatbot"])

if page == "Q&A":
    st.subheader("단일 질문 / 답변 (Chat Completions)")

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

elif page == "Chat":
    st.subheader("대화형 챗봇 (Responses API)")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []  
    if "prev_response_id" not in st.session_state:
        st.session_state.prev_response_id = None

    if st.button("Clear"):
        st.session_state.chat_messages = []
        st.session_state.prev_response_id = None
        st.success("대화가 초기화되었습니다.")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not api_key:
        st.warning("Chat을 사용하려면 먼저 상단에 OpenAI API Key를 입력하세요.")
    else:
        user_input = st.chat_input("메시지를 입력하세요")

        if user_input:
            try:
                client = OpenAI(api_key=api_key)

                st.session_state.chat_messages.append(
                    {"role": "user", "content": user_input}
                )
                with st.chat_message("user"):
                    st.markdown(user_input)

                kwargs = {
                    "model": "gpt-5-mini",
                    "input": user_input,
                }
                if st.session_state.prev_response_id:
                    kwargs["previous_response_id"] = st.session_state.prev_response_id

                response = client.responses.create(**kwargs)

                assistant_text = response.output_text
                st.session_state.prev_response_id = response.id

                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": assistant_text}
                )
                with st.chat_message("assistant"):
                    st.markdown(assistant_text)

            except Exception as e:
                st.error(f"에러 발생: {e}")

elif page == "Chatbot":
    st.subheader("국립부경대학교 도서관 챗봇")

    st.markdown(
        "이 챗봇은 **국립부경대학교 도서관 규정** 문자열(`LIB_RULES`)을 기반으로 "
        "도서관 이용 관련 질문에 답변합니다. 규정에 없는 내용은 모른다고 답하도록 설계되어 있습니다."
    )

    if not api_key:
        st.warning("Chatbot을 사용하려면 먼저 상단에 OpenAI API Key를 입력하세요.")
    else:
        question = st.text_input("도서관 이용에 대해 궁금한 점을 입력하세요")

        if st.button("도서관 챗봇에게 물어보기"):
            if not question:
                st.error("질문을 입력하세요.")
            else:
                try:
                    client = OpenAI(api_key=api_key)

                    system_prompt = (
                        "너는 국립부경대학교 도서관 규정을 안내하는 챗봇이다. "
                        "아래에 주어진 도서관 규정 텍스트를 기반으로만 한국어로 답변해라. "
                        "규정에 없는 내용이거나 확실하지 않은 경우에는 '해당 규정에서 찾을 수 없습니다.' 와 같이 "
                        "모른다고 솔직하게 말해라.\n\n"
                        "===== 국립부경대학교 도서관 규정 =====\n"
                        f"{LIB_RULES}\n"
                        "=====================================\n"
                    )

                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question},
                        ],
                    )

                    answer = response.choices[0].message.content
                    st.subheader("도서관 챗봇의 답변:")
                    st.write(answer)

                except Exception as e:
                    st.error(f"에러 발생: {e}")