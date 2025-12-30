# 🗑️ TeleGarbo

**TeleGarbo** is a command-line tool designed to **disrupt credential harvesters that rely on Telegram bots**.

Unlike tools that simply spam or delete messages — actions that are obvious and easy for a threat actor to work around — TeleGarbo takes a **stealthier approach** by **feeding convincing fake credentials while silently removing real harvested ones**.

---

## 🧠 How It Works

TeleGarbo continuously injects **fake credentials** into a Telegram chat used by a credential harvesting bot, while monitoring message IDs to detect and remove **legitimate harvested credentials**.

### Key behaviors:
- Generates **realistic-looking fake credentials**
- Posts them at **random intervals**
- Detects when new (legitimate) credentials appear
- **Deletes those real credentials**, leaving only fake data behind

The result:  
👉 The attacker’s dataset becomes unreliable without immediately raising suspicion.

---

## ✉️ Fake Credential Generation

### Email addresses
Emails are randomly generated using two common formats:
- `john.smith@example.com`
- `jsmith@example.com`

**Email domains** are constructed from:
- `business-names.txt` (company names)
- `extensions.txt` (domain extensions)

---

### Passwords
Passwords are randomly selected from:
- `rockyou.txt`

This ensures generated credentials look realistic and consistent with common password patterns.

---

## ⏱️ Posting Logic

- Fake credentials are posted at **random intervals between 2 and 20 minutes**
- When the first message is sent, TeleGarbo records its **Telegram message ID**
- On each subsequent post:
  - If message IDs increase normally → nothing happens
  - If there is a **gap in message IDs**:
    - This indicates another message was posted (likely real harvested credentials)
    - TeleGarbo **deletes the skipped message IDs**

✅ This ensures **only fake credentials remain** in the chat.

---

## 🚀 Usage

TeleGarbo requires **two arguments**:
- Telegram **bot token**
- Target **chat ID**

```bash
python TeleGarbo.py -t <BOT_TOKEN> -c <CHAT_ID>
