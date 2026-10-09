# Coding protocol A1: failed requests to the Galaxy interface

Each item is one failed request that an AI agent sent to a Galaxy interface (an MCP server wrapping usegalaxy.org). It gives the interface tool that was called, the returned status, the error text and a truncated copy of the request arguments. Classify each item independently. Do not open any other file and do not use the internet.

## 1. Failure class (choose one)

Requests rejected before a job ran:
- **A1 History context**: the tool form or request needed a Galaxy history and none, or an unusable one, was given.
- **A2 Tool not found**: the tool identifier does not exist or was guessed.
- **A3 Nested parameter structure**: conditional, repeat or nested parameter keys were structured wrongly.
- **A4 Parameter value or datatype**: a parameter value, option or input datatype failed validation.
- **A5 Identifier handling**: a wrong, foreign, truncated or undecodable dataset, history or job ID.
- **A6 UDT definition**: the user-defined tool (agent-written tool) definition was rejected by its schema.
- **A7 Upload or datatype registry**: an upload failed or the requested file extension or datatype was unknown.
- **A8 Server, transport or rate limit**: an HTML error page, time-out, closed transport, rate limit or server exception.

Jobs that failed during execution:
- **B1 Missing dependency in the UDT container**: a package, module or command was missing when the agent's code ran.
- **B2 Job error with no diagnostic**: the job failed and Galaxy returned no usable error message.
- **B3 Tool runtime error**: the tool wrote an error (stderr or traceback); from this record alone the cause could be the agent's input or the tool.
- **B4 Input format, compression or index**: the input was in the wrong format, compressed wrongly or lacked an index.
- **B5 Memory or resources**: out of memory, killed or resource limits.

Other:
- **X Other transport or tool exception**, **Z Cannot classify**.

## 2. What would most likely have prevented it (choose one or more)

- **API design**: a different interface design (for example, automatic history context, simpler parameter structures, ID validation).
- **Error diagnostics**: a clearer or more complete error message would have let the agent fix it.
- **Tool and parameter descriptions**: better tool or parameter documentation shown to the agent.
- **Datatypes and uploads**: better datatype or upload handling.
- **UDT support**: better UDT schema guidance or container dependencies.
- **Server capacity**: more server resources or reliability.
- **Agent error only**: no infrastructure change would plausibly have prevented it.
- **Cannot tell**.

## Output

For each item, one JSON object:

```json
{"code": "R001", "class": "A1|…|B5|X|Z", "prevent": ["Error diagnostics", "…"], "confidence": "high|moderate|low"}
```

Write all objects as a JSON list to the output file named in your assignment, and return a one-line summary.
