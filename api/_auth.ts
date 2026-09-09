import { createHmac, timingSafeEqual, scryptSync } from "node:crypto";

const COOKIE_NAME = "gwos_session";
const SESSION_SECONDS = 60 * 60 * 12;

function authSecret() {
  return (process.env.AUTH_SECRET || "").trim();
}

function ownerEmail() {
  return (process.env.OWNER_EMAIL || "").trim().toLowerCase();
}

function ownerPassword() {
  return process.env.OWNER_PASSWORD || "";
}

function ownerPasswordHash() {
  return process.env.OWNER_PASSWORD_HASH || "";
}

export function authStatus() {
  return {
    configured: Boolean(authSecret() && ownerEmail() && (ownerPasswordHash() || ownerPassword())),
    hasAuthSecret: Boolean(authSecret()),
    hasOwnerEmail: Boolean(ownerEmail()),
    hasOwnerPassword: Boolean(ownerPasswordHash() || ownerPassword()),
  };
}

export function verifyCredentials(email: string, password: string) {
  const expectedEmail = ownerEmail();
  if (!expectedEmail || email.trim().toLowerCase() !== expectedEmail) return false;

  const encoded = ownerPasswordHash();
  if (encoded) {
    const [salt, hash] = encoded.split(":");
    if (!salt || !hash) return false;
    const actual = scryptSync(password, salt, 32);
    const expected = Buffer.from(hash, "hex");
    return expected.length === actual.length && timingSafeEqual(actual, expected);
  }

  const expected = Buffer.from(ownerPassword());
  const supplied = Buffer.from(password);
  return expected.length > 0 && expected.length === supplied.length && timingSafeEqual(expected, supplied);
}

function sign(value: string) {
  return createHmac("sha256", authSecret()).update(value).digest("base64url");
}

export function createSession(email: string) {
  if (!authSecret()) throw new Error("AUTH_SECRET is not configured");
  const payload = Buffer.from(JSON.stringify({
    sub: email.trim().toLowerCase(),
    exp: Math.floor(Date.now() / 1000) + SESSION_SECONDS,
  })).toString("base64url");
  return `${payload}.${sign(payload)}`;
}

function parseCookies(req: any) {
  const entries = String(req.headers?.cookie || "")
    .split(";")
    .map((v: string) => v.trim())
    .filter(Boolean)
    .map((v: string) => {
      const i = v.indexOf("=");
      return i < 0 ? [v, ""] : [v.slice(0, i), decodeURIComponent(v.slice(i + 1))];
    });
  return Object.fromEntries(entries);
}

export function readSession(req: any): { email: string } | null {
  const token = parseCookies(req)[COOKIE_NAME];
  if (!token || !authSecret()) return null;
  const [payload, signature] = token.split(".");
  if (!payload || !signature) return null;

  const actual = Buffer.from(signature);
  const expected = Buffer.from(sign(payload));
  if (actual.length !== expected.length || !timingSafeEqual(actual, expected)) return null;

  try {
    const data = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    if (!data.sub || Number(data.exp) <= Math.floor(Date.now() / 1000)) return null;
    if (String(data.sub).toLowerCase() !== ownerEmail()) return null;
    return { email: String(data.sub) };
  } catch {
    return null;
  }
}

export function setSessionCookie(res: any, token: string) {
  res.setHeader("Set-Cookie", `${COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${SESSION_SECONDS}`);
}

export function clearSessionCookie(res: any) {
  res.setHeader("Set-Cookie", `${COOKIE_NAME}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0`);
}
