# 🚀 START HERE - Your First 5 Minutes with Arkiv

**Welcome!** This guide will get you from zero to storing data on blockchain in 5 minutes.

No blockchain experience needed. No complex setup. Just follow the steps.

---

## ✅ Prerequisites Check

Before you start, make sure you have:

- [ ] VS Code open with this project
- [ ] Reopened in Dev Container (click "Reopen in Container" when prompted)
- [ ] Terminal open in VS Code (View → Terminal)

**Don't have these?** Go back to [README.md](README.md) Quick Start section.

---

## 🎯 Your First Command (30 seconds)

In the VS Code terminal, paste this command:

```bash
uv run python -m arkiv_starter.00_hello_arkiv
```

Press **Enter** and watch the magic happen! ✨

You should see:

```
👋 Hello Arkiv! Storing your first message on-chain...

✅ Message stored on-chain!
   Address: 0x1234...
   Block: 42

📖 Message retrieved: 'Hello, Web3 world!'

🎉 Congratulations! You just used blockchain storage!
```

**🎉 Congratulations!** You just:
- Stored data on a blockchain
- Retrieved it back
- Proved it works

That's all it takes with Arkiv!

---

## 🤔 What Just Happened?

Let's break it down in plain English:

1. **`client = Arkiv()`** - Set up your connection (like opening a database)
2. **`create_entity()`** - Saved your message on-chain (like INSERT in SQL)
3. **`get_entity()`** - Read it back (like SELECT in SQL)

But unlike a regular database, this data is:
- ✅ Stored on a blockchain (decentralized)
- ✅ Publicly verifiable (anyone can check)
- ✅ Queryable (filter, search, paginate)

---

## 🧑‍💻 Your First Custom Message

Let's make it personal! Create a new file called `my_first_app.py`:

```python
from arkiv import Arkiv

client = Arkiv()

# Change this to YOUR message!
my_message = b"Hi, I'm learning blockchain!"

key, receipt = client.arkiv.create_entity(
    payload=my_message,
    expires_in=3600
)

entity = client.arkiv.get_entity(key)
if entity.payload:
    print(f"Stored: {entity.payload.decode()}")
```

Run it:
```bash
uv run python my_first_app.py
```

**💡 Experiment:**
- Change the message to anything you want
- Try emojis: `b"Hello 🌍"`

---

## 🤖 Using AI to Build (Optional)

If you have **GitHub Copilot** or **Cursor** installed:

### Method 1: Ask in Chat

Open Copilot Chat (Ctrl+Alt+I) and try these prompts:

**Beginner Prompt 1: Store JSON Data**
```
Using the Arkiv SDK in this repository, create a Python script that stores 
a user profile as JSON (name, age, email) and retrieves it back.
```

**Beginner Prompt 2: Store Multiple Messages**
```
Create a script that stores 3 different messages in Arkiv and then 
retrieves all messages owned by my account.
```

**Beginner Prompt 3: Simple Query**
```
Show me how to store messages with a "category" attribute, then query 
only messages where category="important".
```

### Method 2: Use Code Completion

Just start typing in a Python file:

```python
# Store a user profile in Arkiv
from arkiv import Arkiv

client = Arkiv()

# [Let Copilot suggest the rest!]
```

Press **Tab** to accept suggestions.

---

## 📖 Glossary (Simple Explanations)

**Confused by blockchain terms?** Here's plain English:

| Term | What It Means |
|------|---------------|
| **Entity** | A piece of data you store (like a database row) |
| **Entity Key** | The address where your data lives (like a URL) |
| **Payload** | Your actual data (text, JSON, whatever you want) |
| **Block** | A timestamp on the blockchain (like "saved at 3:45 PM") |
| **Expires In** | How long to keep the data (in seconds) |
| **On-chain** | Stored on the blockchain (permanent, public) |
| **Query** | Search/filter your data (like SQL WHERE) |
| **Receipt** | Proof that your transaction worked |
| **Account** | Your identity on the blockchain (like a username) |

---

## 🎓 Next Steps (Choose Your Path)

### Path 1: Learn More Examples (Guided)
Work through the numbered examples:
- ✅ `00_hello_arkiv.py` - You just did this!
- 📖 `01_clients.py` - Different ways to set up (5 min)
- 📝 `02_entity_crud.py` - Update and delete data (10 min)
- 🔍 `03_queries.py` - Search and filter (10 min)
- 🔔 `04_events.py` - Get notified of changes (15 min)
- 🌐 `05_web3_integration.py` - Mix with other Web3 stuff (10 min)

Run each one:
```bash
uv run python -m arkiv_starter.01_clients
uv run python -m arkiv_starter.02_entity_crud
# ... and so on
```

### Path 2: Build Something (Vibe Coding with AI)
Skip the examples and just build! See [PROMPTS.md](PROMPTS.md) for project ideas.

Use AI to help:
1. Pick a project idea from PROMPTS.md
2. Ask your AI assistant to build it
3. Run the code
4. Tweak and experiment

### Path 3: Read the Full Guide
Go to [README.md](README.md) for comprehensive documentation.

---

## 🆘 Help! Something Broke

### Error: "ModuleNotFoundError: No module named 'arkiv'"

**Fix:**
```bash
uv sync
```

Then: `Ctrl+Shift+P` → "Python: Select Interpreter" → choose `.venv`

### Error: "Docker not running"

**Fix:** Make sure Docker Desktop is running, then restart VS Code.

### Error: "Entity not found"

**Reason:** Your data expired (expired entities can't be read).

**Fix:** Set a longer `expires_in` (e.g., 3600 = 1 hour, 86400 = 1 day).

### My Code Doesn't Work

**Debug checklist:**
1. Did you run in dev container? (Look for "vscode@..." in terminal)
2. Did you use `uv run` to execute? (Not just `python`)
3. Did you copy the code exactly? (Check for typos)

**Still stuck?** Check [README.md](README.md#troubleshooting) troubleshooting section.

---

## 🎉 You're Ready!

You now know:
- ✅ How to store data on blockchain
- ✅ How to retrieve it back
- ✅ How to run Arkiv code
- ✅ Where to get help

**What's next?**
- Try building something (see PROMPTS.md)
- Learn advanced patterns (run the other examples)
- Deploy to testnet (see README.md production section)

**Happy coding!** 🚀

---

*Having fun? Star this repo on GitHub and tell others about Arkiv!*
