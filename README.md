<p align="center">
  <a href="https://arxiv.org/abs/2505.11908">
    <img src="https://img.shields.io/badge/arXiv-2505.11908-b31b1b.svg?style=flat-square" alt="arXiv">
  </a>
</p>



# ELITE: Embedding-Less retrieval with Iterative Text Exploration

Large Language Models (LLMs) have achieved impressive progress in natural language processing, but their limited ability to retain long-term context constrains performance on document-level or multi-turn tasks. Retrieval-Augmented Generation (RAG) mitigates this by retrieving relevant information from an external corpus. However, existing RAG systems often rely on embedding-based retrieval trained on corpus-level semantic similarity, which can lead to retrieving content that is semantically similar in form but misaligned with the question's true intent. Furthermore, recent RAG variants construct graph- or hierarchy-based structures to improve retrieval accuracy, resulting in significant computation and storage overhead. In this paper, we propose an embedding-free retrieval framework. Our method leverages the logical inferencing ability of LLMs in retrieval using iterative search space refinement guided by our novel importance measure and extend our retrieval results with logically related information without explicit graph construction. Experiments on long-context QA benchmarks, including NovelQA and Marathon, show that our approach outperforms strong baselines while reducing storage and runtime by over an order of magnitude. 

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [🔧 Installation & Quick Start](#-installation--quick-start)
- [Framework](#Framework)
- [Performance Analysis](#Performance-Analysis)
- [📄 How to Get Results on NovelQA and Marathon](#-how-to-get-results-on-novelqa-and-marathon)


## Features

- **Embedding-Free Retrieval**: Eliminates the reliance on embedding models and dense retrievers.

- **Fast Response & Deployment**: Minimal offline preparation and indexing time enables fast responses and rapid deployment.

- **Lightweight Reasoning**: Utilizes LLMs’ native lexical and reasoning abilities—no need to construct graph or tree databases.

- **Strong Performance**: Outperforms baselines on long-context QA benchmarks such as NovelQA and Marathon.

## Project Structure

- `src/`: Core implementation of the embedding-free RAG framework.
- `reproduce/`: Scripts for reproducing experiments.
- `demo.py`: A runnable demo to test the pipeline.
- `requirements.txt`: List of dependencies.
- `.gitignore`: Standard ignored files.
- `Readme.md`: Project documentation.

## 🔧 Installation & Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/tjzvbokbnft/ELITE-Embedding-Less-retrieval-with-Iterative-Text-Exploration.git
cd ELITE-Embedding-Less-retrieval-with-Iterative-Text-Exploration
# 创建并激活环境
conda create -n ELITE python=3.11 -y
conda activate ELITE
# 安装依赖
pip install -r requirements.txt
```

```bash
#string_noise --> optional (To use this package, you must manually add it to your site-packages directory.
#If you don't need it, simply delete the related code. -->using without the importance metric)

#play with demo
#config your txt path in demo.py
#config other parameters in scr/local_config.py

python demo.py

# Reproduce on NovelQA benchmark
python reproduce/test_novelQA.py

# Reproduce on Marathon benchmark
python reproduce/test_marathon.py
```
```bash
# 全默认（含默认小说路径）
python cli_agent.py
# 只改模型名与邻居数
python cli_agent.py --common_model llama3.1:latest --neighbor_num 2
# 覆盖全部超参 & 指定小说
python cli_agent.py \
  --novel nvQA/Frankenstein.txt \
  --recall_index 6 \
  --neighbor_num 15 \
  --deep_search_index 4 \
  --deep_search_num 25 \
  --voter_num 5 \
  --num_ctx 10000 \
  --common_model llama3.1:latest
```
### 2.Basic Usages



## Framework
![framework](framework/framework1.png)
## Performance Analysis

### QA Retrieval Accuracy
![QA Retrieval Accuracy](performance/ret.png)

### Average Query Time by Context Length and Query Volume
![Average Query Time](performance/time3d.png)

### Total Time Consumption by Context Length
![Total Time Consumption](performance/Total%20time.jpg)


## 📄 How to Get Results on NovelQA and Marathon

### 📊 Benchmark & Evaluation

To evaluate the performance of this framework on **NovelQA** and **Marathon**, please follow the official benchmarking instructions:

#### 📘 NovelQA
- [GitHub Repository](https://github.com/NovelQA/novelqa.github.io)
- [Official leaderboard](https://novelqa.github.io/)
  

#### 🏃 Marathon
- [GitHub Repository](https://github.com/Hambaobao/Marathon)
- [Submission](https://openbenchmark.online/marathon/)

## License
- MIT 
  
## Citation

If **ELITE** assists in your research, please cite us:

```bibtex
@misc{wang2025elite,
  title     = {ELITE: Embedding-Less Retrieval with Iterative Text Exploration},
  author    = {Wang, Zhangyu and Gao, Siyuan and Zhou, Rong and Wang, Hao and Ning, Li},
  year      = {2025},
  eprint    = {2505.11908},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url       = {https://arxiv.org/abs/2505.11908}
}


