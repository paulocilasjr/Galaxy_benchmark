For long-running asynchronous work(for example, running galaxy jobs):
- functions.wait MUST use yield_time_ms >= 300000; prefer 1800000.
- The outer functions.exec yield must exceed the nested wait by 30000 ms.
- Do not wake merely to report that work is still running.
