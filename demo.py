import os
import time
from pathlib import Path

from src import core_functions, utils, local_config


def read_context():
    """Interactively ask the user for a text file path and return its content + filename."""
    while True:
        txt_path = input("请输入小说文件路径（或输入 q 退出）：").strip()
        if txt_path.lower() in {"q", "quit", "exit"}:
            raise SystemExit("已退出。")
        path = Path(txt_path)
        if path.is_file():
            try:
                with path.open("r", encoding="utf-8") as f:
                    return f.read(), path.name
            except Exception as err:
                print(f"❌ 读取文件时出错: {err}")
        else:
            print("❌ 找不到文件，请重新输入有效路径。")


def main():
    """Main interactive loop."""
    context, file_name = read_context()

    print(f"\n🧠 已加载文本: {file_name}")
    print("💬 现在可就该文本内容进行提问，输入 'exit' 退出。\n")

    cold_start = [
        "What core themes and genres best describe this novel?",
        "What is the central narrative hook or premise introduced early in the story?",
        "How would you describe the author's writing style and tone, based on the opening chapters?",
    ]

    cache_keywords = ""
    memory = ""
    timestamp = int(time.time())
    log_dir = Path(f"DEMO_LOG/{local_config.common_model}+{timestamp}")
    log_dir.mkdir(parents=True, exist_ok=True)

    round_idx = 0
    while True:
        # Determine user query
        if round_idx < len(cold_start):
            query = cold_start[round_idx]
            print(query)
        else:
            query = input("You: ").strip()
            if query.lower() in {"exit", "quit"}:
                print("👋 Exiting.")
                break

        new_keywords = ""
        mem_retrieval = ""

        # Retrieve from agent memory
        if memory:
            resp_mem = core_functions.retrieve_useful(
                text_input=memory,
                query=query,
                cached_keywords=cache_keywords,
            )
            mem_retrieval = resp_mem["retrieve_data"]
            new_keywords += resp_mem["keywords_extracted"]

        # Retrieve from context
        resp_ctx = core_functions.retrieve_useful(
            text_input=context,
            query=query,
            cached_keywords=cache_keywords,
        )
        ctx_retrieval = resp_ctx["retrieve_data"]
        new_keywords += resp_ctx["keywords_extracted"]

        # Compose final input for the model
        final_input = (
            f"RETRIEVAL FROM CONTEXT:\n{ctx_retrieval}\n\n"
            f"RETRIEVAL FROM MEMORY:\n{mem_retrieval}\n\n"
            f"BASED on the retrievals above, respond to the user's query: {query}"
        )

        answer = core_functions.send(final_input)
        memory += answer

        # Extract keywords from the answer
        mem_keywords = core_functions.send(
            "Context: "
            f"{query}\n"
            "PROMPT: Extract proper keywords/element/entity/location from given context "
            "Output the keywords **ONLY** in the following format: "
            "[\"keyword1\", \"keyword2\", \"keyword3\"]"
        )
        new_keywords += mem_keywords
        cache_keywords += new_keywords

        # Display answer
        print(f"\n🤖 Agent:\n{answer.strip()}\n{'=' * 20}")

        # Logging
        _write_logs(
            round_idx,
            log_dir,
            query,
            answer,
            ctx_retrieval,
            mem_retrieval,
            new_keywords,
        )

        round_idx += 1


def _write_logs(round_idx, log_dir, query, answer, ctx_retrieval, mem_retrieval, new_keywords):
    """Helper function to write logs in a consistent manner."""
    _append(log_dir / "agent_mem.txt", round_idx, query, "🧠 Agent Memory (new):", answer)
    _append(log_dir / "context_retrieval_log.txt", round_idx, query, "🤖 Context retrieval:", ctx_retrieval)
    _append(log_dir / "mem_retrieval_log.txt", round_idx, query, "🤖 Memory retrieval:", mem_retrieval)
    _append(log_dir / "keywords_cached.txt", round_idx, query, "🤖 Keywords cached:", new_keywords)


def _append(path: Path, round_idx: int, user_query: str, header: str, body: str):
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n==== Round {round_idx} ====\n")
        f.write(f"🧍‍♂️ User: {user_query}\n")
        f.write(f"{header}\n{body.strip()}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting by user interruption.")
