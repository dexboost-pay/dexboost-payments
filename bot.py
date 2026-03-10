import os
import time
import requests
import telebot

from telebot import types
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip()
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@support").strip()

PANDABOOST_API_KEY = os.getenv("PANDABOOST_API_KEY", "").strip()
PANDABOOST_BASE_URL = os.getenv("PANDABOOST_BASE_URL", "https://web.pandaboost.app/api/v1").strip()

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in .env")

if not PANDABOOST_API_KEY:
    raise ValueError("PANDABOOST_API_KEY is missing in .env")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ---------------------------------
# STATE
# ---------------------------------
user_state = {}


def reset_user(chat_id):
    user_state[chat_id] = {}


def get_state(chat_id):
    return user_state.get(chat_id, {})


def set_state(chat_id, data):
    user_state[chat_id] = data


# ---------------------------------
# SUPPLIER PRICES (your PandaBoost prices)
# ---------------------------------
SUPPLIER_PRICES = {
    "rocket": 0.018,
    "fire": 0.018,
    "flag": 0.018,
    "poop": 0.018,

    "gecko-search": 120,
    "gecko-pool": 120,
    "gecko-full": 200,

    "dex-trending-sol-24h": 1300,
    "dex-trending-sol-12h": 1000,
    "dex-trending-evm-24h": 800,

    "manual-dextools-sol": 1100,
    "manual-dextools-evm": 800,
    "manual-dextools-other": 500,
    "manual-birdeye": 200,
    "manual-solscan": 250,
    "manual-rugcheck": 150,
    "manual-insightx": 150,
}

# ---------------------------------
# CLIENT PRICES (what your clients see)
# ---------------------------------
CLIENT_PRICES = {
    "rocket": 0.045,
    "fire": 0.045,
    "flag": 0.045,
    "poop": 0.045,

    "gecko-search": 249,
    "gecko-pool": 249,
    "gecko-full": 399,

    "dex-trending-sol-24h": 2290,
    "dex-trending-sol-12h": 1590,
    "dex-trending-evm-24h": 1390,

    "manual-dextools-sol": 1690,
    "manual-dextools-evm": 1190,
    "manual-dextools-other": 790,
    "manual-birdeye": 349,
    "manual-solscan": 399,
    "manual-rugcheck": 249,
    "manual-insightx": 249,
}

# ---------------------------------
# LAUNCH PACKAGES
# ---------------------------------
PACKAGES = {
    "🚀 Starter Launch Pack": {
        "package_name": "Starter Launch Pack",
        "client_price": 990,
        "supplier_cost": 465,
        "description": (
            "Best for fresh launches that need visibility fast.\n\n"
            "Includes:\n"
            "• 5,000 DEX Reactions\n"
            "• Gecko Search Trending\n"
            "• Birdeye Trending (manual)\n"
        )
    },
    "🔥 Trending Push Pack": {
        "package_name": "Trending Push Pack",
        "client_price": 1990,
        "supplier_cost": 1210,
        "description": (
            "Strong launch setup for meme coins and active campaigns.\n\n"
            "Includes:\n"
            "• Solana Trending 12H\n"
            "• Gecko Search Trending\n"
            "• 5,000 DEX Reactions\n"
            "• Birdeye Trending (manual)\n"
        )
    },
    "💎 Full Launch Campaign": {
        "package_name": "Full Launch Campaign",
        "client_price": 2990,
        "supplier_cost": 1680,
        "description": (
            "High-impact package for teams that want maximum visibility.\n\n"
            "Includes:\n"
            "• Solana Trending 24H\n"
            "• Gecko Full Trending\n"
            "• 10,000 DEX Reactions\n"
            "• Birdeye Trending (manual)\n"
            "• Launch support flow\n"
        )
    },
}

