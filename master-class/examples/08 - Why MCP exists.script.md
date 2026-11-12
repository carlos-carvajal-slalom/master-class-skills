# 08 · The N×M problem: why MCP exists

**Goal:** understand the integration problem MCP solves, the host / client / server roles, and what MCP does *not* change.
**Opens with:** a multiplication · **Thread:** "isn't there something simpler?", weighing the options · **Closes with:** what MCP standardises, in one line
**Misconception:** "The model speaks MCP."
**Analogy:** USB
**Est. length:** ~8 min

---

### Beat 1 · Hook (a multiplication)
**Screen:** A grid builds up: 5 apps across the top (support agent, billing bot, IDE assistant, dashboard, Slack bot), 20 systems down the side (orders, CRM, Jira, Slack, files…). Every cell fills with a tiny connector icon. The counter in the corner reads **5 × 20 = 100**.

**Narration:**
Five AI apps in a company, and twenty systems they'd like to talk to: orders, the CRM, Jira, Slack, a few internal APIs. Without any standard, every app writes its own connector to every system. That's five times twenty, a hundred separate integrations, each with its own tool definitions, its own auth handling and its own bugs. And when the orders API changes, you fix it in five places.

### Beat 2 · The constraint
**Screen:** The same `get_order_status` tool drawn three times, slightly differently: as a Bedrock `toolSpec`, as an Anthropic `input_schema`, as an OpenAI `function`. Each lives *inside* its app's process.

**Narration:**
The same thing is happening in our lab. The order tools live *inside* the notebook, right next to the loop. They're written in the tool format of one specific API, and they run in the same process. That was fine for one agent. But the billing team uses a different framework, the IDE assistant uses a different model provider and the dashboard is written in TypeScript.

### Beat 3 · Option A: copy them everywhere
**Screen:** The three tools photocopied into five apps. A month later, two of the copies have drifted (one has the old 14-day refund rule).

**Narration:**
The first option is the obvious one: copy the tools into every app. It works on day one. A month later, one copy still has the old refund rule, another has a bug that was fixed somewhere else, and nobody knows which one is right.

### Beat 4 · Option B: a shared library
**Screen:** A package `ridgeline-tools` imported by the Python apps. The TypeScript dashboard and the off-the-shelf IDE assistant can't import it; a red ✗ on each.

**Narration:**
The second option is a shared library. Better, because there's one source of truth. But a library ties you to one language and one way of describing tools, and it still runs inside each app with that app's permissions. And it doesn't help at all with apps you didn't write, like an IDE assistant or a desktop chat app.

### Beat 5 · Option C: isn't OpenAPI enough?
**Screen:** An OpenAPI spec document. Arrows show it describes endpoints well. A side note: *"describes an API, but not how an AI app connects to it, discovers tools at runtime, or gets context and prompts alongside them"*. A small bridge icon: *"Gateways can turn an OpenAPI spec into an MCP server"*.

**Narration:**
Then the question you'd ask: we already have OpenAPI, so isn't that enough? OpenAPI is excellent at *describing* an HTTP API. What it doesn't define is a conversation between an AI application and a tool provider: connecting, agreeing on capabilities, discovering what's available right now, and serving data and prompt templates alongside the actions. And endpoint-by-endpoint tools are rarely the right shape for a model, as we saw in lesson three.
They aren't rivals. Managed gateways can take an OpenAPI spec and expose it *as* an MCP server. One describes the API, and the other is how agents plug into it.

### Beat 6 · The concept: MCP
**Screen:** The grid collapses. Now: 5 apps each with one generic "MCP client" plug on top; 20 systems each wrapped once as an "MCP server" below. Counter: **5 + 20 = 25**.

**Narration:**
**MCP**, the Model Context Protocol, is an open standard for exactly this. You wrap a system *once* as an **MCP server**. Any app that speaks MCP connects to it with a generic **MCP client**, whether that's a desktop chat app, an IDE, an agent framework, a managed gateway or your own notebook. Five apps plus twenty servers makes twenty-five pieces of work instead of a hundred.

