import os
import redis
from flask import Flask, render_template_string

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
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 0.4em 0.8em; text-align: left; }
    th { background: #eee; }
    .clean { color: green; }
    .notclean { color: red; font-weight: bold; }
    .summary { margin-bottom: 1.5em; }
  </style>
</head>
<body>
  <h1>Lossless Audio Checker Results</h1>
  <div class="summary">
    Total: {{ total }} &nbsp;|&nbsp;
    <span class="clean">Clean: {{ clean }}</span> &nbsp;|&nbsp;
    <span class="notclean">Not clean: {{ not_clean }}</span>
  </div>
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
            data = r.hgetall(key)
            if not data or b"result" not in data:
                continue
            rows.append({
                "result": data.get(b"result", b"").decode(),
                "filename": data.get(b"filename", b"").decode(),
                "path": data.get(b"path", b"").decode(),
            })
        if cursor == 0:
            break
    rows.sort(key=lambda r: (r["result"] != "Clean", r["path"]))
    return rows


@app.route("/")
def index():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    rows = get_results(r)
    clean = sum(1 for row in rows if row["result"] == "Clean")
    return render_template_string(
        TEMPLATE,
        rows=rows,
        total=len(rows),
        clean=clean,
        not_clean=len(rows) - clean,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
