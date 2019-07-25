# aiorunner

Hello, world
-------------

```
import asyncio
from aiorunner import AioRunner

async def main():
    script = """await asyncio.sleep(1)
print("Hello, world")
return "Thanks"
"""

    try:
        response = await AioRunner(script)
        print(response)
    except AioRunnerException as e:
        print(e)

asyncio.run(main())
```
