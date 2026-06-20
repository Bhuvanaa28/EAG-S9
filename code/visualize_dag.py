import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
import os
import argparse

def get_node_label_parts(node):
    skill = node.get('skill', '').replace('_', ' ').title()
    metadata = node.get('metadata', {})
    
    desc = ""
    if 'goal' in metadata:
        desc = metadata['goal']
    elif 'question' in metadata:
        desc = metadata['question']
    elif 'failure_report' in metadata:
        desc = "Recovery Node"
    elif 'label' in metadata:
        desc = metadata['label']

    if len(desc) > 50:
        desc = desc[:47] + "..."
    
    return skill, desc

def visualize_dag(session_id):
    base_sessions_path = r"c:\Bhuv\The School of AI\S9 code\code\state\sessions"
    json_path = os.path.join(base_sessions_path, session_id, "graph.json")

    if not os.path.exists(json_path):
        print(f"Error: graph.json not found at {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    G = nx.DiGraph()
    node_data = {node['id']: node for node in data['nodes']}
    
    for node in data['nodes']:
        G.add_node(node['id'])
    for edge in data['edges']:
        G.add_edge(edge['source'], edge['target'])

    try:
        layers = list(nx.topological_generations(G))
    except:
        layers = [[n] for n in G.nodes()]

    # Spacing
    layer_width = 4.5
    node_height = 2.0
    
    pos = {}
    for layer_idx, nodes in enumerate(layers):
        v_offset = (len(nodes) - 1) * node_height / 2
        for node_idx, node_id in enumerate(nodes):
            pos[node_id] = (layer_idx * layer_width, -node_idx * node_height + v_offset)

    fig, ax = plt.subplots(figsize=(18, 10))
    bg_color = '#F8F5F0'
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)

    # Theme Colors
    theme = {
        "box_bg": "#E6E6FA",
        "box_border": "#9B86BD",
        "complete": "#C8E6C9",
        "failed": "#FFCDD2",
        "pending": "#E0E0E0",
        "running": "#BBDEFB",
        "text": "#2C3E50"
    }

    # Status to Color Mapping
    status_bg = {
        "complete": theme["complete"],
        "failed": theme["failed"],
        "pending": theme["pending"],
        "running": theme["running"],
        "unknown": theme["box_bg"]
    }

    # Draw Edges
    for u, v in G.edges():
        ux, uy = pos[u]
        vx, vy = pos[v]
        # Curved arrows
        ax.annotate("", 
                    xy=(vx - 0.9, vy), xycoords='data',
                    xytext=(ux + 0.9, uy), textcoords='data',
                    arrowprops=dict(arrowstyle="-|>", color="#7F8C8D", 
                                  connectionstyle="arc3,rad=0.15", lw=1.2, mutation_scale=15))

    # Draw Nodes
    for node_id, (x, y) in pos.items():
        node = node_data[node_id]
        status = node.get('status', 'unknown')
        skill_name = node.get('skill', '')
        
        bg = status_bg.get(status, theme["box_bg"])
        border = theme["box_border"]
        
        skill, desc = get_node_label_parts(node)
        
        # Determine shape: Diamond for generic logic/planner/critic
        if skill_name.lower() in ['planner', 'critic'] or '?' in desc:
            poly = mpatches.RegularPolygon((x, y), numVertices=4, radius=1.0, 
                                          facecolor=bg, edgecolor=border, lw=1.5, zorder=3)
            ax.add_patch(poly)
        else:
            # Box
            width = 1.8
            height = 1.0
            box = mpatches.FancyBboxPatch((x - width/2, y - height/2), width, height, 
                                         boxstyle="round,pad=0.1,rounding_size=0.1", 
                                         facecolor=bg, edgecolor=border, lw=1.5, zorder=3)
            ax.add_patch(box)
        
        # Skill Text (Bold)
        ax.text(x, y + (0.15 if desc else 0), skill, ha='center', va='center', 
                fontsize=10, fontweight='bold', color=theme["text"], zorder=4)
        
        # Description Text (Smaller)
        if desc:
            # Wrap description
            wrapped_desc = "\n".join([desc[i:i+20] for i in range(0, len(desc), 20)])
            ax.text(x, y - 0.2, wrapped_desc, ha='center', va='center', 
                    fontsize=8, color='#5D6D7E', zorder=4, linespacing=1.2)

    ax.set_xlim(-2, len(layers) * layer_width)
    max_nodes = max(len(l) for l in layers)
    ax.set_ylim(-max_nodes * node_height / 2 - 1, max_nodes * node_height / 2 + 1)
    ax.axis('off')
    
    plt.title(f"DAG Execution Flow | Session: {session_id}", fontsize=20, fontweight='bold', pad=40, color='#2C3E50')
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=theme["complete"], edgecolor=theme["box_border"], label='Complete'),
        mpatches.Patch(facecolor=theme["failed"], edgecolor=theme["box_border"], label='Failed'),
        mpatches.Patch(facecolor=theme["pending"], edgecolor=theme["box_border"], label='Pending'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.05))

    # Ensure logs directory exists
    output_dir = r"c:\Bhuv\The School of AI\S9 code\logs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_image = os.path.join(output_dir, f"dag_{session_id}.png")
    plt.savefig(output_image, dpi=300, bbox_inches='tight', facecolor=bg_color)
    print(f"Premium visualization saved to {output_image}")
    
    try:
        plt.show()
    except Exception:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize a DAG with a premium UI")
    parser.add_argument("session_id", help="The ID of the session")
    args = parser.parse_args()
    visualize_dag(args.session_id)
