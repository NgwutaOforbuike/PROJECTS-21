import {authConfigured,createSession,setSessionCookie,verifyCredentials} from "../../lib/auth";

export default function handler(req:any,res:any){
  res.setHeader("Cache-Control","no-store");
  if(req.method!=="POST")return res.status(405).json({error:"Method not allowed"});
  if(!authConfigured())return res.status(503).json({error:"Owner sign-in has not been configured yet",code:"AUTH_NOT_CONFIGURED"});
  let body:any={};
  try{body=typeof req.body==="string"?JSON.parse(req.body||"{}"):req.body||{};}
  catch{return res.status(400).json({error:"Invalid JSON body"});}
  if(!verifyCredentials(String(body.email||""),String(body.password||"")))return res.status(401).json({error:"Invalid email or password"});
  setSessionCookie(res,createSession(String(body.email)));
  return res.status(200).json({ok:true});
}
