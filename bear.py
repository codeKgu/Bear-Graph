"""
Code to access bear db taken from https://github.com/DeLub/bear-backlinks/blob/master/update-backlinks.py
"""

import sqlite3

import os
import streamlit as st

import networkx as nx
import pandas as pd
from streamlit_agraph import Config, Edge, Node, agraph

st.set_page_config(page_title='Bear Graph', page_icon=":Bear:", layout="wide")
st.title('Bear Notes Graph 🐻')

st.markdown("""
 A graph created from a user's bear db. Your graph will appear below.
""")


HOME = os.getenv('HOME', '')
DEFAULT_DB_PATH = os.path.join(HOME, 'Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite')
backlinks_header = '\n## Backlinks'


def main(bear_db):
    notes = get_all_notes(bear_db)
    G_tag, notes_to_tag = build_tag_graph(bear_db)
    nodes = []
    edges = []
    for i, note in notes.iterrows():
        # Split Note text from backlinks
        note_text = note['Text'].split(backlinks_header)[0]
        if note['ID'] not in notes_to_tag:
            continue

        nodes.append(Node(note['ID'], label=note['Title']))

        # Add an edge from each leaf tag to corresponding note with tag
        for tag in notes_to_tag[note['ID']]:
            edges.append(Edge(source=tag, target=note['ID']))

        # Get notes this note is referenced by
        linked_by_notes = get_notes_linking_to(note['ID'], bear_db)
        for j, linked_by_note in linked_by_notes.iterrows():
            lb_note_text = linked_by_note['Text'].split(backlinks_header)[0]
            if ('[[' + note['Title'] + ']]') in lb_note_text:  #if the current(target) note is linked in the source note, before the backlinks section
                edges.append(Edge(source=linked_by_note['ID'], target=note['ID'],
                                  color='#385385'))

    for node in G_tag.nodes:
        nodes.append(Node(node, label=node, color='red'))

    for src, dest in G_tag.edges:
        edges.append(Edge(source=src, target=dest, color='#d3d3d3'))

    return nodes, edges, G_tag

def get_tags(bear_db):
    with sqlite3.connect(bear_db) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT ZSFNOTE.Z_PK AS ID,\
                        ZSFNOTE.ZTITLE AS Title,\
                        ZSFNOTETAG.ZTITLE AS Tag\
                 FROM ZSFNOTE\
                    INNER JOIN Z_7TAGS\
                    ON ZSFNOTE.Z_PK=Z_7TAGS.Z_7NOTES\
                    INNER JOIN ZSFNOTETAG\
                    ON Z_7TAGS.Z_14TAGS=ZSFNOTETAG.Z_PK\
                WHERE ZSFNOTE.ZTRASHED = 0"
        return pd.read_sql_query(query, conn)


def get_all_notes(bear_db):
    with sqlite3.connect(bear_db) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT TNote.Z_PK              AS ID\
                      , TNote.ZUNIQUEIDENTIFIER AS UID\
                      , TNote.ZTITLE            AS Title\
                      , TNote.ZTEXT             AS Text\
                  FROM ZSFNOTE AS TNote\
                  WHERE TNote.ZTRASHED = 0"
        return pd.read_sql_query(query, conn)


def get_notes_linking_to(id, bear_db):
    with sqlite3.connect(bear_db) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT DISTINCT\
                        SNote.Z_PK              AS ID\
                      , SNote.ZUNIQUEIDENTIFIER AS UID\
                      , SNote.ZTITLE            AS Title\
                      , SNote.ZTEXT             AS Text\
                   FROM Z_7LINKEDNOTES          AS Source\
                      , ZSFNOTE                 AS SNote\
                  WHERE Source.Z_7LINKEDNOTES = %i\
                    AND SNote.Z_PK            = Source.Z_7LINKEDBYNOTES\
                    AND SNote.ZTRASHED        = 0\
               ORDER BY SNote.ZCREATIONDATE ASC" % id
        return pd.read_sql_query(query, conn)


def get_all_tables(bear_db):
    with sqlite3.connect(bear_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        df_tables = {}
        for table_name in tables:
            table_name = table_name[0]
            table = pd.read_sql_query("SELECT * from " + table_name, conn)
            df_tables[table_name] = table
        return df_tables


def build_tag_graph(bear_db):
    tags = get_tags(bear_db)
    unique_tags = set(tags['Tag'].values)
    edge_list = []
    for tag_path in unique_tags:
        tags_in_path = tag_path.split('/')
        if len(tags_in_path) >= 2:
            for i in range(len(tags_in_path) - 1):
                edge_list.append(f'{"/".join(tags_in_path[:i + 1])},{"/".join(tags_in_path[:i + 2])}')
    G_tag = nx.parse_edgelist(edge_list, delimiter=',', create_using=nx.DiGraph)

    def keep_leaf_nodes(tags):
        return [node for node in tags.values if not any(True for _ in G_tag.neighbors(node))]

    note_to_tags = tags.groupby(by=['ID'])['Tag'].apply(keep_leaf_nodes).to_dict()
    return G_tag, note_to_tags


if __name__ == '__main__':

    nodes, edges, G_tag = main(DEFAULT_DB_PATH)
    nodes_in_edges = set()
    for edge in edges:
        nodes_in_edges.add(edge.source)
        nodes_in_edges.add(edge.target)
    nodes = [node for node in nodes if node.id in nodes_in_edges]

    st.sidebar.header('Graph Configurations')
    layout = st.sidebar.selectbox('Layout', ['dot',
                                             'sphere',
                                             'fr',
                                             'rt',])
    st.sidebar.markdown(f"**There are a {len(nodes)} nodes and {len(edges)} edges** 🚀")

    config = Config(width=1250,
                    graphviz_layout=layout,
                    graphviz_config={"rankdir": 'BT', "ranksep": 7, "nodesep": 7},
                    directed=True,
                    nodeHighlightBehavior=True,
                    linkHighlightBehavior=True,
                    highlightColor="#F6A7A6",
                    collapsible=True,
                    node={'labelProperty': 'label', 'renderLabel': True, 'highlightColor': '#FFFF00',
                          'highlightFontWeight': '800', "highlightFontSize": 10},
                    link={'labelProperty': 'label', 'renderLabel': True,
                          'highlightFontWeight': '800'},
                    highlightDegree=2,
                    maxZoom=2,
                    minZoom=0.1,
                    staticGraphWithDragAndDrop=False,
                    staticGraph=False,
                    initialZoom=1
                    )

    return_value = agraph(nodes=nodes,
                          edges=edges,
                          config=config)