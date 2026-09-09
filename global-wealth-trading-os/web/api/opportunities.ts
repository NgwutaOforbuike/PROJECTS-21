export default function handler(req:any,res:any){
  res.status(200).json({
    generatedAt:new Date().toISOString(),
    opportunities:[
      {market:"Nigeria",status:"LIVE_FEED_NOT_YET_ENTITLED",decision:"SCAN",expectedReturn:null,confidence:null},
      {market:"United States",status:"LIVE_FEED_NOT_YET_ENTITLED",decision:"SCAN",expectedReturn:null,confidence:null},
      {market:"United Kingdom",status:"LIVE_FEED_NOT_YET_ENTITLED",decision:"SCAN",expectedReturn:null,confidence:null}
    ]
  });
}
