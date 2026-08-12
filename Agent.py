import os
from datetime import date
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools.Search_tool import web_search, reset_search_count

load_dotenv()

SYSTEM_PROMPT = """You are an autonomous research analyst.

Your job: given a research topic, you must:
1. Break the topic into 3-5 sub-questions that together give a complete picture.
2. Use the web_search tool to investigate each sub-question with different, specific queries.
3. Cross-check facts across sources when possible. Note disagreements if you find them.
4. Synthesize everything into a well-organized, cited research report.

STRICT RULE: You must call web_search NO MORE than 5 times total, no matter how the
topic looks. After your 5th search (or sooner, if you already have enough to cover the
sub-questions), STOP calling tools entirely and write the final Markdown report using
only what you've already found. Do not search "just to be safe" — treat 5 searches as
a hard budget, not a target.
"""

REPORT_PROMPT = """Using everything you found during your research on the topic below,
write a complete report in clean, well-formatted Markdown following this structure
EXACTLY:

# {topic}

*Report date: {today}*

## Executive Summary
(3-5 sentences, the key takeaway)

## Key Findings
(bulleted list; **bold** the most important facts, numbers, or names in each bullet)

## Detailed Analysis
(2-4 `###` subsections covering different angles you researched — give each a clear,
specific heading, not generic labels like "Analysis 1")

## Sources
(numbered list, each formatted as a Markdown link: `1. [Source Title](URL)` — never
paste a bare URL)

Formatting rules:
- Use `**bold**` for key facts/figures, not for whole sentences
- Never put the report date at the bottom — it belongs only in the byline under the title
- Keep paragraphs short (3-5 sentences max) and use bullets where a list is clearer than prose
- Do not include a "Report date:" line anywhere except the byline under the title
"""


def build_agent():
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)

    tools = [web_search]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=8,              # hard cap: ~5 searches + reasoning steps
        max_execution_time=120,        # seconds — safety net against runaway loops
        handle_parsing_errors=True,
    )
    return executor


def run_research(topic: str) -> str:
    reset_search_count()
    executor = build_agent()

    instructions = (
        f"Research this topic thoroughly: {topic}\n\n"
        "You have a maximum of 5 web_search calls. Use them on distinct, specific "
        "queries covering different sub-questions. Once you've used your searches "
        "(or you already have enough information), stop searching immediately.\n\n"
        "Then write the final report in this exact format:\n\n"
        + REPORT_PROMPT.format(topic=topic, today=date.today().isoformat())
    )

    result = executor.invoke({"input": instructions})
    return result["output"]