# ---------------------------------
# API / MANUAL SERVICES
# ---------------------------------
API_ORDER_TYPES = {
    "🚀 Rocket ($45 / 1000)": {
        "mode": "api",
        "service_name": "reactions",
        "order_type_id": "rocket",
        "plan_name": "Rocket",
        "client_unit_price": CLIENT_PRICES["rocket"],
        "supplier_unit_price": SUPPLIER_PRICES["rocket"],
        "needs_quantity": True,
        "needs_speed": True,
        "category": "DEX Screener Reactions",
    },
    "🔥 Fire ($45 / 1000)": {
        "mode": "api",
        "service_name": "reactions",
        "order_type_id": "fire",
        "plan_name": "Fire",
        "client_unit_price": CLIENT_PRICES["fire"],
        "supplier_unit_price": SUPPLIER_PRICES["fire"],
        "needs_quantity": True,
        "needs_speed": True,
        "category": "DEX Screener Reactions",
    },
    "🚩 Flag ($45 / 1000)": {
        "mode": "api",
        "service_name": "reactions",
        "order_type_id": "flag",
        "plan_name": "Flag",
        "client_unit_price": CLIENT_PRICES["flag"],
        "supplier_unit_price": SUPPLIER_PRICES["flag"],
        "needs_quantity": True,
        "needs_speed": True,
        "category": "DEX Screener Reactions",
    },
    "💩 Poop ($45 / 1000)": {
        "mode": "api",
        "service_name": "reactions",
        "order_type_id": "poop",
        "plan_name": "Poop",
        "client_unit_price": CLIENT_PRICES["poop"],
        "supplier_unit_price": SUPPLIER_PRICES["poop"],
        "needs_quantity": True,
        "needs_speed": True,
        "category": "DEX Screener Reactions",
    },

    "☀️ Solana 24H - $2,290": {
        "mode": "api",
        "service_name": "dex-trending",
        "order_type_id": "dex-trending-sol-24h",
        "plan_name": "Solana 24H",
        "client_price": CLIENT_PRICES["dex-trending-sol-24h"],
        "supplier_price": SUPPLIER_PRICES["dex-trending-sol-24h"],
        "needs_quantity": False,
        "needs_speed": False,
        "category": "DEX Screener Trending",
    },
    "🌙 Solana 12H - $1,590": {
        "mode": "api",
        "service_name": "dex-trending",
        "order_type_id": "dex-trending-sol-12h",
        "plan_name": "Solana 12H",
        "client_price": CLIENT_PRICES["dex-trending-sol-12h"],
        "supplier_price": SUPPLIER_PRICES["dex-trending-sol-12h"],
        "needs_quantity": False,
        "needs_speed": False,
        "category": "DEX Screener Trending",
    },
    "⚡ EVM 24H (ETH/BSC/Base/Other) - $1,390": {
        "mode": "api",
        "service_name": "dex-trending",
        "order_type_id": "dex-trending-evm-24h",
        "plan_name": "EVM 24H",
        "client_price": CLIENT_PRICES["dex-trending-evm-24h"],
        "supplier_price": SUPPLIER_PRICES["dex-trending-evm-24h"],
        "needs_quantity": False,
        "needs_speed": False,
        "category": "DEX Screener Trending",
    },

    "🔎 Gecko Search Trending (24H) - $249": {
        "mode": "api",
        "service_name": "gecko-trending",
        "order_type_id": "gecko-search",
        "plan_name": "Gecko Search Trending",
        "client_price": CLIENT_PRICES["gecko-search"],
        "supplier_price": SUPPLIER_PRICES["gecko-search"],
        "needs_quantity": False,
        "needs_speed": False,
        "category": "GeckoTerminal Trending",
    },
    "📄 Gecko Pool Page Trending (24H) - $249": {
        "mode": "api",
        "service_name": "gecko-trending",
        "order_type_id": "gecko-pool",
        "plan_name": "Gecko Pool Page Trending",
        "client_price": CLIENT_PRICES["gecko-pool"],
        "supplier_price": SUPPLIER_PRICES["gecko-pool"],
        "needs_quantity": False,
        "needs_speed": False,
        "category": "GeckoTerminal Trending",
    },
    "🦎 Gecko Full Trending (24H) - $399": {
        "mode": "api",
        "service_name": "gecko-trending",
        "order_type_id": "gecko-full",
        "plan_name": "Gecko Full Trending",
        "client_price": CLIENT_PRICES["gecko-full"],
        "supplier_price": SUPPLIER_PRICES["gecko-full"],
        "needs_quantity": False,
        "needs_speed": False,
        "category": "GeckoTerminal Trending",
    },
}

