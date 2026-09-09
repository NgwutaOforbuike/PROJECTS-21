import React,{useEffect,useMemo,useState} from "react";
import {createRoot} from "react-dom/client";
import {AlertTriangle,ArrowRight,Globe2,LockKeyhole,RefreshCw,ShieldCheck,Target,WalletCards} from "lucide-react";
import "./styles.css";
import {buildInfo} from "./buildInfo";

type Tab="decision"|"opportunities"|"portfolio"|"risk";
type Json=Record<string,any>;

function useApi(path:string){
  const [data,setData]=useState<Json|null>(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState<string|null>(null);
  const load=async()=>{
    setLoading(true); setError(null);
    try{
      const r=await fetch(path,{cache:"no-store"});
      if(!r.ok) throw new Error(`${r.status} ${r.statusText}`);
      setData(await r.json());
    }catch(e:any){setError(e?.message||String(e));}
    finally{setLoading(false);}
  };
  useEffect(()=>{load();},[path]);
  return {data,loading,error,load};
}

function App(){
  const [tab,setTab]=useState<Tab>("decision");
  const mandate=useApi("/api/mandate");
  const decision=useApi("/api/decision");
  const opportunities=useApi("/api/opportunities");
  const portfolio=useApi("/api/portfolio");
  const risk=useApi("/api/risk");

  const current=useMemo(()=>({
    decision,opportunities,portfolio,risk
  }[tab]),[tab,decision,opportunities,portfolio,risk]);

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
        <span>Equity <b>${mandate.data?.startingEquityUsd?.toFixed?.(2) ?? "150.00"}</b></span>
        <span>Cash <b>${mandate.data?.cashUsd?.toFixed?.(2) ?? "150.00"}</b></span>
        <span>Max risk / trade <b>{mandate.data?.maxRiskPerTradePct ?? 0.5}%</b></span>
        <span>Return hurdle <b>{mandate.data?.minModelledReturnPct ?? 5}%+</b></span>
        <span>Markets <b>NG · US · UK</b></span>
      </section>

      {current.error && <section className="panel"><div className="danger"><AlertTriangle/>Unable to reach live app service: {current.error}</div></section>}
      {current.loading && <section className="panel"><p className="thesis">Refreshing live application data…</p></section>}

      {!current.loading && tab==="decision" && <DecisionView data={decision.data}/>}
      {!current.loading && tab==="opportunities" && <OpportunitiesView data={opportunities.data}/>}
      {!current.loading && tab==="portfolio" && <PortfolioView data={portfolio.data}/>}
      {!current.loading && tab==="risk" && <RiskView data={risk.data}/>}
    </main>
  </div>
}

function DecisionView({data}:{data:Json|null}){
  return <>
    <section className="heroGrid">
      <div className="panel portfolioHero">
        <div className="panelHead"><div><span>TODAY'S BEST ACTION</span><h2>{data?.action??"NO TRADE"}</h2></div><span className="status">{data?.status??"CHECKING"}</span></div>
        <p className="thesis">{data?.reason??"The system is checking available evidence and risk constraints."}</p>
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
        <div className="danger"><AlertTriangle/> A valid result can be NO TRADE.</div>
      </div>
    </section>
  </>
}

function OpportunitiesView({data}:{data:Json|null}){
  const rows=data?.opportunities??[];
  return <>
    <section className="sectionTitle"><div><p className="eyebrow">BEST AVAILABLE OPPORTUNITIES</p><h2>Daily market shortlist</h2></div></section>
    <section className="panel tablePanel"><div className="table">
      <div className="tr th"><span>Market</span><span>Status</span><span>Decision</span><span>Expected Return</span><span>Confidence</span><span>Risk</span><span></span></div>
      {rows.map((m:any)=><div className="tr" key={m.market}>
        <span className="asset"><b>{m.market}</b><small>Mandate-approved market</small></span>
        <span>{m.status}</span><span className="pill watch">{m.decision}</span>
        <span>{m.expectedReturn==null?"—":`${m.expectedReturn}%`}</span>
        <span>{m.confidence==null?"—":`${m.confidence}%`}</span>
        <span>0.5% max</span><span><ArrowRight style={{width:14}}/></span>
      </div>)}
    </div></section>
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
    <div className="panel stress">
      <div className="panelHead"><div><span>KILL SWITCH</span><h3>{data?.killSwitch?"ARMED":"OFF"}</h3></div></div>
      <p className="thesis">Critical data, reconciliation, drawdown or specialist veto conditions can block new trades.</p>
    </div>
  </section>
}

createRoot(document.getElementById("root")!).render(<App/>);
