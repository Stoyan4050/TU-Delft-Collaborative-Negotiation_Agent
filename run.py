import json
import os

from utils.plot_trace import plot_trace
from utils.runners import run_session

# create results directory if it does not exist
if not os.path.exists("results"):
    os.mkdir("results")

# Settings to run a negotiation session:
#   We need to specify the classpath of 2 agents to start a negotiation.
#   We need to specify the preference profiles for both agents. The first profile will be assigned to the first agent.
#   We need to specify a deadline of amount of rounds we can negotiate before we end without agreement
settings = {
    "agents": [
        "agents.template_agent.agent_gosho_ascended.AgentGosho",
        "agents.template_agent.agent_gosho_ascended.AgentGosho",
        # "agents.template_agent.agent_gosho.AgentGosho",
        # "agents.template_agent.agent_bat_gosho.AgentBatGosho",
    ],
    "profiles": ["domains/domain00/profileA.json", "domains/domain00/profileB.json"],
    "deadline_rounds": 200,
}

# run a session and obtain results in dictionaries
results_trace, results_summary = run_session(settings)

# plot trace to html file
plot_trace(results_trace, "results/trace_plot.html")

# write results to file
with open("results/results_trace.json", "w") as f:
    f.write(json.dumps(results_trace, indent=2))
with open("results/results_summary.json", "w") as f:
    f.write(json.dumps(results_summary, indent=2))
