# 01 · The model never runs anything

**Goal:** understand what tool use really is: the model *requests*, your code *decides and executes*.
**Opens with:** a sentence that's wrong · **Thread:** who decides what · **Closes with:** a rule
**Misconception:** "The model ran our SQL query and deleted the rows."
**Analogy:** your ESP32 and the infrared remote
**Est. length:** ~6 min

---

### Beat 1 · Hook (a wrong sentence)
**Screen:** A Slack-style message from a teammate: *"The model ran our SQL query and deleted 300 rows 😱"*. The word "ran" is underlined.

**Narration:**
Here's a message you might see in a team channel one day: "The model ran our SQL query and deleted three hundred rows." It sounds plausible, and almost everybody says it this way. But one word is wrong, and by the end of this lesson you'll know which one, and why it changes who you should blame and where the fix goes.

### Beat 2 · Back to the constraint
**Screen:** The "text in → LLM → text out" box from lesson 00.

**Narration:**
Remember the constraint: the model only produces text. So how can it ever "use" a database? It can't, not directly. What it can do is produce a very particular kind of text.

### Beat 3 · The naive picture
**Screen:** A wrong diagram, drawn on purpose: `LLM → (arrow labelled "executes") → Database`. A red stamp: **NOT HOW IT WORKS**.

**Narration:**
The picture most people carry around looks like this: the model reaches into the database and does something. If that were true, the only way to make it safe would be to make the model behave, with better prompts, sterner instructions and fingers crossed. Keep that picture in mind, because we're going to replace it.

### Beat 4 · Intuition (analogy)
**Screen:** A hand-drawn infrared remote pointing at a small ESP32 board, which is wired to an RGB light bulb. Labels: remote → "emits a code"; ESP32 → "decides what the code means"; bulb → "the actual effect".

**Narration:**
Think about the infrared LED project. When you press a button on the remote, the remote doesn't turn on the light. It can't. It sends a code, a pattern of pulses that means "red" or "brighter". The receiver, your ESP32, reads that code and decides what to do with it. It could switch the colour, or log it, or ignore it entirely if you programmed it to. The remote only *asks*. The board *acts*.
A language model with tools is the remote. It sends codes, and your program is the board.

### Beat 5 · The concept: tool use
**Screen:** The real diagram, built step by step:
1. `Your code → LLM`: "question + list of tools (name, description, input schema)"
2. `LLM → Your code`: a structured request (shown as a small JSON card)
3. `Your code → Tool function`: "validate, then run (or refuse)"
4. `Your code → LLM`: "the result"

JSON card on screen:
```json
{"toolUse": {"name": "get_order_status",
             "input": {"order_id": "A-1005"}}}
```

**Narration:**
Here's how it really works. Along with the question, your code sends the model a short menu of tools. Each one has a name, a description in plain language and a schema for its arguments. When the model decides a tool would help, it doesn't answer in prose. It produces a structured request: "call `get_order_status` with order ID A-1005." That small block of JSON is all it does.
Your code reads that request. It checks it, runs the real function (or decides not to) and sends the result back. Then the model writes its answer using real data instead of a guess.
That's tool use. Some APIs call it function calling, but it's the same thing.

### Beat 6 · The split of responsibilities
**Screen:** Two columns.
**The model decides:** whether a tool is needed · which tool · with what arguments
**Your code decides:** how it runs · what it's allowed to touch · what goes back

**Narration:**
This split is the whole design, so it's worth saying slowly. The model decides *whether* a tool is needed, *which* one and *with what arguments*. Your code decides *how* it runs, *what* it's allowed to touch and *what* information goes back to the model.
Back to the first question from lesson zero: who should calculate the refund? Your code, every time. The model's job is to recognise that a refund needs calculating and to pass the right order ID. The arithmetic and the policy belong in code you can test.

### Beat 7 · Fixing the sentence
**Screen:** The teammate's message again. "ran" is crossed out and replaced with "*requested*, and our code ran". Below it: *Fix → the tool and its permissions, not the prompt.*

**Narration:**
Now the sentence from the start. "The model ran our SQL query" is wrong. The model *requested* a query, and *our code* ran it. That isn't nitpicking, because it moves the fix. If the model executed things, you'd fix it in the prompt. Since your code executes them, the fix lives in the tool. Use a read-only tool with read-only credentials, put validation in code, and add a confirmation step before anything destructive. A sterner system prompt doesn't fix it.

### Beat 8 · Limits: a schema is a contract, not a guarantee
**Screen:** The schema for `calculate_refund` with `reason` as an enum: `damaged | late | changed_mind`. A model request appears with `"reason": "broken"`, highlighted in red. A second note: *"within 30 days" → can't be expressed in a schema*.

**Narration:**
One honest limit. The schema you give the model is guidance. Models follow it very well, but not perfectly: they can send a value that isn't in your list, or an order ID that looks right and doesn't exist. Some providers offer a strict mode that forces the shape. Even then, the schema can't check your business rules, such as "only within thirty days of delivery". So your tool validates its inputs anyway, the same way a backend never trusts a form just because the frontend has validation.

### Beat 9 · Retrieval pause
**Screen:** *"A model 'sends an email'. List the three things your code decided."*

**Narration:**
Quick check. Somebody says "the agent sent an email to the customer". Using the split we just saw, name three things your code decided in that moment. Pause, answer, then continue. …
Here's mine: whether to send it at all, which credentials and account to send it from, and what to report back to the model afterwards.

### Beat 10 · Close (rule) and bridge
**Screen:** Big sticky note: **"The model asks. Your code acts."** Then a new customer question appears: *"A-1005 arrived damaged. How much do I get back?"*, with two tool icons below it: `get_order_status` → `calculate_refund`.

**Narration:**
The model asks, and your code acts. Everything else in this course builds on that line.
Now look at our customer's question again. Answering it needs two tools: first look up the order, then calculate the refund. The second depends on the first. A single request can't do that, so next we need a loop.
