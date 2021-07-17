import os

import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

import bear_db
HOME = os.getenv('HOME', '')
DEFAULT_DB_PATH = os.path.join(HOME, 'Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite')
BACKLINKS_HEADER = '\n## Backlinks'


@st.cache
def build_streamlit_graph(bear_db_path, backlinks_header):
    notes = bear_db.get_all_notes(bear_db_path)
    G_tag, notes_to_tag = bear_db.build_tag_graph(bear_db_path)
    nodes = []
    edges = []
    for i, note in notes.iterrows():
        if note['ID'] not in notes_to_tag:
            continue

        nodes.append(Node(note['ID'], label=note['Title'], color='#453d3c'))

        # Add an edge from each leaf tag to corresponding note with tag
        for tag in notes_to_tag[note['ID']]:
            edges.append(Edge(source=tag, target=note['ID']))

        # Get notes this note is referenced by
        linked_by_notes = bear_db.get_notes_linking_to(note['ID'], bear_db_path)
        for j, linked_by_note in linked_by_notes.iterrows():
            lb_note_text = linked_by_note['Text'].split(backlinks_header)[0]
            # if the current(target) note is linked in the source note, before the backlinks section
            if ('[[' + note['Title'] + ']]') in lb_note_text:
                edges.append(Edge(source=linked_by_note['ID'], target=note['ID'],
                                  color='#385385'))

    for node in G_tag.nodes:
        nodes.append(Node(node, label=node, color='#db230b'))

    for src, dest in G_tag.edges:
        edges.append(Edge(source=src, target=dest, color='#d3d3d3'))

    nodes_in_edges = set()
    for edge in edges:
        nodes_in_edges.add(edge.source)
        nodes_in_edges.add(edge.target)
    nodes = [node for node in nodes if node.id in nodes_in_edges]

    return nodes, edges


st.set_page_config(page_title='Bear Graph', page_icon=":Bear:", layout="wide")
st.title('Bear Notes Graph 🐻')

st.markdown("""
 A graph created from a user's bear db. Your graph will appear below.
""")
# uploaded_file = st.sidebar.file_uploader("Choose a file")

nodes, edges = build_streamlit_graph(DEFAULT_DB_PATH, BACKLINKS_HEADER)


st.sidebar.header('Graph Configurations')
layout = st.sidebar.selectbox('Layout', ['dot',
                                         'sphere',
                                         'fr',
                                         'rt',])
st.sidebar.header('Legend')
st.sidebar.image("media/legend.png", use_column_width=True)
st.sidebar.text('')
st.sidebar.markdown(f"**There are a {len(nodes)} nodes and {len(edges)} edges** 🚀")


config = Config(width=1250,
                graphviz_layout=layout,
                graphviz_config={"rankdir": 'BT', "ranksep": 7, "nodesep": 7},
                directed=True,
                nodeHighlightBehavior=True,
                linkHighlightBehavior=True,
                highlightColor="#F6A7A6",
                collapsible=True,
                node={'labelProperty': 'label', 'renderLabel': True, 'highlightColor': '#73f593',
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