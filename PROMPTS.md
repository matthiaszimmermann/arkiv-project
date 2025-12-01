# 🗣️ PROMPTS.md - AI Conversation Starters for Arkiv

**Use these prompts with GitHub Copilot, Cursor, Claude, or any AI coding assistant.**

Just copy-paste these into your AI chat to build Arkiv apps quickly!

---

## 🎯 How to Use This File

1. **Pick a prompt** below that matches what you want to build
2. **Copy the entire prompt** (including the context)
3. **Paste into your AI assistant** (Copilot Chat, Cursor, etc.)
4. **Review the generated code** and run it with `uv run python your_file.py`
5. **Iterate** - Ask follow-up questions to refine the code

**Pro Tip:** The prompts include context about this repository to help AI generate correct code.

---

## 📝 Basic Operations

### Store a Simple Message

```
Using the Arkiv SDK in this repository:

Create a Python script that stores a text message "Hello from my app!" on-chain 
with a 1-hour expiration. Print the entity key and confirmation when done.

Make sure to use snake_case naming (entity_key, expires_in, content_type).
```

### Store JSON Data

```
Using the Arkiv SDK in this repository:

Create a script that stores a user profile as JSON with these fields:
- name: "Alice"
- age: 25
- email: "alice@example.com"

Store it with a 7-day expiration. Then retrieve and print the data.

Use snake_case naming and handle the JSON encoding/decoding properly.
```

### Update Existing Data

```
Using the Arkiv SDK in this repository:

Show me how to:
1. Create an entity with payload "Initial data"
2. Update it to "Modified data" 
3. Print both versions to verify the update worked

Use proper snake_case naming (entity_key, expires_in, etc.).
```

### Query Multiple Entities

```
Using the Arkiv SDK in this repository:

Create a script that:
1. Stores 3 entities with different messages
2. Queries all entities owned by the current account
3. Prints each message

Use the correct query syntax with $owner attribute and snake_case.
```

---

## 🚀 Project Ideas (Start Building!)

### 1. Simple Todo List

```
Using the Arkiv SDK in this repository:

Build a command-line todo list app with these features:
- Add a todo item (stores on-chain with status="pending")
- List all todos (queries by owner)
- Mark a todo as done (updates entity)
- Delete a todo

Use snake_case naming throughout. Store todos as JSON with fields:
{
  "task": "description",
  "status": "pending" or "done",
  "created": timestamp
}

Add custom attributes for filtering: status, created_date
```

### 2. On-Chain Message Board

```
Using the Arkiv SDK in this repository:

Create a simple message board where users can:
- Post a message with a category (tech/sports/random)
- View all messages in a category
- View their own messages

Store messages as JSON with:
{
  "author": account_address,
  "message": text,
  "category": string,
  "timestamp": time
}

Use custom attributes for category to enable filtering.
Use snake_case naming (entity_key, content_type, expires_in).
```

### 3. Simple Voting System

```
Using the Arkiv SDK in this repository:

Build a voting app that:
- Creates a poll with a question and options
- Lets users vote (one entity per vote)
- Counts votes and displays results

Store votes as JSON with:
{
  "poll_id": unique_id,
  "option": selected_option,
  "voter": account_address
}

Use query_entities to count votes by option.
Use snake_case naming throughout.
```

### 4. Event RSVP System

```
Using the Arkiv SDK in this repository:

Create an event RSVP system that:
- Creates an event with name, date, and max attendees
- Lets users RSVP (stores their response)
- Lists all attendees for an event
- Checks if event is full

Store RSVPs as JSON with:
{
  "event_id": string,
  "attendee_name": string,
  "attendee_email": string,
  "status": "going" or "maybe"
}

Use custom attributes event_id and status for querying.
```

### 5. Simple Leaderboard

```
Using the Arkiv SDK in this repository:

Build a gaming leaderboard that:
- Records player scores (player name + score)
- Queries top 10 players by score
- Updates a player's score
- Shows player rank

Store scores as JSON with:
{
  "player_name": string,
  "score": integer,
  "game": string,
  "timestamp": time
}

Use custom attributes: game, score for filtering.
Note: You'll need to sort client-side since Arkiv queries don't support ORDER BY.
```

### 6. Bookmark Manager

```
Using the Arkiv SDK in this repository:

Create a bookmark manager that:
- Saves URLs with title and tags
- Lists all bookmarks
- Filters bookmarks by tag
- Deletes bookmarks

Store bookmarks as JSON:
{
  "url": string,
  "title": string,
  "tags": ["tag1", "tag2"],
  "saved_date": timestamp
}

Use custom attribute 'tags' for filtering (query for specific tag).
```

---

## 🔍 Querying & Filtering

### Filter by Owner

```
Using the Arkiv SDK in this repository:

Show me how to query all entities owned by the current account.

Use the correct query syntax: $owner with snake_case.
Print each entity's key and payload.
```

### Filter by Custom Attribute

```
Using the Arkiv SDK in this repository:

Create a script that:
1. Stores 5 entities with custom attribute "priority" (values: 1-5)
2. Queries only entities where priority > 3
3. Prints the results

Use correct query syntax (no $ for custom attributes).
```

### Combined Filters

```
Using the Arkiv SDK in this repository:

Show me how to query entities that match ALL of these:
- Owned by current account ($owner)
- Type is "message" (custom attribute)
- Status is "active" (custom attribute)

Use correct AND query syntax with snake_case naming.
```

