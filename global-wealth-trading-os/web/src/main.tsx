import React,{useEffect,useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import {AlertTriangle,Globe2,LockKeyhole,RefreshCw,Search,ShieldCheck,Target,WalletCards} from "lucide-react";
import "./styles.css";
import {buildInfo} from "./buildInfo";

type Tab="decision"|"opportunities"|"portfolio"|"risk";
type Json=Record<string,any>;
type Quote={
  symbol:string;assetClass:string;region:string;price:number|null;bid:number|null;ask:number|null;
  changePct:number|null;volume:number|null;currency:string|null;source:string;delayed:boolean;stale:boolean;
  confidence:number;available:boolean;error?:string;observedAt?:string|null;
};

const ASSET_CLASSES=["ALL","EQUITY","ETF","FX","CRYPTO","COMMODITY","FUTURE","OPTION","BOND","FUND"] as const;

function useApi(path:string,autoMs?:number){
  const [data,setData]=useState<Json|null>(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState<string|null>(null);
  const load=async()=>{
    setLoading(true);setError(null);
    try{
      const r=await fetch(path,{cache:"no-store"});
      if(!r.ok) throw new Error(`${r.status} ${r.statusText}`);
      setData(await r.json());
    }catch(e:any){setError(e?.message||String(e));}
    finally{setLoading(false);}
  };
  useEffect(()=>{
    load();
    if(!autoMs) return;
    const id=setInterval(load,autoMs);
    return()=>clearInterval(id);
  },[path,autoMs]);
  return {data,loading,error,load};
}

function formatPrice(v:number|null,currency?:string|null){
  if(v==null)return "—";
  const max=v<1?6:v<100?4:2;
  return `${currency==="USD"?"$":""}${v.toLocaleString(undefined,{maximumFractionDigits:max})}`;
}

function App(){
  const [tab,setTab]=useState<Tab>("opportunities");
  const mandate=useApi("/api/mandate");
  const decision=useApi("/api/decision",15000);
  const market=useApi("/api/market/quotes",10000);
  const providers=useApi("/api/market/providers",30000);
  const portfolio=useApi("/api/portfolio",15000);
  const risk=useApi("/api/risk",15000);

  const current=useMemo(()=>({decision,opportunities:market,portfolio,risk}[tab]),[tab,decision,market,portfolio,risk]);
  const nav=[
    ["decision","Today's Decision",Target],
    ["opportunities","Opportunities",Globe2],
    ["portfolio","Portfolio",WalletCards],
    ["risk","Risk & Exposure",ShieldCheck],
  ] as const;

  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><div className="mark">GW</div><div><strong>Global Wealth</strong><span>Investment OS</span></div></div>
      <nav>{nav.map(([id,label,Icon])=><button key={id} onClick={()=>setTab(id)} className={tab===id?"active":""}><Icon/>{label}</button>)}</nav>
      <div className="guard"><LockKeyhole/><div><b>Live execution locked</b><span>Interactive analysis · owner approval required</span><span>{buildInfo.source}</span></div></div>
    </aside>

    <main>
      <header>
        <div><p className="eyebrow">PERSONAL INVESTMENT COMMAND CENTRE</p><h1>{
          tab==="decision"?"What should I do with my capital today?":
          tab==="opportunities"?"Where are the best opportunities?":
          tab==="portfolio"?"What do I own and how is capital allocated?":
          "How much risk am I carrying?"
        }</h1></div>
        <button className="status" onClick={current.load}><RefreshCw style={{width:14}}/> REFRESH</button>
      </header>

      <section className="marketStrip">
        <span>Equity <b>${mandate.data?.startingEquityUsd?.toFixed?.(2)??"150.00"}</b></span>
        <span>Cash <b>${mandate.data?.cashUsd?.toFixed?.(2)??"150.00"}</b></span>
        <span>Max risk / trade <b>{mandate.data?.maxRiskPerTradePct??0.5}%</b></span>
        <span>Return hurdle <b>{mandate.data?.minModelledReturnPct??5}%+</b></span>
        <span>Markets <b>NG · US · UK</b></span>
      </section>

      {current.error&&<section className="panel"><div className="danger"><AlertTriangle/>Live application service error: {current.error}</div></section>}
      {current.loading&&<section className="panel"><p className="thesis">Refreshing live application data…</p></section>}

      {!current.loading&&tab==="decision"&&<DecisionView data={decision.data}/>}
      {!current.loading&&tab==="opportunities"&&<MarketView data={market.data} providers={providers.data} reload={market.load}/>}
      {!current.loading&&tab==="portfolio"&&<PortfolioView data={portfolio.data}/>}
      {!current.loading&&tab==="risk"&&<RiskView data={risk.data}/>}
    </main>
  </div>
}

function DecisionView({data}:{data:Json|null}){
  return <section className="heroGrid">
    <div className="panel portfolioHero">
      <div className="panelHead"><div><span>TODAY'S BEST ACTION</span><h2>{data?.action??"NO TRADE"}</h2></div><span className="status">{data?.status??"CHECKING"}</span></div>
      <p className="thesis">{data?.reason??"The autonomous investment engine is evaluating market evidence."}</p>
      <div className="heroMetrics">
        <div><span>Entry zone</span><b>{data?.entry??"—"}</b></div>
        <div><span>Stop / invalidation</span><b>{data?.stop??"—"}</b></div>
        <div><span>Profit target</span><b>{data?.target??"—"}</b></div>
        <div><span>Position size</span><b>{data?.quantity??"—"}</b></div>
      </div>
    </div>
    <div className="panel riskCard">
      <div className="panelHead"><div><span>DECISION QUALITY</span><h3>Trade gate</h3></div><ShieldCheck className="shield"/></div>
      <div className="riskRows">
        <p><span>Confidence</span><b>{data?.confidence??"—"}</b></p>
        <p><span>Max planned loss</span><b>${data?.maxPlannedLossUsd??0.75}</b></p>
        <p><span>Minimum return hurdle</span><b>{data?.minModelledReturnPct??5}%+</b></p>
        <p><span>Generated</span><b>{data?.generatedAt?new Date(data.generatedAt).toLocaleTimeString():"—"}</b></p>
      </div>
      <div className="danger"><AlertTriangle/> A valid investment decision can be NO TRADE.</div>
    </div>
  </section>
}

function MarketView({data,providers,reload}:{data:Json|null;providers:Json|null;reload:()=>void}){
  const [filter,setFilter]=useState("ALL");
  const [selected,setSelected]=useState<Quote|null>(null);
  const [lookup,setLookup]=useState({symbol:"",assetClass:"EQUITY",region:"US"});
  const [lookupResult,setLookupResult]=useState<Quote|null>(null);
  const [lookupError,setLookupError]=useState("");
  const quotes=(data?.quotes??[]) as Quote[];
  const filtered=filter==="ALL"?quotes:quotes.filter(q=>q.assetClass===filter);
  const configured=(providers?.providers??[]).filter((p:any)=>p.configured).length;
  const liveCount=quotes.filter(q=>q.available&&!q.stale).length;

  async function doLookup(){
    setLookupError("");setLookupResult(null);
    if(!lookup.symbol.trim())return;
    const u=new URL("/api/market/quote",window.location.origin);
    u.searchParams.set("symbol",lookup.symbol.trim());
    u.searchParams.set("assetClass",lookup.assetClass);
    u.searchParams.set("region",lookup.region);
    try{
      const r=await fetch(u,{cache:"no-store"});
      const d=await r.json();
      if(!r.ok) throw new Error(d.error||String(r.status));
      setLookupResult(d);
    }catch(e:any){setLookupError(e?.message||String(e));}
  }

  return <>
    <section className="sectionTitle"><div><p className="eyebrow">LIVE MULTI-ASSET MARKET DATA</p><h2>Market shortlist</h2></div></section>

    <section className="panel">
      <div className="marketStrip">
        <span>Live quotes <b>{liveCount}</b></span>
        <span>Configured providers <b>{configured}</b></span>
        <span>Auto refresh <b>10 sec</b></span>
        <span>Last refresh <b>{data?.generatedAt?new Date(data.generatedAt).toLocaleTimeString():"—"}</b></span>
      </div>
      <div className="filters">
        {ASSET_CLASSES.map(a=><button key={a} className={filter===a?"selected":""} onClick={()=>setFilter(a)}>{a}</button>)}
      </div>
    </section>

    <section className="panel tablePanel">
      <div className="table">
        <div className="tr th"><span>Asset</span><span>Price</span><span>Change</span><span>Source</span><span>Freshness</span><span>Confidence</span><span>Status</span></div>
        {filtered.map(q=><button className="tr marketRow" key={q.assetClass+q.symbol} onClick={()=>setSelected(q)}>
          <span className="asset"><b>{q.symbol}</b><small>{q.assetClass} · {q.region}</small></span>
          <span>{formatPrice(q.price,q.currency)}</span>
          <span className={(q.changePct??0)>0?"good":(q.changePct??0)<0?"bad":""}>{q.changePct==null?"—":`${q.changePct.toFixed(2)}%`}</span>
          <span>{q.source}</span>
          <span>{q.stale?"STALE":q.delayed?"DELAYED":"LIVE"}</span>
          <span>{q.confidence}%</span>
          <span className={q.available?"pill buy":"pill watch"}>{q.available?"AVAILABLE":"UNAVAILABLE"}</span>
        </button>)}
      </div>
    </section>

    <section className="lowerGrid">
      <div className="panel">
        <div className="panelHead"><div><span>QUOTE INSPECTOR</span><h3>{selected?.symbol??"Click any asset"}</h3></div></div>
        {selected?<div className="riskRows">
          <p><span>Last</span><b>{formatPrice(selected.price,selected.currency)}</b></p>
          <p><span>Bid</span><b>{formatPrice(selected.bid,selected.currency)}</b></p>
          <p><span>Ask</span><b>{formatPrice(selected.ask,selected.currency)}</b></p>
          <p><span>Source</span><b>{selected.source}</b></p>
          <p><span>Observed</span><b>{selected.observedAt?new Date(selected.observedAt).toLocaleString():"—"}</b></p>
          <p><span>Provider note</span><b>{selected.error??"Quote available"}</b></p>
        </div>:<p className="thesis">Select an asset to inspect its live quote provenance and market quality.</p>}
      </div>

      <div className="panel">
        <div className="panelHead"><div><span>CUSTOM LOOKUP</span><h3>Check another instrument</h3></div><Search/></div>
        <div className="lookupForm">
          <input value={lookup.symbol} onChange={e=>setLookup({...lookup,symbol:e.target.value})} placeholder="e.g. AAPL, BTC/USDT, GBP/USD"/>
          <select value={lookup.assetClass} onChange={e=>setLookup({...lookup,assetClass:e.target.value})}>
            {ASSET_CLASSES.filter(x=>x!=="ALL").map(x=><option key={x}>{x}</option>)}
          </select>
          <select value={lookup.region} onChange={e=>setLookup({...lookup,region:e.target.value})}>
            <option value="US">US</option><option value="UK">UK</option><option value="NG">NG</option><option value="GLOBAL">GLOBAL</option>
          </select>
          <button onClick={doLookup}>GET LIVE QUOTE</button>
        </div>
        {lookupError&&<div className="danger">{lookupError}</div>}
        {lookupResult&&<div className="riskRows">
          <p><span>Price</span><b>{formatPrice(lookupResult.price,lookupResult.currency)}</b></p>
          <p><span>Source</span><b>{lookupResult.source}</b></p>
          <p><span>Status</span><b>{lookupResult.available?"AVAILABLE":"UNAVAILABLE"}</b></p>
          <p><span>Message</span><b>{lookupResult.error??"Live quote returned"}</b></p>
        </div>}
      </div>
    </section>
  </>
}

function PortfolioView({data}:{data:Json|null}){
  const positions=data?.positions??[];
  return <section className="heroGrid">
    <div className="panel portfolioHero">
      <div className="panelHead"><div><span>PORTFOLIO</span><h2>${data?.equityUsd?.toFixed?.(2)??"150.00"}</h2></div><span className="status">{data?.grossExposurePct??0}% EXPOSED</span></div>
      <div className="heroMetrics">
        <div><span>Cash</span><b>${data?.cashUsd?.toFixed?.(2)??"150.00"}</b></div>
        <div><span>Invested</span><b>${data?.investedUsd?.toFixed?.(2)??"0.00"}</b></div>
        <div><span>Positions</span><b>{positions.length}</b></div>
        <div><span>Drawdown</span><b>{data?.drawdownPct??0}%</b></div>
      </div>
      <p className="thesis">{positions.length?"Open positions are shown here.":"No open positions. Cash remains a valid position."}</p>
    </div>
    <div className="panel stress"><div className="panelHead"><div><span>POSITIONS</span><h3>{positions.length?"Open holdings":"None"}</h3></div></div></div>
  </section>
}

function RiskView({data}:{data:Json|null}){
  return <section className="heroGrid">
    <div className="panel riskCard">
      <div className="panelHead"><div><span>RISK GOVERNOR</span><h2>Capital protection</h2></div><ShieldCheck className="shield"/></div>
      <div className="riskRows">
        <p><span>Max risk / trade</span><b>{data?.maxRiskPerTradePct??0.5}%</b></p>
        <p><span>Max planned loss</span><b>${data?.maxPlannedLossUsd??0.75}</b></p>
        <p><span>Max drawdown</span><b>{data?.maxDrawdownPct??12}%</b></p>
        <p><span>Data confidence required</span><b>{data?.dataConfidenceRequired??70}%</b></p>
        <p><span>Leverage</span><b>{data?.leverage?"ON":"OFF"}</b></p>
        <p><span>Live execution</span><b>{data?.liveExecution?"ON":"LOCKED"}</b></p>
      </div>
    </div>
    <div className="panel stress"><div className="panelHead"><div><span>KILL SWITCH</span><h3>{data?.killSwitch?"ARMED":"OFF"}</h3></div></div><p className="thesis">Critical data, reconciliation, drawdown or specialist veto conditions can block new trades.</p></div>
  </section>
}

createRoot(document.getElementById("root")!).render(<App/>);
