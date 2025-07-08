"""
中央配置文件——项目里所有其它模块一律:
    import local_config as cfg
然后通过 cfg.xxx 读取，或 cfg.set_config(...) 修改。

改动后会自动把依赖它的派生路径重新计算，避免手动同步。
"""

# ========= 基础参数（默认值） =========
recall_index      = 25
neighbor_num      = 2
deep_search_index = 5
deep_search_num   = 10
voter_num         = 10
num_ctx           = 21145
common_model      = "llama3.1:latest"

# ========= 其它固定参数 =========
# ollama
url = "http://localhost:11434/api/generate"
embedder_config = {
    "model": "nomic-embed-text",
    "ollama_base_url": "http://localhost:11434"
}

# novelqa / marathon 数据集
dataset           = "marathon"          # 可改成 novelQA、longbench-v2 等
novelQAtxtdir     = "nvQA/book/PublicDomain"
novelQAjsondir    = "nvQA/data/PublicDomain"
novelQAansdir     = "nvQA/0_questions_with_correct_answer/CorrectAnswers/res_mc.json"
longBenchjsondir  = "newData/LongBench_v2.json"
marathonjsondir   = "newData/marathon.json"

# 停用词集合（保持原样）
literary_stopwords ={
    "the","is","am","are","was","were","be","been","being","he","she","it","they",
    "a","an","to","of","for","in","on","with","at","by","and","but","or","so","if","that",
    "this","those","these","i","you","me","we","us","them","there","then","what","which",
    "as","from","up","down","out","over","under","again","further","about","above","below",
    "between","into","through","during","before","after","right","left","just","their",
    'did', 'doing', 'do', 'never', 'yes', '[', ']', 'how', 'many', 'times', 'that', 'the', 'author', 
    'mentioned', 'implication', 'metaphor', 'described', 'have', 'symbol', "'", '*', '.', ',', '?', 
    "''", 'in', '``', 'so', 'there', 'are', 'and', "'s", 'has', 'this', 'happened', 'being', 'novel', 
    'plot', '**', '***', 'was', 'be', 'being', 'is', 'were', 'i', 'but', 'for', 'my', '(', 'which', 
    'past', 'its', 'it', 'had', 'from', 'with', ')', 'of', 'to', 'a','once','1','2','3','4',':', 'now', 'you','me',
    'into','emun',"his","him","her","someone","who","said","few","three","yes","no",'himself',"where","not","all","hundred",
    "would","when",
}
from datetime import datetime
_run_stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
# ========= 依据基础参数生成的派生路径 =========
def _recompute_paths() -> None:
    """根据当前基础参数计算派生路径变量。"""
    global matching_method, history_folder, res_mc_dir, log_directory, output_folder

    matching_method  = (
        f"{voter_num}voters+cot+2x{neighbor_num}neighbours+"
        f"deep_search{deep_search_num}+CTX_{num_ctx}"
    )
    history_folder   = f"REPRODUCE_LOGS/{common_model}+{matching_method}@{recall_index}_{_run_stamp}"
    res_mc_dir       = f"{history_folder}/res_mc"
    log_directory    = f"{history_folder}/logs"
    output_folder    = f"{history_folder}/Test_results"

# 首次导入先计算一次
_recompute_paths()

# ========= 动态更新接口 =========
def set_config(**kwargs) -> None:
    """
    运行时动态修改配置项。
    用法示例:
        import local_config as cfg
        cfg.set_config(recall_index=30, neighbor_num=4, common_model="qwen2:latest")
    """
    for k, v in kwargs.items():
        if k not in globals():
            raise KeyError(f"未知配置项: {k}")
        globals()[k] = v
    _recompute_paths()         # 自动刷新派生路径
