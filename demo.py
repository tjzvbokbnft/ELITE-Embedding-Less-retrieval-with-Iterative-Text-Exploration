import time
from pathlib import Path
from src import core_functions, utils            # 你的业务代码
import local_config as cfg                           # <— 统一只这么导入

# ---------- 启动时让用户交互修改配置 ----------
def _prompt_cfg() -> dict:
    """逐项询问配置（回车或输入 default = 使用当前默认值）。"""
    def ask(name, default, cast=int):
        # 在提示里明确告诉用户回车即默认
        raw = input(f"{name} [{default}] (Press 'Enter' to use our default value): ").strip()
        if raw == "" or raw.lower() == "default":
            return default
        return cast(raw) if cast else raw


    return {
        "recall_index":      ask("recall_index",      cfg.recall_index),
        "neighbor_num":      ask("neighbor_num",      cfg.neighbor_num),
        "deep_search_index": ask("deep_search_index", cfg.deep_search_index),
        "deep_search_num":   ask("deep_search_num",   cfg.deep_search_num),
        "voter_num":         ask("voter_num",         cfg.voter_num),
        "num_ctx":           ask("num_ctx",           cfg.num_ctx),
        "common_model":      ask("common_model",      cfg.common_model, cast=str),
    }

# 收集用户输入并写回全局配置
cfg.set_config(**_prompt_cfg())
# ---------- 交互配置完毕 ----------


def read_context():
    """让用户输入小说文件路径，返回文本内容和文件名。"""
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
    """主循环：问答 + 日志。"""
    context, file_name = read_context()
    print(f"\n🧠 已加载文本: {file_name}")
    print("💬 现在可就该文本内容进行提问，输入 'exit' 退出。\n")
    #可以根据不同的内容类型, 调整冷启动问题
    cold_start = [ 
        "What core themes and genres best describe this novel?",
        "What is the central narrative hook or premise introduced early in the story?",
        "How would you describe the author's writing style and tone, based on the opening chapters?",
    ]

    cache_keywords = ""
    memory = ""
    timestamp = int(time.time())
    log_dir = Path(f"DEMO_LOG/{cfg.common_model}+{timestamp}")
    log_dir.mkdir(parents=True, exist_ok=True)

    round_idx = 0
    while True:
        # 拿用户/冷启动问题
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

        # ---- Memory 检索 ----
        if memory:
            resp_mem = core_functions.retrieve_useful(
                text_input=memory,
                query=query,
                cached_keywords=cache_keywords,
            )
            mem_retrieval = resp_mem["retrieve_data"]
            new_keywords += resp_mem["keywords_extracted"]

        # ---- Context 检索 ----
        resp_ctx = core_functions.retrieve_useful(
            text_input=context,
            query=query,
            cached_keywords=cache_keywords,
        )
        ctx_retrieval = resp_ctx["retrieve_data"]
        new_keywords += resp_ctx["keywords_extracted"]

        # ---- 调用模型 ----
        final_input = (
            f"RETRIEVAL FROM CONTEXT:\n{ctx_retrieval}\n\n"
            f"RETRIEVAL FROM MEMORY:\n{mem_retrieval}\n\n"
            f"BASED on the retrievals above, respond to the user's query: {query}"
        )
        answer = core_functions.send(final_input)
        memory += answer

        # ---- 关键词抽取 ----
        mem_keywords = core_functions.send(
            "Context: "
            f"{query}\n"
            "PROMPT: Extract proper keywords/element/entity/location from given context "
            "Output the keywords **ONLY** in the following format: "
            "[\"keyword1\", \"keyword2\", \"keyword3\"]"
        )
        new_keywords += mem_keywords
        cache_keywords += new_keywords

        # ---- 输出 ----
        print(f"\n🤖 Agent:\n{answer.strip()}\n{'=' * 20}")

        # ---- 日志 ----
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
    """把本轮所有信息写到不同日志文件，方便调试。"""
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
