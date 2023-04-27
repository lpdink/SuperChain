from .consensus_server import ConsensusServer, ConsensusNodeInit, RoleType 

class TreeServer(ConsensusServer):
    def _set_tree(self):
        post_box_init = ConsensusNodeInit(
            role=RoleType.POSTBOX, leader=self.consensus_group[1]
        )
        self.consensus_group[0].init_status = post_box_init
        tree_nodes = self.consensus_group[1:]  # 浅拷贝正是我们需要的
        for idx, node in enumerate(tree_nodes):
            left_idx = 2 * idx + 1
            right_idx = 2 * idx + 2
            parent_idx = int((idx - 1) / 2)
            node_left = tree_nodes[left_idx] if left_idx < len(tree_nodes) else None
            node_right = tree_nodes[right_idx] if right_idx < len(tree_nodes) else None
            node_parent = tree_nodes[parent_idx]
            node_leader = tree_nodes[0]
            if idx == 0:
                node_role = RoleType.LEADER
                node_parent = None
            else:
                node_role = RoleType.FOLLOWER
            node_status = ConsensusNodeInit(
                node_role,
                None, None, None,
                node_left,
                node_right,
                node_parent,
                node_leader,
            )
            node.init_status = node_status
        