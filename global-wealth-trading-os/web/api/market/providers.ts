import {providerStatuses} from "../../lib/market/router";

export default function handler(req:any,res:any){
  res.status(200).json({
    generatedAt:new Date().toISOString(),
    providers:providerStatuses()
  });
}
