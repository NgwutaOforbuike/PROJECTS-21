import {createHmac, timingSafeEqual, scryptSync} from "node:crypto";

const COOKIE_NAME="gwos_session";
const SESSION_SECONDS=60*60*12;

function secret(){
  return process.env.AUTH_SECRET||"";
}

function b64url(value:string){
  return Buffer.from(value).toString("base64url");
}

function sign(value:string){
  return createHmac("sha256",secret()).update(value).digest("base64url");
}

export function authConfigured(){
  return Boolean(secret()&&process.env.OWNER_EMAIL&&(process.env.OWNER_PASSWORD_HASH||process.env.OWNER_PASSWORD));
}

export function verifyCredentials(email:string,password:string){
  const expectedEmail=(process.env.OWNER_EMAIL||"").trim().toLowerCase();
  if(!expectedEmail||email.trim().toLowerCase()!==expectedEmail)return false;
  const encoded=process.env.OWNER_PASSWORD_HASH||"";
  if(encoded){
    const [salt,hash]=encoded.split(":");
    if(!salt||!hash)return false;
    const actual=scryptSync(password,salt,32);
    const expected=Buffer.from(hash,"hex");
    return expected.length===actual.length&&timingSafeEqual(actual,expected);
  }
  const plain=Buffer.from(process.env.OWNER_PASSWORD||"");
  const supplied=Buffer.from(password);
  return plain.length===supplied.length&&plain.length>0&&timingSafeEqual(plain,supplied);
}

export function createSession(email:string){
  if(!secret())throw new Error("AUTH_SECRET is not configured");
  const payload=b64url(JSON.stringify({sub:email.toLowerCase(),exp:Math.floor(Date.now()/1000)+SESSION_SECONDS}));
  return `${payload}.${sign(payload)}`;
}

function parseCookies(req:any){
  return Object.fromEntries(String(req.headers?.cookie||"").split(";").map((v:string)=>v.trim()).filter(Boolean).map((v:string)=>{
    const i=v.indexOf("=");return i<0?[v,""]:[v.slice(0,i),decodeURIComponent(v.slice(i+1))];
  }));
}

export function readSession(req:any):{email:string}|null{
  const token=parseCookies(req)[COOKIE_NAME];
  if(!token||!secret())return null;
  const [payload,signature]=token.split(".");
  if(!payload||!signature)return null;
  const actual=Buffer.from(signature);const expected=Buffer.from(sign(payload));
  if(actual.length!==expected.length||!timingSafeEqual(actual,expected))return null;
  try{
    const data=JSON.parse(Buffer.from(payload,"base64url").toString("utf8"));
    if(!data.sub||Number(data.exp)<=Math.floor(Date.now()/1000))return null;
    if(String(data.sub).toLowerCase()!==(process.env.OWNER_EMAIL||"").trim().toLowerCase())return null;
    return {email:String(data.sub)};
  }catch{return null;}
}

export function requireOwner(req:any,res:any){
  const session=readSession(req);
  if(!authConfigured()){
    res.status(503).json({error:"Owner authentication is not configured",code:"AUTH_NOT_CONFIGURED"});
    return null;
  }
  if(!session){res.status(401).json({error:"Authentication required",code:"UNAUTHORIZED"});return null;}
  return session;
}

export function setSessionCookie(res:any,token:string){
  res.setHeader("Set-Cookie",`${COOKIE_NAME}=${encodeURIComponent(token)}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${SESSION_SECONDS}`);
}

export function clearSessionCookie(res:any){
  res.setHeader("Set-Cookie",`${COOKIE_NAME}=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0`);
}
