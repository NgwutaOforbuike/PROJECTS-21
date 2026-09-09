import { clearSessionCookie } from "../_auth";

export default function handler(req: any, res: any) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });
  clearSessionCookie(res);
  return res.status(200).json({ ok: true });
}
