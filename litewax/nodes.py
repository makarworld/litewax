import requests

class Nodes:
    """Get nodes from antelope and ping them"""
    @staticmethod
    def get_nodes(network = "mainnet") -> list:
        """
        Get producers nodes from antelope
        
        :param network: mainnet or testnet
        
        :return: list of nodes
        """
        if network == "testnet":
            url = "https://graphql-wax-testnet.antelope.tools/v1/graphql"
        else:
            url = "https://graphql-wax.antelope.tools/v1/graphql"

        nodesList = requests.post(
            url,
            json={
                "operationName": "producer",
                "variables": {
                    "offset": 0,
                    "limit": 130,
                    "where": {
                    "owner": {
                        "_like": "%%"
                    },
                    "nodes": {"endpoints": {"response": {"_contains": {"status": 200}}}}},
                    "endpointFilter": {
                    "_or": [{"type": {"_eq": "p2p"}},{"response": {"_contains": {"status": 200}}}]
                    }
                },
                "query": "query producer($offset: Int = 0, $limit: Int = 21, $where: producer_bool_exp, $endpointFilter: endpoint_bool_exp) {\n  info: producer_aggregate(where: $where) {\n    producers: aggregate {\n      count\n      __typename\n    }\n    __typename\n  }\n  producers: producer(\n    where: $where\n    order_by: {total_votes_percent: desc}\n    offset: $offset\n    limit: $limit\n  ) {\n    id\n    owner\n    updated_at\n    nodes {\n      endpoints(order_by: {head_block_time: desc}, where: $endpointFilter) {\n        id\n        type\n        value\n        head_block_time\n        response\n        updated_at\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
            }).json()

        nodes = []

        for producer in nodesList['data']['producers']:
            for node in producer['nodes']:
                
                if node['endpoints']:
                    for endpoint in node['endpoints']:
                        
                        if endpoint['type'] == 'ssl':
                            nodes.append(endpoint['value'])
        
        return nodes

    @staticmethod
    def ping_nodes(network = "mainnet") -> dict:
        """
        Ping nodes and return dict. key - URL, value - ping (ms)
        
        :param network: mainnet or testnet
        
        :return: dict. key - URL, value - ping (ms)"""
        nodes = Nodes.get_nodes(network=network)

        result = {}
        for node in nodes:
            try:
                req = requests.get(node + "/v1/chain/get_accounts_by_authorizers", timeout=5)
                if req.json().get("message") == "Not Found":
                    ping = 9999
                else:
                    ping = int(req.elapsed.total_seconds() * 1000)
                result[node] = ping
            except:
                result[node] = 9999
        
        return result

    @staticmethod
    def best_nodes(network = "mainnet") -> dict:
        """
        Search best nodes for you. It may take a 20-50 sec. to get the result.
        
        :param network: mainnet or testnet
        
        :return: sorted dict. key - URL, value - ping (ms)
        """
        nodes = Nodes.ping_nodes(network=network)

        return dict(sorted(nodes.items(), key=lambda item: item[1]))
        

    @staticmethod
    def best_node(network = "mainnet") -> str:
        """
        Returns the best node with the lowest ping. It may take a 20-50 sec. to get the result.
        
        :param network: mainnet or testnet
        
        :return: URL
        """
        nodes = Nodes.best_nodes(network=network)

        best_node = list(nodes.keys())[0]
        best_ping = list(nodes.values())[0]
        print(f"Best node: {best_node} ({best_ping}ms)")
        return best_node


#if __name__ == '__main__':
#    Nodes.best_node()