MANUAL_ORDER_TYPES = {
    "📈 DexTools HOT 10 — SOL ($1,690)": {
        "service_name": "manual-dextools",
        "manual_key": "manual-dextools-sol",
        "plan_name": "DexTools HOT 10 — SOL",
        "client_price": CLIENT_PRICES["manual-dextools-sol"],
        "supplier_price": SUPPLIER_PRICES["manual-dextools-sol"],
        "category": "DexTools HOT 10",
    },
    "📈 DexTools HOT 10 — EVM ($1,190)": {
        "service_name": "manual-dextools",
        "manual_key": "manual-dextools-evm",
        "plan_name": "DexTools HOT 10 — EVM",
        "client_price": CLIENT_PRICES["manual-dextools-evm"],
        "supplier_price": SUPPLIER_PRICES["manual-dextools-evm"],
        "category": "DexTools HOT 10",
    },
    "📈 DexTools HOT 10 — Other ($790)": {
        "service_name": "manual-dextools",
        "manual_key": "manual-dextools-other",
        "plan_name": "DexTools HOT 10 — Other",
        "client_price": CLIENT_PRICES["manual-dextools-other"],
        "supplier_price": SUPPLIER_PRICES["manual-dextools-other"],
        "category": "DexTools HOT 10",
    },
    "👁 Birdeye Trending ($349)": {
        "service_name": "manual-birdeye",
        "manual_key": "manual-birdeye",
        "plan_name": "Birdeye Trending",
        "client_price": CLIENT_PRICES["manual-birdeye"],
        "supplier_price": SUPPLIER_PRICES["manual-birdeye"],
        "category": "Birdeye Trending",
    },
    "🧭 Solscan Trending ($399)": {
        "service_name": "manual-solscan",
        "manual_key": "manual-solscan",
        "plan_name": "Solscan Trending",
        "client_price": CLIENT_PRICES["manual-solscan"],
        "supplier_price": SUPPLIER_PRICES["manual-solscan"],
        "category": "Solscan Trending",
    },
    "🛡 Rugcheck Most Viewed ($249)": {
        "service_name": "manual-rugcheck",
        "manual_key": "manual-rugcheck",
        "plan_name": "Rugcheck Most Viewed",
        "client_price": CLIENT_PRICES["manual-rugcheck"],
        "supplier_price": SUPPLIER_PRICES["manual-rugcheck"],
        "category": "Rugcheck Most Viewed",
    },
    "💡 InsightX Trending ($249)": {
        "service_name": "manual-insightx",
        "manual_key": "manual-insightx",
        "plan_name": "InsightX Trending",
        "client_price": CLIENT_PRICES["manual-insightx"],
        "supplier_price": SUPPLIER_PRICES["manual-insightx"],
        "category": "InsightX Trending",
    },
}


# ---------------------------------
# API HELPERS
# ---------------------------------
def api_headers():
    return {
        "x-api-key": PANDABOOST_API_KEY,
        "Content-Type": "application/json",
    }


def pb_get(path, params=None):
    url = f"{PANDABOOST_BASE_URL}{path}"
    response = requests.get(url, headers=api_headers(), params=params, timeout=30)
    try:
        return response.status_code, response.json()
    except Exception:
        return response.status_code, {"success": False, "error": response.text}


def pb_post(path, payload):
    url = f"{PANDABOOST_BASE_URL}{path}"
    response = requests.post(url, headers=api_headers(), json=payload, timeout=30)
    try:
        return response.status_code, response.json()
    except Exception:
        return response.status_code, {"success": False, "error": response.text}


def get_balance():
    return pb_get("/balance")


