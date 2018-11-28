from traph import Traph

traph = Traph(folder='./', debug=True)
trie = traph.lru_trie
link_store = traph.link_store

euronews_id = 342
euronews_prefixes = [
    's:https|h:com|h:euronews|h:fr|',
    's:http|h:com|h:euronews|h:fr|',
    's:http|h:com|h:euronews|h:fr|h:www|',
    's:https|h:com|h:euronews|h:fr|h:www|'
]

linked_ids = set([
    96,
    98,
    299,
    315
])

def links_iter(weid, prefixes):
    for prefix in prefixes:
        starting_node = trie.lru_node(prefix)
        target_node = trie.node()

        for node, lru in trie.webentity_dfs_iter(starting_node, prefix):

            if not node.is_page():
                continue

            if node.has_outlinks():
                links_block = node.outlinks()

                for link_node in link_store.link_nodes_iter(links_block):

                    target_node.read(link_node.target())
                    target_weid = trie.windup_lru_for_webentity(target_node)

                    if target_weid in linked_ids:
                        yield lru, trie.windup_lru(target_node.block)

for source_lru, target_lru in links_iter(euronews_id, euronews_prefixes):
    print(source_lru)
    print(target_lru)
    print()
