import {requireOwner} from "../lib/auth";
export default function handler(req:any,res:any){
  if(!requireOwner(req,res))return;
  res.status(200).json({
    equityUsd:150,
    cashUsd:150,
    investedUsd:0,
    positions:[],
    grossExposurePct:0,
    drawdownPct:0,
    updatedAt:new Date().toISOString()
  });
}
