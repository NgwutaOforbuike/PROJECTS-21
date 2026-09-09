export default function handler(req:any,res:any){
  res.status(200).json({
    ok:true,
    service:"global-wealth-trading-os-live",
    mode:"interactive-private-use",
    timestamp:new Date().toISOString()
  });
}