---

## 🔔 Events & Real-Time Updates

### Watch for New Entities

```
Using the Arkiv SDK in this repository:

Create a script that:
1. Watches for new entities being created
2. Prints a message when a new entity is detected
3. Shows the entity key and owner

Use the high-level watch_entity_created() method (not raw contract events).
Use typed callbacks with CreateEvent and TxHash.
```

### Monitor Updates

```
Using the Arkiv SDK in this repository:

Show me how to monitor entity updates in real-time.

Use watch_entity_updated() and print:
- Entity key
- Old expiration block
- New expiration block

Use proper types: UpdateEvent and TxHash.
```

---

## 🔧 Advanced Patterns

### Batch Create Multiple Entities

```
Using the Arkiv SDK in this repository:

Create a script that stores 10 entities in a loop with different messages.
For each entity, print its key and the block number it was created in.

Use snake_case naming (entity_key, expires_in).
```

### Error Handling

```
Using the Arkiv SDK in this repository:

Show me how to properly handle errors when:
1. Creating an entity (check if payload is too large)
2. Reading an entity (handle "not found" case)
3. Updating an entity (handle ownership errors)

Use entity_exists() to check before reading.
Use try/except for error handling.
```

### Working with Large Data

```
Using the Arkiv SDK in this repository:

I have a 200KB file. Show me how to:
1. Check if it's too large for direct storage
2. Split it into chunks (90KB each)
3. Store each chunk as a separate entity
4. Retrieve and reassemble the chunks

Explain the 100KB transaction limit and why chunking is needed.
```

---

## 🌐 Web3 Integration

### Get Current Block Number

```
Using the Arkiv SDK in this repository:

Show me how to:
1. Get the current block number
2. Calculate when an entity will expire (block number + blocks until expiration)
3. Print human-readable time remaining

Use client.eth.block_number and proper time conversions.
```

### Check Account Balance

```
Using the Arkiv SDK in this repository:

Create a script that:
1. Checks the current account's balance
2. Prints it in ETH (not wei)
3. Warns if balance is below a threshold

Use client.eth.get_balance() and proper unit conversion.
```

---

## 🐛 Debugging & Troubleshooting

### Why Isn't My Query Working?

```
I'm trying to query entities with this code:
[paste your code here]

But I'm getting [error or unexpected result].

This is in the Arkiv Python starter repository. 
Can you help me debug this? Remember to use:
- snake_case for Python methods
- $snake_case for system query attributes
- No $ for custom attributes in queries
```

### My Entity Disappeared

```
Using the Arkiv SDK in this repository:

I created an entity but now I can't retrieve it. It says "Entity not found".

Show me how to:
1. Check if an entity exists before reading
2. Check if it expired (compare current block to expires_at_block)
3. Set longer expiration times to prevent this

Use entity_exists() and proper expiration handling.
```

### Naming Convention Confusion

```
I'm confused about when to use snake_case vs camelCase in Arkiv.

Can you explain and show examples of:
1. Python SDK method calls (snake_case)
2. Query syntax ($ + snake_case for system, no $ for custom)
3. Contract events (camelCase)
4. Entity attributes (snake_case)

Reference the AGENTS.md file in this repository for the rules.
```

---

## 📚 Learn More

### Explain This Concept

```
Using the Arkiv SDK documentation in this repository:

Explain [concept] in simple terms with a code example.

Concepts you can ask about:
- What is an entity?
- What is expires_in?
- What are custom attributes?
- How do queries work?
- What is a receipt?
- What is an entity_key?
```

### Show Me Best Practices

```
Using the Arkiv SDK in this repository:

Show me best practices for:
[pick one: storing sensitive data / handling large files / error recovery / 
          gas optimization / security / production deployment]

Include code examples and explanations.
```

---

## 🎯 Template Prompt (Customize This)

```
Using the Arkiv SDK in this repository:

I want to build [describe your app idea].

It should:
- [Feature 1]
- [Feature 2]  
- [Feature 3]

Please create a complete Python script with:
- Proper snake_case naming (entity_key, content_type, expires_in)
- Error handling
- Comments explaining each step
- Example output

Use the patterns from the examples in src/arkiv_starter/.
```

---

## 💡 Tips for Better AI Responses

1. **Always mention "Using the Arkiv SDK in this repository"** - This tells AI to use the context from AGENTS.md

2. **Be specific about naming** - Say "use snake_case naming" to avoid camelCase mistakes

3. **Ask for explanations** - Add "explain each step with comments" to understand the code

4. **Request error handling** - Add "include error handling" for production-ready code

5. **Iterate** - After getting code, ask:
   - "Can you make this more efficient?"
   - "Add error handling for [scenario]"
   - "Explain why you used [pattern]"

6. **Reference examples** - Say "like in 02_entity_crud.py" to guide AI to correct patterns

---

## 🆘 Still Stuck?

If AI-generated code isn't working:

1. **Check the error message** - Copy it into AI and ask for help
2. **Review AGENTS.md** - Make sure code follows naming conventions
3. **Run the examples** - Compare AI code to working examples (00-05)
4. **Ask simpler questions** - Break complex requests into smaller steps

**Remember:** AI assistants work best with clear, specific prompts that reference this repository's context!

---

*Happy prompting! 🚀*
