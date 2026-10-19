"""Generate AsyncSample.cs with unique class/struct async method parameters."""

from pathlib import Path


FUNCTION_COUNT = 500
OUTPUT_PATH = Path(__file__).with_name("AsyncSample.cs")


def generate() -> str:
    lines = [
        "using System;",
        "using System.Threading.Tasks;",
        "",
        "public static class AsyncSample",
        "{",
        "    public static async Task Run()",
        "    {",
    ]

    for index in range(1, FUNCTION_COUNT + 1):
        suffix = f"{index:04d}"
        lines.append(
            f"        await Function{suffix}(new AsyncClass{suffix}(), new AsyncStruct{suffix}({index}));"
        )
        if index % 100 == 0:
            lines.append(
                f'        Console.WriteLine("Completed {index} of {FUNCTION_COUNT} async functions.");'
            )

    lines.extend(
        [
            "",
            f'        Console.WriteLine("All {FUNCTION_COUNT} async functions completed.");',
            "    }",
            "",
        ]
    )

    for index in range(1, FUNCTION_COUNT + 1):
        suffix = f"{index:04d}"
        lines.extend(
            [
                f"    private sealed class AsyncClass{suffix}",
                "    {",
                f"        public int Value {{ get; }} = {index};",
                "    }",
                "",
                f"    private readonly struct AsyncStruct{suffix}",
                "    {",
                "        public int Value { get; }",
                "",
                f"        public AsyncStruct{suffix}(int value)",
                "        {",
                "            Value = value;",
                "        }",
                "    }",
                "",
                f"    private static async Task Function{suffix}(",
                f"        AsyncClass{suffix} classParameter,",
                f"        AsyncStruct{suffix} structParameter)",
                "    {",
                "        ArgumentNullException.ThrowIfNull(classParameter);",
                "        _ = classParameter.Value;",
                "        _ = structParameter.Value;",
                "        await Task.Yield();",
                "    }",
                "",
            ]
        )

    lines.append("}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    OUTPUT_PATH.write_text(generate(), encoding="utf-8", newline="\n")
    print(f"Generated {FUNCTION_COUNT} async functions in {OUTPUT_PATH}.")
