import {requireOwner} from "../lib/auth";

export default function handler(req:any,res:any){
  if(!requireOwner(req,res))return;
  const mode=String(req.query?.mode||"integrations");
  res.setHeader("Cache-Control","no-store");
  if(mode==="integrations")return res.status(200).json({
    generatedAt:new Date().toISOString(),
    services:[
      {name:"Binance public data",category:"Market data",configured:true,cost:"Free public endpoints",status:"AVAILABLE"},
      {name:"Alpaca",category:"Market data / paper broker",configured:Boolean(process.env.ALPACA_API_KEY||process.env.APCA_API_KEY_ID),cost:"Provider plan dependent",status:process.env.ALPACA_API_KEY||process.env.APCA_API_KEY_ID?"CONFIGURED":"NEEDS_KEY"},
      {name:"Twelve Data",category:"Multi-asset data",configured:Boolean(process.env.TWELVE_DATA_API_KEY),cost:"Free tier available",status:process.env.TWELVE_DATA_API_KEY?"CONFIGURED":"NEEDS_KEY"},
      {name:"FRED",category:"Macroeconomic data",configured:Boolean(process.env.FRED_API_KEY),cost:"Free",status:process.env.FRED_API_KEY?"CONFIGURED":"NEEDS_KEY"},
      {name:"Python intelligence service",category:"Models and training",configured:Boolean(process.env.PYTHON_AI_URL),cost:"Hosting not connected",status:process.env.PYTHON_AI_URL?"CONFIGURED":"NOT_DEPLOYED"},
      {name:"Google Drive",category:"Research archive",configured:Boolean(process.env.GOOGLE_DRIVE_FOLDER_ID),cost:"Free within account quota",status:process.env.GOOGLE_DRIVE_FOLDER_ID?"CONFIGURED":"NOT_CONNECTED"},
      {name:"Google Cloud",category:"Long-running compute",configured:Boolean(process.env.GOOGLE_CLOUD_PROJECT),cost:"Not required yet",status:process.env.GOOGLE_CLOUD_PROJECT?"CONFIGURED":"DEFERRED"}
    ]
  });
  if(mode==="models")return res.status(200).json({
    policy:"CHAMPION_CHALLENGER",livePromotion:false,
    lifecycle:["DRAFT","BACKTESTED","PAPER","APPROVED","RETIRED"],
    controls:["chronological splits","leakage gate","held-out test set","drift detection","owner approval"],
    status:"PYTHON_SERVICE_NOT_CONNECTED"
  });
  if(mode==="research")return res.status(200).json({
    sources:["SEC EDGAR","FRED","BEA","BLS","Companies House","official regulator sources"],
    rules:["primary sources preferred","publication timestamp retained","licence recorded","conflicting evidence quarantined"],
    driveStatus:process.env.GOOGLE_DRIVE_FOLDER_ID?"CONNECTED":"NOT_CONNECTED"
  });
  return res.status(400).json({error:"Unknown mode"});
}
