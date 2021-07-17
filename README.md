# BearGraph
A dashboard, to be ran locally, to view your [Bear](https://bear.app/) Notes as a graph.

![](media/usage.gif)

## Implementation
The graph is constructed using the Bear sqlite database using links between notes as well as the tag structure. 
In addition, backlinks are ignored if the links come after `BACKLINKS_HEADER` (which is specified in `run_bear_graph.py`).

Sqlite3 is used to connect to the Bear database, typically stored in
`
~/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite
`, to construct the graph.

Meanwhile, we use [streamlit](https://streamlit.io/) and [streamlit_agraph](https://github.com/ChrisChross/streamlit-agraph)
to build the UI. 



## Usage
Make sure `DEFAULT_DB_PATH` and `BACKLINKS_HEADER` are configured correctly in `run_bear_graph.py`

```bash
streamlit run bear.py
```
