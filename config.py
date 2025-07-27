from flask import Flask, render_template_string, request, redirect
import os

CONFIG_FILE = "config.py"

app = Flask(__name__)

# Функция загрузки конфига из файла
def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            code = f.read()
            exec(code, config)
    return {
        "BOT_TOKEN": config.get("TOKEN", ""),
        "PREFIX": config.get("PREFIX", ""),
        "API_URL": config.get("API_URL", ""),
        "API_KEY": config.get("API_KEY", ""),
        "STARTUP_REACTION_COUNT": config.get("STARTUP_REACTION_COUNT", 1),
        "STARTUP_CHANNEL_ID": config.get("STARTUP_CHANNEL_ID", ""),
        "SHUTDOWN_CHANNEL_ID": config.get("SHUTDOWN_CHANNEL_ID", ""),
    }

# Функция сохранения конфига в файл
def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        f.write(f'''# BOT
TOKEN = "{data["BOT_TOKEN"]}"
PREFIX = "{data["PREFIX"]}"

# ERLC SERVER
API_URL = "{data["API_URL"]}"
API_KEY = "{data["API_KEY"]}"

# CMDS
STARTUP_REACTION_COUNT = {data["STARTUP_REACTION_COUNT"]} 

# CHANNELS
STARTUP_CHANNEL_ID = {data["STARTUP_CHANNEL_ID"]}
SHUTDOWN_CHANNEL_ID = {data["SHUTDOWN_CHANNEL_ID"]}
''')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Config Editor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; max-width: 600px;}
        label { display: block; margin-top: 15px; font-weight: bold;}
        input[type=text], input[type=number] { width: 100%; padding: 8px; margin-top: 5px; box-sizing: border-box; }
        button { margin-top: 20px; padding: 10px 15px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Редактор конфига</h1>
    <form method="POST">
        <label>BOT TOKEN</label>
        <input type="text" name="BOT_TOKEN" value="{{config.BOT_TOKEN}}" required />

        <label>PREFIX</label>
        <input type="text" name="PREFIX" value="{{config.PREFIX}}" required />

        <label>API_URL</label>
        <input type="text" name="API_URL" value="{{config.API_URL}}" required />

        <label>API_KEY</label>
        <input type="text" name="API_KEY" value="{{config.API_KEY}}" required />

        <label>STARTUP_REACTION_COUNT</label>
        <input type="number" name="STARTUP_REACTION_COUNT" min="1" value="{{config.STARTUP_REACTION_COUNT}}" required />

        <label>STARTUP_CHANNEL_ID</label>
        <input type="text" name="STARTUP_CHANNEL_ID" value="{{config.STARTUP_CHANNEL_ID}}" required />

        <label>SHUTDOWN_CHANNEL_ID</label>
        <input type="text" name="SHUTDOWN_CHANNEL_ID" value="{{config.SHUTDOWN_CHANNEL_ID}}" required />

        <button type="submit">Сохранить</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def config_editor():
    if request.method == "POST":
        data = {
            "BOT_TOKEN": request.form["BOT_TOKEN"],
            "PREFIX": request.form["PREFIX"],
            "API_URL": request.form["API_URL"],
            "API_KEY": request.form["API_KEY"],
            "STARTUP_REACTION_COUNT": int(request.form["STARTUP_REACTION_COUNT"]),
            "STARTUP_CHANNEL_ID": int(request.form["STARTUP_CHANNEL_ID"]),
            "SHUTDOWN_CHANNEL_ID": int(request.form["SHUTDOWN_CHANNEL_ID"]),
        }
        save_config(data)
        return redirect("/")
    else:
        config = load_config()
        return render_template_string(HTML_TEMPLATE, config=config)

if __name__ == "__main__":
    app.run(debug=True)
