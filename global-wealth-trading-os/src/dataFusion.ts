export interface MarketObservation {
  sourceId:string;
  instrumentId:string;
  field:string;
  value:number;
  observedAt:string;
  receivedAt:string;
  tier:1|2|3|4;
  delayed:boolean;
}

export interface ConsensusResult {
  instrumentId:string;
  field:string;
  value:number|null;
  confidence:number;
  sourceCount:number;
  acceptedSources:string[];
  rejectedSources:string[];
  stale:boolean;
  dispersionPct:number|null;
}

const ageMs=(iso:string)=>Date.now()-new Date(iso).getTime();

export function buildConsensus(
  rows:MarketObservation[],
  opts:{maxAgeMs:number;maxDispersionPct:number;minimumIndependentSources:number}
):ConsensusResult {
  if(!rows.length) return {instrumentId:"",field:"",value:null,confidence:0,sourceCount:0,acceptedSources:[],rejectedSources:[],stale:true,dispersionPct:null};

  const fresh=rows.filter(r=>ageMs(r.observedAt)<=opts.maxAgeMs && !r.delayed);
  const rejected=rows.filter(r=>!fresh.includes(r)).map(r=>r.sourceId);
  if(!fresh.length) return {instrumentId:rows[0].instrumentId,field:rows[0].field,value:null,confidence:0,sourceCount:0,acceptedSources:[],rejectedSources:rejected,stale:true,dispersionPct:null};

  const weighted=fresh.map(r=>({r,w:r.tier===1?4:r.tier===2?3:r.tier===3?2:1}));
  const sorted=[...fresh].sort((a,b)=>a.value-b.value);
  const median=sorted[Math.floor(sorted.length/2)].value;
  const deviations=fresh.map(r=>Math.abs(r.value-median)/Math.max(Math.abs(median),1e-12)*100);
  const maxDisp=Math.max(...deviations);
  const accepted=weighted.filter(x=>Math.abs(x.r.value-median)/Math.max(Math.abs(median),1e-12)*100<=opts.maxDispersionPct);
  const totalW=accepted.reduce((s,x)=>s+x.w,0);
  const value=totalW?accepted.reduce((s,x)=>s+x.r.value*x.w,0)/totalW:null;
  const sourceCount=accepted.length;
  const independence=Math.min(1,sourceCount/Math.max(1,opts.minimumIndependentSources));
  const tierQuality=accepted.length?accepted.reduce((s,x)=>s+x.w,0)/(accepted.length*4):0;
  const agreement=Math.max(0,1-Math.min(1,maxDisp/Math.max(opts.maxDispersionPct,0.0001)));
  const confidence=Math.round((independence*.4+tierQuality*.35+agreement*.25)*100);

  return {
    instrumentId:rows[0].instrumentId,
    field:rows[0].field,
    value,
    confidence,
    sourceCount,
    acceptedSources:accepted.map(x=>x.r.sourceId),
    rejectedSources:[...rejected,...weighted.filter(x=>!accepted.includes(x)).map(x=>x.r.sourceId)],
    stale:false,
    dispersionPct:Number(maxDisp.toFixed(6))
  };
}
