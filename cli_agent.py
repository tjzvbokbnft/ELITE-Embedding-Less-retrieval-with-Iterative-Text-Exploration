#!/usr/bin/env python
# coding: utf-8
"""
cli_agent.py — 终端直接跑的版本
用法示例（覆盖部分参数）：
    python cli_agent.py \
        --novel nvQA/Frankenstein.txt \
        --recall_index 8 \
        --neighbor_num 20 \
        --common_model gpt-4o

不传任何参数即全部走默认值。
"""

import argparse
import time
from pathlib import Path

from src import core_functions, utils          # 你的业务代码
import local_config as cfg                     # 统一只这么导入


# ---------- CLI 参数 ----------
def parse_cli() -> dict:
    p = argparse.ArgumentParser(
        description="Run the Q&A agent over a novel with optional hyper-parameters."
    )
    # 通用超参
    p.add_argument("--recall_index",      type=int, help=f"default={cfg.recall_index}")
    p.add_argument("--neighbor_num",      type=int, help=f"default={cfg.neighbor_num}")
    p.add_argument("--deep_search_index", type=int, help=f"default={cfg.deep_search_index}")
    p.add_argument("--deep_search_num",   type=int, help=f"default={cfg.deep_search_num}")
    p.add_argument("--voter_num",         type=int, help=f"default={cfg.voter_num}")
    p.add_argument("--num_ctx",           type=int, help=f"default={cfg.num_ctx}")
    p.add_argument("--common_model",      type=str, help=f"default='{cfg.common_model}'")

    # 小说文件
    p.add_argument(
        "--novel",
        type=str,
        help="Path to novel text file (default=nvQA/Frankenstein.txt).",
        default="nvQA/Frankenstein.txt",
    )

    # True/False 接口，举例
    # p.add_argument("--dry_run", action="store_true", help="Don't call LLM, debug only")

    args = p.parse_args()

    # 把 None 的字段剔掉，只覆盖用户显式传入的
    overrides = {k: v for k, v in vars(args).items() if v is not None}
    return overrides


# ---------- 主逻辑 ----------
def _write_logs(round_idx, log_dir, query, answer, ctx_retrieval, mem_retrieval, new_keywords):
    def _append(path: Path, header: str, body: str):
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n\n==== Round {round_idx} ====\n")
            f.write(f"🧍‍♂️ User: {query}\n")
            f.write(f"{header}\n{body.strip()}\n")

    _append(log_dir / "agent_mem.txt", "🧠 Agent Memory (new):", answer)
    _append(log_dir / "context_retrieval_log.txt", "🤖 Context retrieval:", ctx_retrieval)
    _append(log_dir / "mem_retrieval_log.txt", "🤖 Memory retrieval:", mem_retrieval)
    _append(log_dir / "keywords_cached.txt", "🤖 Keywords cached:", new_keywords)


def main():
    # 1. 解析 CLI 并覆盖配置
    cli_kwargs = parse_cli()
    novel_path = Path(cli_kwargs.pop("novel", "nvQA/Frankenstein.txt"))
    cfg.set_config(**cli_kwargs)  # 只更新传入的项

    # 2. 读取小说
    if not novel_path.is_file():
        raise FileNotFoundError(f"❌ Novel file not found: {novel_path}")
    context = novel_path.read_text(encoding="utf-8")
    print(f"🧠 已加载文本: {novel_path}")
    print("💬 输入问题（exit 退出）")

    # 3. 冷启动
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

    # 4. 主循环
    while True:
        query = (
            cold_start[round_idx] if round_idx < len(cold_start)
            else input("You: ").strip()
        )
        if query.lower() in {"exit", "quit"}:
            print("👋 Exiting.")
            break

        mem_retrieval = ""
        new_keywords = ""

        # Memory 检索
        if memory:
            resp_mem = core_functions.retrieve_useful(
                text_input=memory,
                query=query,
                cached_keywords=cache_keywords,
            )
            mem_retrieval = resp_mem["retrieve_data"]
            new_keywords += resp_mem["keywords_extracted"]

        # Context 检索
        resp_ctx = core_functions.retrieve_useful(
            text_input=context,
            query=query,
            cached_keywords=cache_keywords,
        )
        ctx_retrieval = resp_ctx["retrieve_data"]
        new_keywords += resp_ctx["keywords_extracted"]

        # 调 LLM
        final_input = (
            f"RETRIEVAL FROM CONTEXT:\n{ctx_retrieval}\n\n"
            f"RETRIEVAL FROM MEMORY:\n{mem_retrieval}\n\n"
            f"BASED on the retrievals above, respond to the user's query: {query}"
        )
        answer = core_functions.send(final_input)
        memory += answer

        # 关键词抽取
        mem_keywords = core_functions.send(
            "Context: "
            f"{query}\n"
            "PROMPT: Extract proper keywords/element/entity/location from given context "
            "Output the keywords **ONLY** in the following format: "
            "[\"keyword1\", \"keyword2\", \"keyword3\"]"
        )
        new_keywords += mem_keywords
        cache_keywords += new_keywords

        # 输出 & 日志
        print(f"\n🤖 Agent:\n{answer.strip()}\n{'=' * 20}")
        _write_logs(
            round_idx, log_dir, query, answer, ctx_retrieval, mem_retrieval, new_keywords
        )
        round_idx += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting by user interruption.")
