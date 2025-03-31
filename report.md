# RAG-Based Web Insights Generator using FLAN-T5

## Approach  
This project implements a Retrieval-Augmented Generation (RAG) system to extract, categorize, and summarize website content for task-specific use cases such as lead generation or business intelligence. The system follows a three-stage architecture:  
1. **Scraping & Storage:** Extracts raw HTML and structured content using `BeautifulSoup` and optionally Selenium.  
2. **Preprocessing & Categorization (LLM1):** Uses `google/flan-t5-large` to convert unstructured content into well-labeled sections (e.g., About, Services, Call to Action).  
3. **Task-Specific Querying (LLM2):** Generates structured insights by querying the categorized content using the same FLAN-T5 model.  

## Model Selection  
We selected `google/flan-t5-large` for both categorization and insight generation due to its strong zero/few-shot learning capabilities and effectiveness on instruction-following tasks. The model consistently outperforms others in its class across a broad set of NLP benchmarks, making it suitable for flexible and modular RAG pipelines.

## Data Preprocessing  
- **Boilerplate removal:** Eliminates repetitive web elements like menus and footers.  
- **Deduplication:** Ensures unique and relevant textual content is passed to the model.  
- **Domain typing:** Users specify a domain type (e.g., SaaS, e-commerce), which influences the prompt format for LLM1.  
- **Structured Prompting:** Extracted text is reformatted into a prompt-friendly structure to enhance LLM1 and LLM2 output quality.

## Performance Evaluation  
Performance is evaluated qualitatively on real domain samples:
- **Categorization accuracy:** Evaluates whether LLM1 correctly segments content into labeled sections.  
- **Insight relevance:** Checks if LLM2 produces actionable and coherent summaries.  
- **Latency:** Maintains real-time usability (< 2 seconds/model call using `transformers` pipeline).  

Future work may involve adding automated evaluation metrics such as ROUGE, BLEU, or GPT-based scoring for summarization fidelity.

## Rationale  
This architecture emphasizes modularity, reuse, and adaptability. By using `flan-t5-large` for both steps and incorporating typed domain guidance, the system scales to new use cases with minimal changes while keeping inference costs manageable.

---

**Citation**  
Chung, H., Hou, L., Longpre, S., Zoph, B., Tay, Y., Fedus, W., Li, E., Wang, X., Dehghani, M., Brahma, S., Webson, A., Gu, S. S., Dai, Z., Suzgun, M., Chen, X., Chowdhery, A., Narang, S., Mishra, G., Yu, A., Zhao, V., Huang, Y., Dai, A., Yu, H., Petrov, S., Chi, E. H., Dean, J., Devlin, J., Roberts, A., Zhou, D., Le, Q. V., & Wei, J. (2022). *Scaling Instruction-Finetuned Language Models*. arXiv. https://doi.org/10.48550/arxiv.2210.11416
