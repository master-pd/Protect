import os, json, threading, time
from datetime import datetime
from telegram import Bot, ParseMode
from telegram.ext import Updater, CommandHandler
from jnius import autoclass

# ---------- Config ----------
CFG_FILE = os.path.expanduser('~/UltimateAntiTheftPro/config.json')
STORE_FILE = os.path.expanduser('~/UltimateAntiTheftPro/store.json')

if not os.path.exists(CFG_FILE):
    os.makedirs(os.path.dirname(CFG_FILE), exist_ok=True)
    with open(CFG_FILE,'w') as f:
        json.dump({
            "bot_token":"7620754730:AAHnzn3UYRbhrdb5m4LIwjiGb-OMjdnDvds",
            "admin_chat_id":6454347745,
            "heartbeat_min":30
        },f)

with open(CFG_FILE,'r') as f: cfg = json.load(f)
BOT_TOKEN = cfg.get("bot_token")
ADMIN_CHAT_ID = cfg.get("admin_chat_id")
HEARTBEAT_MIN = cfg.get("heartbeat_min",30)

bot = Bot(token=BOT_TOKEN)

# ---------- Device Auto-Detect ----------
Build = autoclass('android.os.Build')
PHONE_NAME = Build.MODEL

def register_device():
    if not os.path.exists(STORE_FILE):
        store = {"devices":{}}
    else:
        store = json.load(open(STORE_FILE))
        if "devices" not in store: store={"devices":store}

    if PHONE_NAME not in store["devices"]:
        store["devices"][PHONE_NAME] = {"extra_commands":["photo","location","alarm"]}
        with open(STORE_FILE,'w') as f:
            json.dump(store,f)
    return store["devices"][PHONE_NAME]

DEVICE = register_device()

# ---------- Helper ----------
def check_admin(chat_id):
    return chat_id==ADMIN_CHAT_ID

def send_message(text):
    bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode=ParseMode.MARKDOWN)

# ---------- Core Commands ----------
def cmd_status(update, context):
    if not check_admin(update.effective_chat.id):
        update.message.reply_text("Unauthorized"); return
    update.message.reply_text(f"Device: {PHONE_NAME}\nTime: {datetime.now()}")

def cmd_heartbeat(update, context):
    if not check_admin(update.effective_chat.id):
        update.message.reply_text("Unauthorized"); return
    update.message.reply_text(f"Heartbeat: {datetime.now()} ({PHONE_NAME})")

# ---------- Extra Commands ----------
def cmd_extra(update, context):
    if not check_admin(update.effective_chat.id):
        update.message.reply_text("Unauthorized"); return
    args = context.args
    if not args:
        update.message.reply_text("Usage: /extra <command> [all]")
        return

    command = args[0].lower()
    target = args[1] if len(args)>1 else PHONE_NAME

    with open(STORE_FILE,'r') as f: store=json.load(f)
    devices = store.get("devices",{})

    if target!="all" and target not in devices:
        update.message.reply_text(f"Device {target} not found"); return

    target_devices = devices.keys() if target=="all" else [target]

    for dev in target_devices:
        extra_cmds = devices[dev].get("extra_commands",[])
        if command not in extra_cmds:
            update.message.reply_text(f"Command {command} not allowed on {dev}")
            continue

        # Execute command example
        if command=="photo":
            update.message.reply_text(f"📸 Photo taken from {dev}")
        elif command=="location":
            update.message.reply_text(f"📍 Location sent from {dev}")
        elif command=="alarm":
            update.message.reply_text(f"🔔 Alarm triggered on {dev}")
        else:
            update.message.reply_text(f"Executed {command} on {dev}")

# ---------- Heartbeat Loop ----------
def heartbeat_loop():
    while True:
        send_message(f"Auto Heartbeat: {datetime.now()} ({PHONE_NAME})")
        time.sleep(HEARTBEAT_MIN*60)

# ---------- Main ----------
def main():
    if BOT_TOKEN.startswith("PUT_YOUR"):
        print("Edit config.json with BOT_TOKEN"); return

    updater = Updater(BOT_TOKEN,use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('status', cmd_status))
    dp.add_handler(CommandHandler('heartbeat', cmd_heartbeat))
    dp.add_handler(CommandHandler('extra', cmd_extra, pass_args=True))

    threading.Thread(target=heartbeat_loop,daemon=True).start()
    updater.start_polling()
    print(f"Ultimate Multi-Device Bot started on {PHONE_NAME}")
    updater.idle()

if __name__=="__main__":
    main()
