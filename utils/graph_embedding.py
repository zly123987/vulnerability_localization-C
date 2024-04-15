import torch
from tree_lstm import TreeLSTM

def create_tree_structure(json_dict):
    # Assign a unique node ID to each class or method
    node_id = 0
    node_mapping = {}
    adjacency_list = []
    node_order = []
    edge_order = []
    
    # Create a stack to perform a Depth-First Search of your tree
    stack = [(None, json_dict)]
    while stack:
        parent, node = stack.pop()
        if node not in node_mapping:
            node_mapping[node] = node_id
            node_id += 1
        if parent is not None:
            adjacency_list.append((node_mapping[parent], node_mapping[node]))
            edge_order.append(len(edge_order))
        node_order.append(node_mapping[node])
        
        # Add the children to the stack
        for child in node['children']:
            stack.append((node, child))

    return node_mapping, adjacency_list, node_order, edge_order


def get_tree_lstm_vector(json_dict):
    # Convert your data to tensors
    node_mapping, adjacency_list, node_order, edge_order = create_tree_structure(json_dict)
    print(adjacency_list)
    node_order = torch.tensor(node_order, dtype=torch.long)
    edge_order = torch.tensor(edge_order, dtype=torch.long)
    adjacency_list = torch.tensor(adjacency_list, dtype=torch.long)
    # Assuming features is your node features tensor
    features = torch.tensor(features, dtype=torch.float32)
    # Define the dimensionality of your input features and the dimensionality of the hidden states in the Tree LSTM.
    in_features = 100  # for example
    out_features = 100  # for example

    # Initialize the Tree LSTM model.
    tree_lstm_model = TreeLSTM(in_features, out_features)

    # Pass your data to the Tree-LSTM model
    h, c = tree_lstm_model(features, node_order, adjacency_list, edge_order)
    mean_embedding = h.mean(dim=0)
    print(mean_embedding)
if __name__=='__main__':
    json_dict = {
        "JndiLookup":{"lookUp": ["method"]}
    }
    get_tree_lstm_vector(json_dict)