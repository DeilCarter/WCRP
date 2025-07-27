# DISCORD BOT
TOKEN = "MTM5ODk2MDUxNjA4ODU5ODYxOQ.GSJ1aE.OYspbisT6pQ6EnGL45SNnoQPTDJFHrm-u_P_5c"
PREFIX = ">"

# ERLC SERVER
API_URL = "https://api.policeroleplay.community/v1/server"
API_KEY = "SabvPXdoQYgEaCSyxlOD-yNpevWPmlwygYRMlnobiDWNEIvGYqBFDSPihlHGe"

HEADERS = {
    "server-key": API_KEY,
    "Accept": "*/*"
}
BANNED_VEHICLES = {
    "Chevlon Corbeta 1M Edition 2014",
    "Chevlon Corbeta C2 1967",
    "Navara Boundary 2022",
    "Celestial Type-6 2023",
    "Chevlon Corbeta X08 2014",
    "Chevlon Corbeta RZR 2014",
    "Chevlon Corbeta TZ",
    "Chevlon Corbeta 8 2023",
    "Takeo Experience 2021",
    "Averon R8 2017",
    "Surrey 650S 2016",
    "Silhouette Carbon",
    "Strugatti Ettore 2020",
    "Falcon Heritage 2021",
    "Falcon Heritage Track 2022",
    "Kovac Heladera 2023"
}

MODERATOR_COMMANDS = {
    ":h",
    ":m",
    ":tp",
    ":bring",
    ":load",
    ":heal",
    ":kill",
    ":log",
    ":pm",
    ":refresh",
    ":unwanted",
    ":wanted",
    ":jail",
    ":pt",
    ":kick"
}
ADMINISTRATOR_COMMANDS = {
    ":time",
    ":mod",
    ":unmod",
    ":weather",
    ":ban",
    ":unban"
}
OWNER_COMMANDS = {
    ":admin",
    ":unadmin"
}

import json


def load_admins():
    with open("admin.json", "r") as f:
        return json.load(f)["admins"]

def save_admins(admins):
    with open("admin.json", "w") as f:
        json.dump({"admins": admins}, f, indent=4)

ADMIN_ID = load_admins()

# Время ожидания между проверками игроков, например
VEHICLE_CHECK_INTERVAL = 3600  # В секундах

# CMDS
STARTUP_REACTION_COUNT = 4

# ROLES
ADMIN_ROLE_ID = [1307375137573568633, 1377698319475933298]
MODERATOR_ROLE_ID = [1307375137573568632] + ADMIN_ROLE_ID
SHR_ROLE_ID  = 1377698308574941326
OWNER_ID = 123456789012345678

# CHANNELS
LOG_CHANNEL_ID = 139900000000000000
STARTUP_CHANNEL_ID = 1377550692109258843
SHUTDOWN_CHANNEL_ID = 1398969594538102888
INGAME_ALARM_CHANNEL_ID = 1399071643963494440