def get_orders(page=1, limit=10):
    return pb_get("/orders", params={"page": page, "limit": limit})


def create_order(service_name, order_type_id, quantity, fields):
    payload = {
        "serviceName": service_name,
        "orderTypeId": order_type_id,
        "quantity": quantity,
        "fields": fields,
    }
    return pb_post("/orders", payload)


# ---------------------------------
# KEYBOARDS
# ---------------------------------
def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🚀 Boost Token", "📦 Launch Packages")
    keyboard.row("📊 My Orders", "💰 Balance")
    keyboard.row("💳 Deposit", "🤝 Affiliate")
    keyboard.row("❓ Help", "🛟 Support")
    return keyboard


def back_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🔙 Main Menu")
    return keyboard


def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("❌ Cancel")
    return keyboard


def category_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("DEX Screener Reactions")
    keyboard.row("DEX Screener Trending")
    keyboard.row("GeckoTerminal Trending")
    keyboard.row("DexTools HOT 10")
    keyboard.row("Birdeye Trending", "Solscan Trending")
    keyboard.row("Rugcheck Most Viewed", "InsightX Trending")
    keyboard.row("❌ Cancel")
    return keyboard


def reactions_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🚀 Rocket ($45 / 1000)")
    keyboard.row("🔥 Fire ($45 / 1000)")
    keyboard.row("🚩 Flag ($45 / 1000)")
    keyboard.row("💩 Poop ($45 / 1000)")
    keyboard.row("❌ Cancel")
    return keyboard


def trending_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("☀️ Solana 24H - $2,290")
    keyboard.row("🌙 Solana 12H - $1,590")
    keyboard.row("⚡ EVM 24H (ETH/BSC/Base/Other) - $1,390")
    keyboard.row("❌ Cancel")
    return keyboard


def gecko_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🔎 Gecko Search Trending (24H) - $249")
    keyboard.row("📄 Gecko Pool Page Trending (24H) - $249")
    keyboard.row("🦎 Gecko Full Trending (24H) - $399")
    keyboard.row("❌ Cancel")
    return keyboard


def dextools_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📈 DexTools HOT 10 — SOL ($1,690)")
    keyboard.row("📈 DexTools HOT 10 — EVM ($1,190)")
    keyboard.row("📈 DexTools HOT 10 — Other ($790)")
    keyboard.row("❌ Cancel")
    return keyboard


def packages_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🚀 Starter Launch Pack")
    keyboard.row("🔥 Trending Push Pack")
    keyboard.row("💎 Full Launch Campaign")
    keyboard.row("❌ Cancel")
    return keyboard


def speed_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🐢 Slow")
    keyboard.row("⚡ Normal")
    keyboard.row("🚀 Fast")
    keyboard.row("❌ Cancel")
    return keyboard


def confirm_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("✅ Confirm Order")
    keyboard.row("❌ Cancel")
    return keyboard


# ---------------------------------
# START / COMMON
# ---------------------------------
@bot.message_handler(commands=["start"])
def start(message):
    reset_user(message.chat.id)

    text = """
🚀 Welcome to DEXBOOST

Your crypto growth engine.

Boost your token on:

🔥 DEX Screener
📈 DexTools
🦎 GeckoTerminal
⚡ Reactions

Orders start instantly.
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu_keyboard()
    )


@bot.message_handler(commands=["order"])
def order_command(message):
    show_categories(message)


@bot.message_handler(commands=["deposit"])
def deposit_command(message):
    show_deposit(message)


@bot.message_handler(func=lambda m: m.text is not None and m.text == "🔙 Main Menu")
def go_main_menu(message):
    start(message)


@bot.message_handler(func=lambda m: m.text is not None and m.text == "❌ Cancel")
def cancel_action(message):
    reset_user(message.chat.id)
    bot.send_message(
        message.chat.id,
        "❌ Action cancelled.",
        reply_markup=main_menu_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "❓ Help")
def show_help(message):
    text = """
🛠 DEXBOOST Help

Menu buttons:

