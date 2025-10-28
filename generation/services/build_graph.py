import json
from typing import Dict
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, END
from .search_relevant_laws import retrieve_relevant_laws
from models.schemas import State



def build_graph(llm):
    def user_input_node(state: State):
        try:
            last_msg = state["messages"][-1]
            if isinstance(last_msg, dict):
                query = last_msg.get("content", "")
            else:
                query = getattr(last_msg, "content", "")

            print(f"\n🧠 User query: {query}")

            # Wrap prompt in HumanMessage
            prompt = f"""Xác định xem câu hỏi này có cần tra cứu thông tin từ tài liệu luật của Việt Nam không:
            Câu hỏi: {query}

            Chỉ trả lời 'legal' hoặc 'general':"""

            is_legal_query = llm.invoke([HumanMessage(content=prompt)]).content.lower().strip()

            route = "legal_search" if "legal" in is_legal_query else "direct_answer"
            print(f"Query type: {'Cần tra cứu tài liệu' if route == 'legal_search' else 'Kiến thức chung'}")

            return {
                "query": query,
                "messages": state["messages"],
                "route": route
            }
        except Exception as e:
            print(f"Error in user_input_node: {e}")
            return {"query": "", "messages": state["messages"], "error": str(e)}

    def direct_answer_node(state: State):
        try:
            query = state.get("query", "")
            prompt = f"""Bạn là trợ lý hữu ích trả lời câu hỏi về luật bảo vệ dữ liệu cá nhân của Việt Nam.
            Trả lời câu hỏi này chỉ sử dụng kiến thức chung của bạn:

            Câu hỏi: {query}

            Trả lời ngắn gọn không trình bày dài dòng."""

            answer = llm.invoke(prompt).content
            #print(f"\n📝 Direct Answer:\n{answer}")
            return {"messages": [{"role": "assistant", "content": answer}]}
        except Exception as e:
            print(f"Error in direct_answer_node: {e}")
            return {"messages": [{"role": "assistant", "content": f"Tôi gặp lỗi: {e}"}]}

    def refine_query_node(state: State):
        try:
            query = state.get("query", "")
            prompt = f"""Nâng cao câu truy vấn này để tìm kiếm tối ưu trong văn bản luật của Việt Nam.

            Câu truy vấn gốc: {query}

            Hãy:
            1. Sửa lỗi chính tả và thuật ngữ pháp lý (nếu có)
            2. Chuyển đổi câu hỏi thông thường thành câu truy vấn pháp lý chính xác
            3. Thêm các thuật ngữ chuyên ngành liên quan đến pháp luật
            4. Xác định các điều khoản hoặc khái niệm pháp lý cụ thể (nếu có thể)
            5. Giữ ngắn gọn, súc tích và rõ ràng về ý định tìm kiếm

            Ví dụ:
            - "quyền của người dùng khi bị lộ thông tin" → "quyền của chủ thể dữ liệu cá nhân khi xảy ra vi phạm dữ liệu"
            - "ai quản lý dữ liệu cá nhân" → "bên kiểm soát dữ liệu cá nhân và trách nhiệm pháp lý"

            Câu truy vấn đã cải thiện:"""


            refined = llm.invoke(prompt).content
            # print(f"🔍 Refined Query: {refined}")

            # Update the state directly
            state["refined_query"] = refined
            return state # Return the modified state
        except Exception as e:
            print(f"Error in refine_query_node: {e}")
            state["refined_query"] = state.get("query", "") # Fallback to original query
            state["error"] = str(e)
            return state

    def semantic_search_node(state: State):
        """
        Perform semantic search with error handling and relevance filtering.
        """
        try:
            query = state.get("refined_query") or state.get("query", "")
            # print(f"🔎 Searching with query: {query}")

            top_docs = retrieve_relevant_laws(
                query=query,
                n_resources_to_return=3,
                print_time=True
            )
            for doc in top_docs:
                print(json.dumps(doc, ensure_ascii=False, indent=2))

            return {"top_docs": top_docs, "query": query, "messages": state["messages"]}
        except Exception as e:
            print(f"Error in semantic_search_node: {e}")
            return {"top_docs": [], "query": state.get("query", ""), "messages": state["messages"], "error": str(e)}

    def generate_answer_node(state: State, llm=llm):
        try:
            query = state.get("query", "")
            top_docs = state.get("top_docs", [])
            # print(f"query", query)
            # print(f"top_docs", top_docs)
            sentence_chunks = [doc["sentence_chunk"] for doc in top_docs]
            context = " ".join(sentence_chunks)
              # Add page references
            page_refs = [str(doc["page_number"]) for doc in top_docs]
            unique_refs = sorted(set(page_refs))
            refs_text = f"\n\n*Tham khảo: Trang {', '.join(unique_refs)} của Luật Bảo vệ dữ liệu cá nhân.*"


            if not top_docs:
                return {"messages": [{"role": "assistant", "content": "Tôi không tìm thấy thông tin liên quan để trả lời câu hỏi của bạn. Vui lòng thử lại với câu hỏi khác."}]}

            # print(f"context", context)
            # print(f"📚 Context length: {len(context)} characters")

            prompt = f"""Bạn là trợ lý pháp lý chuyên về luật của Việt Nam.
            Trả lời câu hỏi dựa trên các trích đoạn văn bản luật bên dưới.

            Các trích đoạn:
            {context}

            Câu hỏi: {query}

            Trả lời theo các tiêu chí sau:
            1. Dựa trên các trích đoạn văn bản luật
            2. Nêu rõ điều, khoản liên quan nếu có
            3. Giải thích bằng ngôn ngữ đơn giản và dễ hiểu
            4. Nếu trích đoạn không đủ thông tin hoặc không có thông tin liên quan về câu hỏi, hãy thừa nhận điều đó một cách trung thực
            5. Nếu bạn có khả năng trả lời câu hỏi hãy thêm {refs_text}
            """

            response = llm.invoke([HumanMessage(content=prompt)])

            # Get content from AIMessage response
            answer = response.content if hasattr(response, 'content') else str(response)

            # Add references if we have content
            if answer and top_docs:
                answer = f"{answer}\n{refs_text}"

            return {"messages": [{"role": "assistant", "content": answer}]}
        except Exception as e:
            print(f"Error in generate_answer_node: {e}")
            return {"messages": [{"role": "assistant", "content": f"Xin lỗi, tôi gặp lỗi khi xử lý câu trả lời: {e}"}]}


    graph_builder = StateGraph(State)

    graph_builder.add_node("user_input", user_input_node)
    graph_builder.add_node("direct_answer", direct_answer_node)
    graph_builder.add_node("refine_query", refine_query_node)
    graph_builder.add_node("semantic_search", semantic_search_node)
    graph_builder.add_node("generate_answer", generate_answer_node)

    graph_builder.set_entry_point("user_input")
    graph_builder.add_conditional_edges(
        "user_input",
        lambda state: state.get("route", "legal_search"),
        {
            "direct_answer": "direct_answer",
            "legal_search": "refine_query"
        }
    )
    graph_builder.add_edge("refine_query", "semantic_search")
    graph_builder.add_edge("semantic_search", "generate_answer")
    graph_builder.add_edge("direct_answer", END)
    graph_builder.add_edge("generate_answer", END)
    graph = graph_builder.compile()

    return graph