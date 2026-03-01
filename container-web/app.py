import os
import redis
from collections import defaultdict
from flask import Flask, render_template_string, request

app = Flask(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Lossless Audio Checker Results</title>
  <style>
    body { font-family: monospace; padding: 2em; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 2em; }
    th, td { border: 1px solid #ccc; padding: 0.4em 0.8em; text-align: left; }
    th { background: #eee; }
    .clean { color: green; }
    .notclean { color: red; font-weight: bold; }
    .summary { margin-bottom: 1em; }
    .filters { margin-bottom: 1.5em; }
    .filters a { margin-right: 1em; text-decoration: none; }
    .filters a.active { font-weight: bold; text-decoration: underline; }
    h2 { margin-top: 1.5em; }
  </style>
</head>
<body>
  <h1>Lossless Audio Checker Results</h1>
  <div class="summary">
    Total: {{ total }} &nbsp;|&nbsp;
    <span class="clean">Clean: {{ clean }}</span> &nbsp;|&nbsp;
    <span class="notclean">Not clean: {{ not_clean }}</span>
  </div>
  <div class="filters">
    <a href="/" class="{{ 'active' if filter == 'all' }}">All</a>
    <a href="/?filter=clean" class="{{ 'active' if filter == 'clean' }}">Clean</a>
    <a href="/?filter=notclean" class="{{ 'active' if filter == 'notclean' }}">Not Clean</a>
  </div>

  <h2>By Directory</h2>
  <table>
    <tr>
      <th>Status</th>
      <th>Directory</th>
      <th>Files</th>
    </tr>
    {% for dir in dirs %}
    <tr>
      <td class="{{ 'clean' if dir.clean_count == dir.count else 'notclean' }}">
        {{ dir.clean_count }}/{{ dir.count }} clean ({{ dir.pct_clean }}%)
      </td>
      <td>{{ dir.prefix }}</td>
      <td>{{ dir.count }}</td>
    </tr>
    {% endfor %}
  </table>

  <h2>Files</h2>
  <table>
    <tr>
      <th>Result</th>
      <th>Filename</th>
      <th>Path</th>
    </tr>
    {% for row in rows %}
    <tr>
      <td class="{{ 'clean' if row.result == 'Clean' else 'notclean' }}">{{ row.result }}</td>
      <td>{{ row.filename }}</td>
      <td>{{ row.path }}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""


def get_results(r):
    rows = []
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor, count=100)
        for key in keys:
            key_str = key.decode()
            if key_str.endswith("-lock"):
                continue
            try:
                data = r.hgetall(key)
            except redis.exceptions.ResponseError:
                continue
            if not data or b"result" not in data:
                continue
            rows.append({
                "result": data.get(b"result", b"").decode(),
                "filename": data.get(b"filename", b"").decode(),
                "path": data.get(b"path", b"").decode(),
            })
        if cursor == 0:
            break
    rows.sort(key=lambda r: r["path"])
    return rows


def build_dir_report(rows):
    dirs = defaultdict(lambda: {"count": 0, "clean_count": 0})
    for row in rows:
        prefix = os.path.dirname(row["path"])
        dirs[prefix]["count"] += 1
        if row["result"] == "Clean":
            dirs[prefix]["clean_count"] += 1
    result = []
    for prefix, d in dirs.items():
        pct = round(100 * d["clean_count"] / d["count"]) if d["count"] else 0
        result.append({"prefix": prefix, "count": d["count"],
                        "clean_count": d["clean_count"], "pct_clean": pct})
    return sorted(result, key=lambda d: (d["pct_clean"], d["prefix"]))


@app.route("/")
def index():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    all_rows = get_results(r)
    clean = sum(1 for row in all_rows if row["result"] == "Clean")

    filter_param = request.args.get("filter", "all")
    if filter_param == "clean":
        rows = [row for row in all_rows if row["result"] == "Clean"]
    elif filter_param == "notclean":
        rows = [row for row in all_rows if row["result"] != "Clean"]
    else:
        filter_param = "all"
        rows = all_rows

    return render_template_string(
        TEMPLATE,
        rows=rows,
        dirs=build_dir_report(all_rows),
        total=len(all_rows),
        clean=clean,
        not_clean=len(all_rows) - clean,
        filter=filter_param,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