💰 Balance — check your current balance
🚀 Boost Token — place a new order
📊 My Orders — view your recent orders
💳 Deposit — deposit funds via crypto
🤝 Affiliate — earn commission
📦 Launch Packages — ready-made growth bundles

Shortcuts:
/start — main menu
/order — create order
/deposit — deposit balance
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=back_menu_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and "Support" in m.text)
def show_support(message):
    text = f"""
🛟 Support

Need help with your order or deposit?

Contact support:
{SUPPORT_USERNAME}
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=back_menu_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "🤝 Affiliate")
def show_affiliate(message):
    user_id = message.from_user.id
    referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

    text = f"""
🤝 Referral Program

Earn 10% commission on every order from users you refer.

Your referral link:
{referral_link}

👥 Referrals: 0
💰 Total Earned: $0.00
⏳ Pending Payout: $0.00
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=back_menu_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "💰 Balance")
def show_balance(message):
    try:
        status_code, result = get_balance()
        if status_code == 200 and result.get("success"):
            balance = result["data"].get("balance", 0)
            currency = result["data"].get("currency", "USD")
            text = f"""
💰 Your Balance

Balance: {balance} {currency}
"""
        else:
            text = f"""
💰 Your Balance

Could not load balance right now.
API error: {result.get('error', 'Unknown error')}
"""
    except Exception as e:
        text = f"""
💰 Your Balance

Could not load balance right now.
Error: {e}
"""

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("💳 Deposit")
    keyboard.row("📜 Transaction History")
    keyboard.row("🔙 Main Menu")

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=keyboard
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "📜 Transaction History")
def transaction_history(message):
    text = """
📜 Transaction History

No transactions yet.
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=back_menu_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "💳 Deposit")
def show_deposit(message):
    reset_user(message.chat.id)
    set_state(message.chat.id, {"mode": "waiting_deposit_amount"})

    text = """
💳 Deposit Funds

Enter the amount in USD:
$10 - $10,000
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=cancel_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "📊 My Orders")
def show_orders(message):
    try:
        status_code, result = get_orders(page=1, limit=10)
        if status_code == 200 and result.get("success"):
            orders = result["data"].get("orders", [])
            if not orders:
                text = """
📊 My Orders

You have no orders yet.
"""
            else:
                lines = ["📊 My Orders\n"]
                for order in orders[:10]:
                    lines.append(
                        f"• {order.get('publicId')} | "
                        f"{order.get('orderTypeName')} | "
                        f"{order.get('status')} | "
                        f"${order.get('amount')}"
                    )
                text = "\n".join(lines)
        else:
            text = f"""
📊 My Orders

Could not load orders.
API error: {result.get('error', 'Unknown error')}
"""
    except Exception as e:
        text = f"""
📊 My Orders

Could not load orders.
Error: {e}
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=back_menu_keyboard()
    )


# ---------------------------------
# PACKAGES
# ---------------------------------
@bot.message_handler(func=lambda m: m.text is not None and m.text == "📦 Launch Packages")
def show_packages(message):
    text = """
📦 Launch Packages

Ready-made bundles for token launches.

These packages are designed to:
• increase visibility
• create stronger first impression
• push discovery faster
• simplify launch setup

Choose a package:
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=packages_keyboard()
    )


@bot.message_handler(func=lambda m: m.text in PACKAGES)
def package_selected(message):
    package = PACKAGES[message.text]
    profit = package["client_price"] - package["supplier_cost"]

    text = f"""
📦 <b>{package['package_name']}</b>

{package['description']}

Client Price: <b>${package['client_price']}</b>
Internal Cost: <b>${package['supplier_cost']}</b>
Estimated Profit: <b>${profit}</b>

⚠️ Packages are handled through support right now.

Contact:
{SUPPORT_USERNAME}
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=back_menu_keyboard()
    )


# ---------------------------------
# CATEGORIES
# ---------------------------------
@bot.message_handler(func=lambda m: m.text is not None and m.text == "🚀 Boost Token")
def show_categories(message):
    reset_user(message.chat.id)
    set_state(message.chat.id, {"mode": "selecting_category"})

    text = """
