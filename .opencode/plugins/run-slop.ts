import { spawn } from "node:child_process";

import { Plugin } from "@opencode/plugin";

type RunSlopInput = { path: string };

type RunSlopResult = {
  stdout: string;
  stderr: string;
  exitCode: number;
};

function runSlop(projectRoot: string, path: string): Promise<RunSlopResult> {
  return new Promise((resolve) => {
    const child = spawn("uv", ["run", "--no-active", "sloperator.py", path], {
      cwd: projectRoot,
    });

    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk: string) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk: string) => {
      stderr += chunk;
    });

    child.on("error", (error) => {
      resolve({ stdout, stderr: stderr + error.message, exitCode: 127 });
    });

    child.on("close", (code, signal) => {
      resolve({ stdout, stderr, exitCode: code ?? (signal ? 1 : 0) });
    });
  });
}

export default Plugin.define({
  id: "sloperator.run-slop",
  setup: async (ctx) => {
    const projectRoot = ctx.location.project.canonical || ctx.location.directory;

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang program with Sloperator and return its stdout, stderr, and exit code as JSON.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "Path to the .slop file, absolute or relative to the project root.",
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { path } = input as RunSlopInput;
          const result = await runSlop(projectRoot, path);
          return { content: JSON.stringify(result, null, 2) };
        },
      });
    });
  },
});
