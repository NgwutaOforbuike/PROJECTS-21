import { authStatus, createSession, setSessionCookie, verifyCredentials } from "../_auth";

export default function handler(req: any, res: any) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const status = authStatus();
  if (!status.configured) {
    return res.status(503).json({
      error: "Owner sign-in is not configured for this deployment",
      code: "AUTH_NOT_CONFIGURED",
      auth: status,
    });
  }

  let body: any = {};
  try {
    body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
  } catch {
    return res.status(400).json({ error: "Invalid JSON body" });
  }

  const email = String(body.email || "");
  const password = String(body.password || "");
  if (!verifyCredentials(email, password)) {
    return res.status(401).json({ error: "Invalid email or password" });
  }

  setSessionCookie(res, createSession(email));
  return res.status(200).json({ ok: true });
}