🚀 Select Category

Select a service:
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=category_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "DEX Screener Reactions")
def category_reactions(message):
    reset_user(message.chat.id)
    set_state(message.chat.id, {"mode": "selecting_reaction_type"})

    text = """
DEX Screener Reactions — 3 modes

Slow 🐢 · Normal ⚡ · Fast 🚀
From $45/1000 · Instant start
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=reactions_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "DEX Screener Trending")
def category_trending(message):
    reset_user(message.chat.id)
    set_state(message.chat.id, {"mode": "selecting_trending_plan"})

    text = """
PandaBoost — DEX Screener Trending
🔥 Push your token to TOP 1–10!

What you get:
✅ Your token in top 1–10 on DEX Screener
✅ Visibility to thousands of active traders
✅ Organic discovery & volume growth
✅ Duration: 12h or 24h (selectable)

Pricing:
💠 SOL — $1,590/12h · $2,290/24h
💠 ETH / BSC / Base / Other — $1,390/24h

Requirements:
💠 SOL — LP 25k+ · VOL 300k+
💠 ETH/BSC — LP 30k+ · VOL 150k+
💠 Other chains — no req
💠 Token info must be updated

⚠️ Important:
💠 Mcap drops below $40k — order paused
💠 Price drops 80%+ — refund not valid
💠 If stats drop below requirements — DEX Screener may remove your token from trending. No refund.

📍 Select your plan below:
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=trending_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "GeckoTerminal Trending")
def category_gecko(message):
    reset_user(message.chat.id)
    set_state(message.chat.id, {"mode": "selecting_gecko_plan"})

    text = """
PandaBoost — GeckoTerminal Trending
🔥 Push your token to GeckoTerminal trends

What you get:
✅ Your token in GeckoTerminal trending
✅ Visibility to thousands of active traders
✅ Organic discovery & volume growth
✅ Duration: 24h

Pricing:
💠 Full Trending (Search + Pool) — $399/24h
💠 Search Trending — $249/24h
💠 Pool Page Trending — $249/24h

Requirements:
💠 Full Trending — Txs 1,000+ · VOL $20k+
💠 Pool Page Trending — Txs 1,000+ · VOL $20k+
💠 Search Trending — no requirements

⚠️ Important:
💠 Price drops 80%+ — refund not valid
💠 If stats drop below requirements — GeckoTerminal may remove your token from trending. No refund.

📍 Select your plan below:
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=gecko_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "DexTools HOT 10")
def category_dextools(message):
    reset_user(message.chat.id)
    set_state(message.chat.id, {"mode": "selecting_dextools_plan"})

    text = """
DexTools HOT 10

This service is available in manual mode right now.

Select your plan:
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=dextools_keyboard()
    )


@bot.message_handler(func=lambda m: m.text is not None and m.text == "Birdeye Trending")
def category_birdeye(message):
    prepare_manual_request(message, "👁 Birdeye Trending ($349)")


@bot.message_handler(func=lambda m: m.text is not None and m.text == "Solscan Trending")
def category_solscan(message):
    prepare_manual_request(message, "🧭 Solscan Trending ($399)")


@bot.message_handler(func=lambda m: m.text is not None and m.text == "Rugcheck Most Viewed")
def category_rugcheck(message):
    prepare_manual_request(message, "🛡 Rugcheck Most Viewed ($249)")


@bot.message_handler(func=lambda m: m.text is not None and m.text == "InsightX Trending")
def category_insightx(message):
    prepare_manual_request(message, "💡 InsightX Trending ($249)")


