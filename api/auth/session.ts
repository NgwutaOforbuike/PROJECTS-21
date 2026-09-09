import { authStatus, readSession } from "../_auth";

export default function handler(req: any, res: any) {
  res.setHeader("Cache-Control", "no-store");
  const status = authStatus();
  const session = readSession(req);
  return res.status(200).json({
    authenticated: Boolean(session),
    configured: status.configured,
    user: session ? { email: session.email } : null,
    auth: status,
  });
}
