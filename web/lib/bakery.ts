import { spawn } from "node:child_process";
import path from "node:path";

const REPO_ROOT = path.resolve(process.cwd(), "..");

/**
 * Run the bakery Python CLI and return parsed JSON stdout.
 * Example: cli(["scale", "sourdough-loaf", "--count", "2"])
 */
export function cli(args: string[], stdinPayload?: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const proc = spawn("python3", ["-m", "bakery", ...args], {
      cwd: REPO_ROOT,
      env: { ...process.env, PYTHONPATH: REPO_ROOT },
    });
    let out = "";
    let err = "";
    proc.stdout.on("data", (b) => (out += b.toString()));
    proc.stderr.on("data", (b) => (err += b.toString()));
    proc.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`bakery CLI exited ${code}: ${err || out}`));
        return;
      }
      try {
        resolve(JSON.parse(out));
      } catch (e) {
        reject(new Error(`Non-JSON CLI output: ${out.slice(0, 200)}`));
      }
    });
    proc.on("error", reject);
    if (stdinPayload !== undefined) {
      proc.stdin.write(JSON.stringify(stdinPayload));
    }
    proc.stdin.end();
  });
}
