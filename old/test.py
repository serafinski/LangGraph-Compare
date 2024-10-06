import re
import networkx as nx
import matplotlib.pyplot as plt
import json


class ChainLogParser:
    def __init__(self, file_path, debugMode=False):
        # Debug mode
        self.debugMode = debugMode
        # Directed graph to store edges and nodes
        self.graph = nx.DiGraph()
        # Stack to track chain hierarchy
        self.node_stack = ["__start__"]
        # Variable to hold JSON blocks
        self.current_json_block = []
        # Variable to track if we're inside a JSON block
        self.inside_json_block = False
        # Variable to track pending end node
        self.pending_end_node = None
        # File path
        self.file_path = file_path
        # Initialize the graph with the start node
        self.graph.add_node("__start__")
        # Start parsing
        self._parse_log_file()

    def _parse_log_file(self):
        # Open and read the file
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Process each line
        for line in lines:
            self._process_line(line.rstrip('\n'))

        # At the end, check if stack only contains '__start__' or 'chatbot'
        if len(self.node_stack) == 1:
            last_node = self.node_stack[-1]
            self.graph.add_node("__end__")
            self.graph.add_edge(last_node, "__end__", label="End of Execution")
            if self.debugMode:
                print(f"Added final node: __end__ connected from {last_node}")
        else:
            if self.debugMode:
                print("Warning: node stack is not empty at end of parsing.")
                print(f"Remaining stack: {self.node_stack}")

    def _process_line(self, line):
        # Debug
        if self.debugMode:
            print(f"Processing line: {line}")

        # Detect the start of a JSON block
        if line.strip() == "{":
            self.inside_json_block = True
            self.current_json_block = [line]
            return

        # If inside a JSON block
        if self.inside_json_block:
            self.current_json_block.append(line)
            # Check for matching braces
            json_text = "\n".join(self.current_json_block)
            if json_text.count("{") == json_text.count("}"):
                self._process_json_block()
            return

        # Regex patterns for chain and LLM starts and ends
        chain_start_match = re.match(
            r'.*\[chain/start\]\s*\[(.*?)\]\s*Entering Chain run with input:', line)
        chain_end_match = re.match(
            r'.*\[chain/end\]\s*\[(.*?)\]\s*\[.*\]\s*Exiting Chain run with output:', line)
        llm_start_match = re.match(
            r'.*\[llm/start\]\s*\[(.*?)\]\s*Entering LLM run with input:', line)
        llm_end_match = re.match(
            r'.*\[llm/end\]\s*\[(.*?)\]\s*\[.*\]\s*Exiting LLM run with output:', line)

        # Chain start
        if chain_start_match:
            chain_path = chain_start_match.group(1)
            chain_names = chain_path.split(' > ')
            chain_name = chain_names[-1].split(':')[-1]
            if self.debugMode:
                print(f"Chain start detected: {chain_name}")
            parent_node = self.node_stack[-1]
            # Skip adding LangGraph and __start__ nodes
            if chain_name not in ['LangGraph', '__start__']:
                self.graph.add_node(chain_name)
                self.graph.add_edge(parent_node, chain_name)
                self.node_stack.append(chain_name)
            else:
                # Still need to push it onto the stack
                self.node_stack.append(chain_name)
            return

        # Chain end
        if chain_end_match:
            chain_path = chain_end_match.group(1)
            chain_names = chain_path.split(' > ')
            chain_name = chain_names[-1].split(':')[-1]
            if self.debugMode:
                print(f"Chain end detected: {chain_name}")
            # Defer popping until after processing JSON block
            self.pending_end_node = chain_name
            return

        # LLM start
        if llm_start_match:
            chain_path = llm_start_match.group(1)
            chain_names = chain_path.split(' > ')
            llm_name = chain_names[-1].split(':')[-1]
            if self.debugMode:
                print(f"LLM start detected: {llm_name}")
            parent_node = self.node_stack[-1]
            # Add bidirectional edges between parent_node and llm_name
            self.graph.add_node(llm_name)
            self.graph.add_edge(parent_node, llm_name)
            self.graph.add_edge(llm_name, parent_node)
            self.node_stack.append(llm_name)
            return

        # LLM end
        if llm_end_match:
            chain_path = llm_end_match.group(1)
            chain_names = chain_path.split(' > ')
            llm_name = chain_names[-1].split(':')[-1]
            if self.debugMode:
                print(f"LLM end detected: {llm_name}")
            # Defer popping until after processing JSON block
            self.pending_end_node = llm_name
            return

        # At the end of processing, check if we need to pop a pending end node
        if self.pending_end_node and not self.inside_json_block:
            if self.node_stack and self.node_stack[-1] == self.pending_end_node:
                self.node_stack.pop()
                self.pending_end_node = None
            else:
                if self.debugMode:
                    print(f"End node mismatch: expected {self.node_stack[-1]} but got {self.pending_end_node}")
                self.pending_end_node = None

    def _process_json_block(self):
        json_data = "\n".join(self.current_json_block)
        if self.debugMode:
            print(f"Processing JSON block: {json_data}")
        try:
            parsed_json = json.loads(json_data)
            current_node = self.node_stack[-1]
            parent_node = self.node_stack[-2] if len(self.node_stack) >= 2 else '__start__'

            if 'messages' in parsed_json:
                input_text = parsed_json['messages'][0][1]  # User input
                # Add edge from __start__ to chatbot
                if parent_node == '__start__' and current_node == '__start__':
                    self.graph.add_node('chatbot')
                    self.graph.add_edge('__start__', 'chatbot', label=f"user: {input_text}")
                    # Update the node stack
                    self.node_stack.pop()
                    self.node_stack.append('chatbot')
                else:
                    self.graph.add_edge(parent_node, current_node, label=f"user: {input_text}")
            elif 'generations' in parsed_json:
                output_text = parsed_json['generations'][0][0]['text']  # LLM output
                # Edge from LLM to chatbot with output
                if parent_node != '__start__':
                    self.graph.add_edge(current_node, parent_node, label=f"output: {output_text}")
                else:
                    self.graph.add_edge(current_node, '__end__', label=f"output: {output_text}")
            else:
                if self.debugMode:
                    print("Unrecognized JSON format.")
        except json.JSONDecodeError as e:
            if self.debugMode:
                print(f"Failed to parse JSON: {e}")
        finally:
            self.inside_json_block = False
            self.current_json_block = []
            # After processing JSON, check if we have a pending end node
            if self.pending_end_node:
                if self.node_stack and self.node_stack[-1] == self.pending_end_node:
                    self.node_stack.pop()
                    self.pending_end_node = None
                else:
                    if self.debugMode:
                        print(f"End node mismatch after JSON: expected {self.node_stack[-1]} but got {self.pending_end_node}")
                    self.pending_end_node = None

    def draw_graph(self):
        if len(self.graph.nodes) == 0:
            if self.debugMode:
                print("No nodes in the graph. Ensure the log file is correctly parsed.")
            return
        pos = nx.spring_layout(self.graph)
        plt.figure(figsize=(10, 8))
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10,
                font_weight='bold', arrows=True)
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=10, label_pos=0.5)
        plt.title("Chain Execution Graph")
        plt.show()


# Usage Example:
file_path = r'D:\PJATK\INZ\LangGraph-Parser-PoC\langchain_debug_logs.log'
parser = ChainLogParser(file_path, debugMode=True)
parser.draw_graph()
