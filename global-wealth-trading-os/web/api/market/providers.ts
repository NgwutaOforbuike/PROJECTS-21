import {providerStatuses} from "../../lib/market/router";
import {requireOwner} from "../../lib/auth";

export default function handler(req:any,res:any){
  if(!requireOwner(req,res))return;
  res.status(200).json({
    generatedAt:new Date().toISOString(),
    providers:providerStatuses()
  });
}