# ---------------------------------
# PLAN SELECTION
# ---------------------------------
@bot.message_handler(func=lambda m: m.text in API_ORDER_TYPES)
def api_plan_selected(message):
    plan = API_ORDER_TYPES[message.text]
    data = {
        "mode": "waiting_pair_address",
        **plan
    }
    set_state(message.chat.id, data)

    if "client_price" in plan:
        price_text = f"${plan['client_price']}"
    else:
        price_text = f"${plan['client_unit_price']} per unit"

    text = f"""
Enter your Pair Address:

⚠️ Make sure it's the PAIR address, not the token.

Selected:
{plan['plan_name']}
Price:
{price_text}
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=cancel_keyboard()
    )


@bot.message_handler(func=lambda m: m.text in MANUAL_ORDER_TYPES)
def manual_plan_selected(message):
    plan = MANUAL_ORDER_TYPES[message.text]
    data = {
        "mode": "waiting_manual_pair_address",
        **plan
    }
    set_state(message.chat.id, data)

    text = f"""
Selected:
{plan['plan_name']}

Price:
${plan['client_price']}

Enter your Pair Address:

⚠️ Make sure it's the PAIR address, not the token.
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=cancel_keyboard()
    )


def prepare_manual_request(message, key_name):
    plan = MANUAL_ORDER_TYPES[key_name]
    data = {
        "mode": "waiting_manual_pair_address",
        **plan
    }
    set_state(message.chat.id, data)

    text = f"""
Selected:
{plan['plan_name']}

Price:
${plan['client_price']}

Enter your Pair Address:

⚠️ Make sure it's the PAIR address, not the token.
"""
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=cancel_keyboard()
    )


# ---------------------------------
# API FLOW
# ---------------------------------
@bot.message_handler(func=lambda m: get_state(m.chat.id).get("mode") == "waiting_pair_address")
def process_pair_address(message):
    pair_address = message.text.strip()
    state = get_state(message.chat.id)
    state["pair_address"] = pair_address

    if state.get("needs_quantity"):
        state["mode"] = "waiting_quantity"
        set_state(message.chat.id, state)

        bot.send_message(
            message.chat.id,
            "Enter quantity:\n\nFor reactions allowed range is 100 to 1000.",
            reply_markup=cancel_keyboard()
        )
        return

    build_confirmation(message.chat.id)


@bot.message_handler(func=lambda m: get_state(m.chat.id).get("mode") == "waiting_quantity")
def process_quantity(message):
    state = get_state(message.chat.id)

    try:
        quantity = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Please enter a valid number.")
        return

    if quantity < 100 or quantity > 1000:
        bot.send_message(message.chat.id, "❌ Quantity must be between 100 and 1000.")
        return

    state["quantity"] = quantity

    if state.get("needs_speed"):
        state["mode"] = "waiting_speed"
        set_state(message.chat.id, state)

        bot.send_message(
            message.chat.id,
            "Choose speed:",
            reply_markup=speed_keyboard()
        )
        return

    set_state(message.chat.id, state)
    build_confirmation(message.chat.id)


@bot.message_handler(func=lambda m: get_state(m.chat.id).get("mode") == "waiting_speed")
def process_speed(message):
    speed_map = {
        "🐢 Slow": "slow",
        "⚡ Normal": "normal",
        "🚀 Fast": "fast",
    }

    if message.text not in speed_map:
        bot.send_message(message.chat.id, "❌ Please choose speed using the buttons.")
        return

    state = get_state(message.chat.id)
    state["speed"] = speed_map[message.text]
    set_state(message.chat.id, state)

    build_confirmation(message.chat.id)


def build_confirmation(chat_id):
    state = get_state(chat_id)
    pair_address = state.get("pair_address", "")
    plan_name = state.get("plan_name", "Unknown")
    category = state.get("category", "Unknown")
    quantity = state.get("quantity", 1)

    if "client_unit_price" in state:
        client_total = round(quantity * state["client_unit_price"], 2)
        supplier_total = round(quantity * state["supplier_unit_price"], 2)
    else:
        client_total = state.get("client_price", 0)
        supplier_total = state.get("supplier_price", 0)

    profit = round(client_total - supplier_total, 2)

    speed_line = ""
    if state.get("needs_speed"):
        speed_line = f"\nSpeed: {state.get('speed', 'normal')}"

    text = f"""
✅ Order Summary

Category: {category}
Plan: {plan_name}
Pair:
<code>{pair_address}</code>
Quantity: {quantity}{speed_line}

Client Price: ${client_total}
Supplier Cost: ${supplier_total}
Estimated Profit: ${profit}

Press Confirm to proceed.
"""
    state["mode"] = "waiting_confirm_api_order"
    state["client_total"] = client_total
    state["supplier_total"] = supplier_total
    state["estimated_profit"] = profit
    set_state(chat_id, state)

    bot.send_message(
        chat_id,
        text,
        reply_markup=confirm_keyboard()
    )


