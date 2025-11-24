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

page = st.sidebar.radio("페이지 선택", ["Q&A", "Chat", "Chatbot", "ChatPDF"])

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

elif page == "ChatPDF":
    st.subheader("ChatPDF: 업로드한 PDF와 대화하기")

    if "pdf_vector_store_id" not in st.session_state:
        st.session_state.pdf_vector_store_id = None
    if "pdf_chat_messages" not in st.session_state:
        st.session_state.pdf_chat_messages = []

    uploaded_file = st.file_uploader(
        "PDF 파일을 업로드하세요",
        type=["pdf"],
        accept_multiple_files=False,
        key="pdf_file"
    )

    if st.button("Clear PDF & Vector Store"):
        if not api_key:
            st.error("먼저 OpenAI API Key를 입력하세요.")
        else:
            try:
                if st.session_state.pdf_vector_store_id:
                    client = OpenAI(api_key=api_key)
                    client.vector_stores.delete(
                        vector_store_id=st.session_state.pdf_vector_store_id
                    )
                st.session_state.pdf_vector_store_id = None
                st.session_state.pdf_chat_messages = []
                st.success("Vector store와 대화 기록이 초기화되었습니다.")
            except Exception as e:
                st.error(f"Vector store 삭제 중 에러 발생: {e}")

    if not api_key:
        st.warning("ChatPDF를 사용하려면 먼저 상단에 OpenAI API Key를 입력하세요.")
        st.stop()

    client = OpenAI(api_key=api_key)

    if uploaded_file is not None and st.session_state.pdf_vector_store_id is None:
        try:
            with st.spinner("PDF를 업로드하고 인덱싱 중입니다..."):
                vector_store = client.vector_stores.create(
                    name="ChatPDF Vector Store"
                )

                file_obj = client.files.create(
                    file=uploaded_file,
                    purpose="assistants"
                )

                client.vector_stores.files.create(
                    vector_store_id=vector_store.id,
                    file_id=file_obj.id,
                )

                st.session_state.pdf_vector_store_id = vector_store.id
                st.success("PDF 업로드 및 인덱싱 완료! 이제 아래에서 질문을 입력하세요.")
        except Exception as e:
            st.error(f"PDF 처리 중 에러 발생: {e}")

    for msg in st.session_state.pdf_chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if st.session_state.pdf_vector_store_id:
        user_q = st.chat_input("업로드한 PDF 내용에 대해 질문해 보세요.")
        if user_q:
            try:
                st.session_state.pdf_chat_messages.append(
                    {"role": "user", "content": user_q}
                )
                with st.chat_message("user"):
                    st.markdown(user_q)

                response = client.responses.create(
                    model="gpt-5-mini",
                    input=user_q,
                    tools=[
                      {
                        "type": "file_search",
                        "vector_store_ids": [st.session_state.pdf_vector_store_id]
                        }
                    ]
                )

                answer = response.output_text

                st.session_state.pdf_chat_messages.append(
                    {"role": "assistant", "content": answer}
                )
                with st.chat_message("assistant"):
                    st.markdown(answer)

            except Exception as e:
                st.error(f"ChatPDF 응답 생성 중 에러 발생: {e}")
    else:
        st.info("먼저 PDF 파일을 업로드하면, 그 내용을 바탕으로 대화할 수 있습니다.")
