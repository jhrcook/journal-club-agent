# AI Agent for Journal Club

## Planning

Agent:

- give key paper to be reviewed
  - PDF, URL (to be downloaded), or HTML
- optional other papers to include in research (along with others found)
  - URL/HTML/PDF that the user wants the agent to use
  - additional papers on similar topics or included in the citations
    - if not open access, can request that the user download them, otherwise will use what is available (usually an abstract)
- specific prompt for a scientist preparing for a journal club
- looks at authors other work (first 3 and last 2 authors by default, but allow to be configurable)
- specifically search google scholar, ncbi, nature, cell, etc.
- additional research on citations:
  - look at papers cited by the key paper
  - looks at those that cited the key paper
- look at lab websites
- intelligently read through a paper:
  - start with abstract
  - then introduction
    - pause to build some background based on the introduction
- organize results, figures, and captions to be interpreted together
  - take the figure, its caption, and relevant section from the results
  - organize into chunks to be interpreted one at a time, passing the summary and key points from one to the next
  - specific prompts of the results (as individual units and as a full story)
- extract specifics from conclusion/discussion:
  - key findings
  - influence on field
  - limitations of the study
  - next steps
  - (option to add in more prompts)
- retain state or summarize findings so can be asked follow up questions

UI:

- CLI with basic inputs and outputs to prepare for JC
  - ability to enter interactive mode for follow-up
- output a markdown report (can convert to HTML)
- GUI for DeepAgents with LangGraph: <https://github.com/langchain-ai/deep-agents-ui>

Other feature ideas:

- mode to be turned on during journal club so follow up queries can be addressed
  - prioritize speed and concise responses

## To-do

1. Review the "Deep Research" example: <https://github.com/langchain-ai/deepagents/tree/main/examples/deep_research>
2. Describe the MVP
3. Develop the MVP

### MVP

Input:

- URL or HTML
- output directory

Features:

- researches authors
- summarizes abstract and introduction for key context
- collects additional citations to look further into
- reads results and summarizes key findings (pointing to locations in figures)
- analyzes conclusion

Outputs:

- persistent memory (as context for future agents)
- markdown/HTML report

**Not** included in the MVP:

- visual parsing of figures

### PDF Parsing

GROBID: <https://grobid.readthedocs.io/en/latest/getting_started/>

- "industry standard" for parsing research papers
- recommended to run via docker

Docling: <https://docling-project.github.io/docling/>

- ML models
- specifically made for scientific papers
- newer library

PyMuPDF: <https://pymupdf.readthedocs.io/en/latest/index.html>

- more hands-on
- no simple "convert to markdown" option

**Decision:** Start with 'Docling' and potentially try PyMuPDF if more control is required

## Paper parsing

Possible inputs:

- URL to an open access paper
- HTML file for a closed access paper
- PDF

These can be provided for the main paper and for supplementary papers to use for background.
For example, there may be papers that should be used but are not available for free online.

<https://www.jbc.org/article/S0021-9258(20)39070-0/fulltext>
