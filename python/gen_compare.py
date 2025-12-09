import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

RESULTS = "results.json"

def load_results():
    with open(RESULTS) as f:
        return pd.DataFrame(json.load(f))

def compare_tcp_http(df):
    tcp = df[df.server.isin(["mono", "multi"])]
    http = df[df.server.isin(["mono_http", "multi_http"])]

    # Renommer les colonnes pour comparaison
    tcp = tcp.rename(columns={"throughput_rps": "tcp_rps"})
    http = http.rename(columns={"throughput_rps": "http_rps"})

    merged = pd.merge(
        tcp[["clients", "server", "tcp_rps"]],
        http[["clients", "server", "http_rps"]],
        on="clients",
        how="outer"
    )
    return merged

def plot_speedup(df):
    df["speedup"] = df["tcp_rps"] / df["http_rps"]
    fig = px.line(df, x="clients", y="speedup",
                  title="Speedup TCP vs HTTP")
    fig.write_html("compare_speedup.html")
    fig.write_image("compare_speedup.png")
    return fig

def generate_excel(df, merged):
    with pd.ExcelWriter("compare.xlsx") as writer:
        df.to_excel(writer, sheet_name="raw_results", index=False)
        merged.to_excel(writer, sheet_name="tcp_vs_http", index=False)

def generate_dashboard(df, merged):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.clients, y=df.throughput_rps,
                             mode="lines+markers",
                             name="Throughput Global"))

    fig.update_layout(title="Comparaison globale TCP/HTTP")
    fig.write_html("compare.html")

def main():
    df = load_results()
    merged = compare_tcp_http(df)
    generate_excel(df, merged)
    generate_dashboard(df, merged)
    plot_speedup(merged)
    print("[OK] Fichiers générés : compare.html, compare.xlsx, compare_speedup.png")

if __name__ == "__main__":
    main()