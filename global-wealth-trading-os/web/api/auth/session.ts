import {authConfigured,readSession} from "../../lib/auth";
export default function handler(req:any,res:any){
  res.setHeader("Cache-Control","no-store");
  const session=readSession(req);
  return res.status(200).json({authenticated:Boolean(session),configured:authConfigured(),user:session?{email:session.email}:null});
}
