import {clearSessionCookie} from "../../lib/auth";
export default function handler(req:any,res:any){
  if(req.method!=="POST")return res.status(405).json({error:"Method not allowed"});
  clearSessionCookie(res);return res.status(200).json({ok:true});
}
