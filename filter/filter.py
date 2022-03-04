import json

json_files = [
            'results/results_summaries.json',
            #'results/initial.json',
            #'results/initial1.json',
            #'results/marko1.json',
            #'results/nov1.json',
            #'results/nov2.json',
        ]

data = []
for json_file_name in json_files:
    with open(json_file_name) as json_file:
        data = data + json.load(json_file)
        json_file.close()

print(data)
# first only get results relevant for agent gosho

no_offer_accepted = 0
relevant_negotiation_results = []
for negotiation_result in data:
    for key, value in negotiation_result.items():
        if key.startswith('agent_') and value == 'AgentGoshoAscended':
            relevant_negotiation_results.append(negotiation_result)
            if negotiation_result['result'] != 'agreement':
                no_offer_accepted += 1
            break

print(no_offer_accepted)
print(data == relevant_negotiation_results)

relevant_negotiation_results_agents_parsed = []

for relevant_negotiation_result in relevant_negotiation_results:
    agent = 0
    utility = 0
    entry = {}
    for key, value in relevant_negotiation_result.items():
        if key.startswith('agent_') and agent == 0:
            entry["agent_1"] = value
            agent += 1
        elif key.startswith('agent_') and agent == 1:
            entry["agent_2"] = value
        elif key.startswith("utility_") and utility == 0:
            entry["utility_1"] = value
            utility += 1
        elif key.startswith("utility_") and utility == 1:
            entry["utility_2"] = value
        else:
            entry[key] = value
    relevant_negotiation_results_agents_parsed.append(entry)

print(relevant_negotiation_results_agents_parsed)

with open('results/results_filtered.json', 'w') as outfile:
    json.dump(relevant_negotiation_results_agents_parsed, outfile)
    outfile.close()
