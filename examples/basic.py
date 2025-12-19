"""Basic example showing how to instantiate and run the KG-Agent skeleton."""

from kg_agent import Agent, ToolBox, KGExecutor, KGQueryTool, FinalAnswerTool


def main() -> None:
    # Create components
    kg = KGExecutor()
    # Load toy triples
    kg.load_triples([
        ("Alice", "knows", "Bob"),
        ("Bob", "works_at", "CompanyX"),
        ("CompanyX", "located_in", "CityZ"),
    ])

    toolbox = ToolBox()
    # register basic tools
    toolbox.register("kg_query", KGQueryTool(kg))
    toolbox.register("final_answer", FinalAnswerTool(llm=None))

    agent = Agent(llm=None, toolbox=toolbox, kg_executor=kg)

    # Run agent on a simple query
    res = agent.run("Where does Alice's colleague work and where is it located?")
    print("Agent result:", res)


if __name__ == "__main__":
    main()
