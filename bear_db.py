import sqlite3

import networkx as nx
import pandas as pd


def get_tags(bear_db_path):
    """
    Get the tags of notes as a dataframe.

    :param bear_db_path: the path to the bear db
    :return: Dataframe containing the note id, title, and tag (can have multiple rows of the same note id
            as notes can have multiple tags)
    """
    with sqlite3.connect(bear_db_path) as conn:
        conn.row_factory = sqlite3.Row
        query = 'SELECT ZSFNOTE.Z_PK AS ID,\
                        ZSFNOTE.ZTITLE AS Title,\
                        ZSFNOTETAG.ZTITLE AS Tag\
                 FROM Z_7TAGS\
                    INNER JOIN ZSFNOTE\
                    ON Z_7TAGS.Z_7NOTES=ZSFNOTE.Z_PK\
                    INNER JOIN ZSFNOTETAG\
                    ON Z_7TAGS.Z_14TAGS=ZSFNOTETAG.Z_PK\
                WHERE ZSFNOTE.ZTRASHED = 0'
        return pd.read_sql_query(query, conn)


def get_all_notes(bear_db_path):
    """
    Gets all the unique notes in the bear db that are note trashed as a dataframe

    :param bear_db_path: the path to the bear db
    :return: Dataframe containing the note id, unique identified, title, and text
    """
    with sqlite3.connect(bear_db_path) as conn:
        conn.row_factory = sqlite3.Row
        query = "SELECT Z_PK              AS ID\
                      , ZUNIQUEIDENTIFIER AS UID\
                      , ZTITLE            AS Title\
                      , ZTEXT             AS Text\
                  FROM ZSFNOTE AS TNote\
                  WHERE TNote.ZTRASHED = 0"
        return pd.read_sql_query(query, conn)


def get_notes_linking_to(id, bear_db_path):
    """
    Get the source notes that link to node with id
    :param id: the note id
    :param bear_db_path: the path to the bear db
    :return: Dataframe containing the note id, unique identified, title, and text of the source notes
    """

    with sqlite3.connect(bear_db_path) as conn:
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


def get_all_tables(bear_db_path):
    """
    Get all the tables of bear db
    :param bear_db_path: the path to the bear db
    :return: a dictionary of table names to dataframes of the tables
    """
    with sqlite3.connect(bear_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        df_tables = {}
        for table_name in tables:
            table_name = table_name[0]
            table = pd.read_sql_query("SELECT * from " + table_name, conn)
            df_tables[table_name] = table
        return df_tables


def build_tag_graph(bear_db_path):
    """
    Builds a tree graph of all the tags in bear
    :param bear_db_path: the path to the bear db
    :return: directed networkx graph
    """
    tags = get_tags(bear_db_path)
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