### Beat 7 · Intuition (analogy)
**Screen:** Old desk drawer: a tangle of proprietary cables (one for the printer, one for the mouse, one for the camera). Then: a single USB port, and every device using it.

**Narration:**
It's the same move USB made. Before it, every printer, mouse and camera came with its own connector, and every computer needed a matching port. After it, the device manufacturer implements USB once, the computer implements USB once, and everything plugs into everything. MCP does that for AI apps and the systems they need.

### Beat 8 · Host, client, server
**Screen:** The architecture, built piece by piece:
- **Host** (big box): "your agent app": contains the **model** + the **agent loop** + **MCP client 1** + **MCP client 2**.
- Client 1 → *stdio* → **Server: orders_server.py** → order data.
- Client 2 → *HTTP* → **Server: remote (e.g. a managed gateway)** → APIs.

**Narration:**
Three roles. The **host** is the app the user interacts with. It owns the model and the agent loop (the loop from lesson two). Inside the host there's one **client** per server, a connection object that knows how to list, read and call. And the **server** is a separate program that exposes capabilities. It knows nothing about any model; it just answers requests.

### Beat 9 · The misconception: "the model speaks MCP"
**Screen:** The model emits the exact same `toolUse` card as in lesson two. The *host* catches it and translates: `toolUse(get_order_status)` → `tools/call get_order_status` → server. The result travels back and is translated into a normal tool result.

**Narration:**
Here's the misconception worth clearing up: the model doesn't speak MCP. It doesn't even know MCP exists. It emits the same tool request it always did, exactly like in lesson two. The *host* catches that request, translates it into an MCP call to the right server, and turns the answer back into an ordinary tool result.
So MCP doesn't change tool use. It standardises the plumbing *behind* tool use: where the tools live, how they're discovered and how they're called.

### Beat 10 · What you already know, mapped
**Screen:** A two-column mapping:
| Before (lesson 2) | With MCP |
|---|---|
| Tool definition in the notebook | Same name + description + schema, discovered from the server |
| `TOOL_FUNCTIONS[name](**args)` | `await session.call_tool(name, args)`, which runs in another process |
| Error result with `status: "error"` | Server reports the error → host passes it to the model the same way |

**Narration:**
And everything you learned still applies. A tool on an MCP server has the same three parts: a name, a description and a schema. Calling it looks almost identical, except the function runs in another process, or on another machine. Errors still go back to the model as information. The one real change is that the agent *discovers* its tools from the server at runtime instead of having them hard-coded.

### Beat 11 · Limits
**Screen:** Sticky note: *"MCP moves your tools. It doesn't improve them."*

**Narration:**
A limit to keep in mind: MCP moves your tools, it doesn't improve them. A vague description is just as vague when it comes from a server. Every principle from the tool-design lesson applies, and even more so when one server is shared by many agents you don't control.

### Beat 12 · Retrieval pause
**Screen:** *"In this lab: who decides to call `calculate_refund`? Who sends the MCP request? Who runs the refund logic?"*

**Narration:**
Three roles, three questions. Who *decides* to call `calculate_refund`? Who *sends* the MCP request? And who *runs* the refund logic? …
The model decides, by emitting a tool request. The host, through its MCP client, sends the request. The server runs the function.

### Beat 13 · Close and bridge
**Screen:** One line: **"MCP standardises the plumbing behind tool use, not tool use itself."** Then: the return policy document, floating near the server with a question mark: *tool? something else?*

**Narration:**
MCP standardises the plumbing behind tool use, not tool use itself.
And once tools live on a server, a new question comes up. Our return policy, the thirty-day rule and the percentages: should the model have to *call a tool* to read it? Or is there a better way for a server to provide it? Next: the three things a server can expose, and who controls each one.