@bot.message_handler(func=lambda m: get_state(m.chat.id).get("mode") == "waiting_confirm_api_order" and m.text == "✅ Confirm Order")
def confirm_api_order(message):
    state = get_state(message.chat.id)
    create_api_order_and_respond(message, state)


# ---------------------------------
# MANUAL FLOW
# ---------------------------------
@bot.message_handler(func=lambda m: get_state(m.chat.id).get("mode") == "waiting_manual_pair_address")
def process_manual_pair_address(message):
    pair_address = message.text.strip()
    state = get_state(message.chat.id)
    profit = state["client_price"] - state["supplier_price"]

    text = f"""
📝 Manual Request Created

Service: {state.get('plan_name')}
Client Price: ${state.get('client_price')}
Supplier Cost: ${state.get('supplier_price')}
Estimated Profit: ${profit}

Pair Address:
<code>{pair_address}</code>

This service is currently handled manually.
Please contact support to process it:
{SUPPORT_USERNAME}
"""
    reset_user(message.chat.id)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu_keyboard()
    )


# ---------------------------------
# DEPOSIT FLOW
# ---------------------------------
@bot.message_handler(func=lambda m: get_state(m.chat.id).get("mode") == "waiting_deposit_amount")
def process_deposit_amount(message):
    amount = message.text.strip()

    text = f"""
💳 Deposit Request Created

Amount: ${amount}

The crypto deposit flow will be connected next.
For now, contact support:
{SUPPORT_USERNAME}
"""
    reset_user(message.chat.id)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu_keyboard()
    )


# ---------------------------------
# CREATE ORDER
# ---------------------------------
def create_api_order_and_respond(message, state):
    try:
        service_name = state["service_name"]
        order_type_id = state["order_type_id"]
        pair_address = state["pair_address"]

        if state.get("needs_quantity"):
            quantity = int(state["quantity"])
        else:
            quantity = 1

        fields = {
            "pair_address": pair_address
        }

        if state.get("needs_speed"):
            fields["speed"] = state.get("speed", "normal")

        status_code, result = create_order(
            service_name=service_name,
            order_type_id=order_type_id,
            quantity=quantity,
            fields=fields
        )

        if status_code == 200 and result.get("success"):
            data = result.get("data", {})
            order = data.get("order", {})
            payment = data.get("payment", {})

            text = f"""
✅ Order Created Successfully

Service: {state.get('plan_name')}
Public ID: <code>{order.get('publicId')}</code>
Status: {order.get('status')}

Client Price: ${state.get('client_total')}
Supplier Charged: ${payment.get('amount')}
Estimated Profit: ${round(state.get('client_total', 0) - float(payment.get('amount', 0)), 2)}

New Supplier Balance: {data.get('newBalance')} USD
"""
        else:
            text = f"""
❌ Order Failed

Service: {state.get('plan_name')}

Error:
{result.get('error', 'Unknown API error')}
"""
    except Exception as e:
        text = f"""
❌ Order Failed

Unexpected error:
{e}
"""

    reset_user(message.chat.id)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu_keyboard()
    )


# ---------------------------------
# FALLBACK
# ---------------------------------
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "I didn’t understand that. Please use the menu below.",
        reply_markup=main_menu_keyboard()
    )


print("Bot is running...")

while True:
    try:
        bot.infinity_polling(timeout=30, long_polling_timeout=30)
    except Exception as e:
        print("Bot crashed:", e)
        time.sleep(5)