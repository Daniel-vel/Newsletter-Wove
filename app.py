import streamlit as st
import os
import requests
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# 1. Stop CrewAI from phoning home (prevents cloud freezing)
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_DISABLE_TRACING"] = "true"

# 2. THE OVERRIDE: Force Streamlit Secrets directly into the OS environment
try:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    os.environ["FIRECRAWL_API_KEY"] = st.secrets["FIRECRAWL_API_KEY"]
except KeyError:
    st.error("Missing API Keys! Please ensure your keys are saved in Streamlit Advanced Settings -> Secrets.")
    st.stop()

# 3. Create a Custom, Bug-Free Firecrawl Tool to bypass crewai_tools
@tool("Firecrawl Web Search")
def safe_firecrawl_search(query: str) -> str:
    """Use this tool to search the web for the latest news, features, and pricing of wealthtech platforms."""
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {os.environ.get('FIRECRAWL_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {"query": query}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response.text
    except Exception as e:
        return f"Search failed: {str(e)}"

# 4. Set up the Streamlit User Interface
st.set_page_config(page_title="Wove Competitive Intelligence", page_icon="📊", layout="centered")
st.title("Wove Benchmarking & AI Newsletter Agent")
st.markdown("Generates a weekly strategic newsletter comparing BNY's Wove against legacy banks and modern fintechs.")

# 5. The Button that triggers the agents
if st.button("Generate Weekly Newsletter", type="primary"):

    with st.status("Initializing AI Agents...", expanded=True) as status_box:
        
        # --- TERMINAL DIAGNOSTIC CHECKPOINTS ---
        print("📍 Checkpoint 1: Connecting to Anthropic...", flush=True)
        my_llm = LLM(model="anthropic/claude-sonnet-4-5")

        print("📍 Checkpoint 2: Waking up the Market Researcher...", flush=True)
        st.write("🕵️‍♂️ Waking up the Market Researcher...")
        researcher = Agent(
            role="Senior Financial Technology Researcher",
            goal="Gather the latest updates from the past 30 days regarding BNY Pershing's Wove, legacy wealth tools, and modern fintechs.",
            backstory="You are an expert at finding hidden insights about wealthtech platforms like Wove, Orion, and Altruist.",
            tools=[safe_firecrawl_search],
            llm=my_llm,
            verbose=True
        )

        print("📍 Checkpoint 3: Waking up the Benchmarking Analyst...", flush=True)
        st.write("📊 Waking up the Benchmarking Analyst...")
        analyst = Agent(
            role="Strategic Wealth Management Consultant",
            goal="Compare Wove against legacy banks and nimble fintechs, assessing cost-effectiveness and capability gaps.",
            backstory="You specialize in digital transformation for financial services, often consulting for firms like Infosys.",
            llm=my_llm,
            verbose=True
        )

        print("📍 Checkpoint 4: Waking up the AI Strategist...", flush=True)
        st.write("🤖 Waking up the AI Innovation Strategist...")
        strategist = Agent(
            role="AI Architect for Financial Services",
            goal="Identify current AI breakthroughs and explain exactly how they can be applied to Wove to automate advisor workflows.",
            backstory="You understand both the technical mechanics of agentic AI and how it drives business value in wealth management.",
            tools=[safe_firecrawl_search],
            llm=my_llm,
            verbose=True
        )

        print("📍 Checkpoint 5: Waking up the Editor...", flush=True)
        st.write("✍️ Waking up the Managing Editor...")
        editor = Agent(
            role="Managing Director at Infosys",
            goal="Synthesize the research, benchmarking, and AI strategies into a crisp, highly readable weekly newsletter.",
            backstory="You write executive-level newsletters. You use clear headings, bullet points, and a professional yet engaging tone tailored for consultants.",
            llm=my_llm,
            verbose=True
        )

        print("📍 Checkpoint 6: Defining Tasks...", flush=True)
        task_research = Task(
            description="Use Firecrawl to search the web for the latest 30-day news on BNY's Wove platform, legacy competitors (Envestnet, Orion), and fintechs (Altruist, Betterment).",
            expected_output="A summary of the latest features, API integrations, and pricing models in the wealthtech space.",
            agent=researcher
        )

        task_analysis = Task(
            description="Create a benchmarking report comparing Wove vs. legacy banks (strengths/opportunities) and Wove vs. fintechs (cost-effectiveness/capabilities).",
            expected_output="A structured benchmarking analysis with actionable strategic insights for Wove.",
            agent=analyst
        )

        task_ai = Task(
            description="Use Firecrawl to research recent AI breakthroughs (like agentic workflows) and detail how Wove could integrate them.",
            expected_output="A strategic section linking specific AI breakthroughs to Wove's architecture.",
            agent=strategist
        )

        task_write = Task(
            description="Compile the outputs of the previous tasks into a weekly newsletter. The newsletter must have sections for Traditional Benchmarking, Innovative Benchmarking, and AI Breakthroughs. Sign the newsletter with the name Daniel Velázquez Marván.",
            expected_output="A final, formatted Markdown newsletter ready for publication.",
            agent=editor
        )

        print("📍 Checkpoint 7: Assembling Crew and Kickoff!", flush=True)
        st.write("🚀 Kickoff! Agents are now researching and writing...")
        newsletter_crew = Crew(
            agents=[researcher, analyst, strategist, editor],
            tasks=[task_research, task_analysis, task_ai, task_write],
            process=Process.sequential,
            verbose=True
        )

        # Run the workflow
        final_newsletter = newsletter_crew.kickoff()
        
        print("📍 Checkpoint 8: Success!", flush=True)
        status_box.update(label="Newsletter Generated Successfully!", state="complete", expanded=False)

    # 6. Display the final result
    st.success("Draft Complete")
    st.markdown("---")
    st.markdown(final_newsletter.raw)
