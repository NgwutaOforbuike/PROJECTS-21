import React from "react";
import {createRoot} from "react-dom/client";
import {Activity,BarChart3,Bell,BrainCircuit,ChevronRight,Globe2,Landmark,LineChart,LockKeyhole,Search,ShieldCheck,SlidersHorizontal,Sparkles,WalletCards} from "lucide-react";
import "./styles.css";
import {buildInfo} from "./buildInfo";

const money=(n:number)=>new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(n);
const pct=(n:number)=>`${n>0?"+":""}${n.toFixed(2)}%`;

const opportunities=[
{asset:"NVDA",name:"NVIDIA",cls:"Equity",region:"US",score:92,ret:2.61,risk:"Medium",decision:"STRONG BUY",committee:"5–1",why:"Earnings momentum + liquidity + positive trend regime"},
{asset:"BTC",name:"Bitcoin",cls:"Crypto",region:"Global",score:86,ret:1.48,risk:"High",decision:"BUY",committee:"4–2",why:"Trend persistence; risk governor limits sizing"},
{asset:"GLD",name:"Gold ETF",cls:"ETF",region:"US",score:79,ret:.52,risk:"Low",decision:"BUY",committee:"5–1",why:"Diversifier under current macro stress basket"},
{asset:"NESN",name:"Nestlé SA",cls:"Equity",region:"Europe",score:71,ret:-.16,risk:"Low",decision:"WATCH",committee:"3–3",why:"Quality high; momentum not yet confirmed"},
{asset:"NGXBANK",name:"NGX Banking",cls:"Equity",region:"Nigeria",score:68,ret:.83,risk:"Medium",decision:"WATCH",committee:"4–2",why:"Valuation attractive; FX risk raises hurdle"}
];

const votes=[
{name:"Macro",vote:"BUY",confidence:81,detail:"Liquidity and growth regime supportive"},
{name:"Fundamental",vote:"BUY",confidence:88,detail:"Earnings revisions remain positive"},
{name:"Technical",vote:"STRONG BUY",confidence:92,detail:"Trend + breadth confirmation"},
{name:"Sentiment",vote:"WATCH",confidence:61,detail:"Positioning becoming crowded"},
{name:"Quant",vote:"BUY",confidence:84,detail:"Cross-sectional score in top decile"},
{name:"Risk Governor",vote:"ALLOW",confidence:96,detail:"Within exposure, drawdown and VaR limits"}
];

function App(){
 return <div className="app">
  <aside className="sidebar">
   <div className="brand"><div className="mark">GW</div><div><strong>Global Wealth</strong><span>Trading OS</span></div></div>
   <nav>
    <button className="active"><BarChart3/>Command Centre</button>
    <button><Globe2/>Opportunity Map</button>
    <button><BrainCircuit/>AI Committee</button>
    <button><LineChart/>Strategy Lab</button>
    <button><Activity/>Market Depth & Flow</button>
    <button><ShieldCheck/>Risk Cockpit</button>
    <button><WalletCards/>Portfolio</button>
    <button><Landmark/>Execution & Orders</button>
    <button><BarChart3/>Performance Attribution</button>
   </nav>
   <div className="guard"><LockKeyhole/><div><b>Live execution locked</b><span>Paper mode · owner approval required</span><span>{buildInfo.source}</span></div></div>
  </aside>
  <main>
   <header>
    <div><p className="eyebrow">INSTITUTIONAL COMMAND CENTRE</p><h1>Nigeria · USA · UK portfolio intelligence</h1></div>
    <div className="headerActions"><button className="icon"><Search/></button><button className="icon"><Bell/></button><button className="control"><SlidersHorizontal/> Controls</button><div className="avatar">ON</div></div>
   </header>

   <section className="marketStrip">
    <span><i className="up"></i>S&P 500 <b>6,548.31</b> <em>+0.42%</em></span>
    <span><i className="up"></i>NGX ASI <b>141,202</b> <em>+0.71%</em></span>
    <span><i className="down"></i>US 10Y <b>4.08%</b> <em>-3bp</em></span>
    <span><i className="up"></i>BTC <b>$113,820</b> <em>+1.32%</em></span>
    <span><i className="up"></i>Gold <b>$3,641</b> <em>+0.26%</em></span>
   </section>

   <section className="heroGrid">
    <div className="panel portfolioHero">
      <div className="panelHead"><div><span>NET LIQUIDATION VALUE</span><h2>{money(150)}</h2></div><span className="status">PAPER PORTFOLIO · $150 START</span></div>
      <div className="return"><strong>+{money(0)}</strong><span>Starting capital</span></div>
      <div className="equityCurve">
        <svg viewBox="0 0 600 150" preserveAspectRatio="none"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5be7c4" stopOpacity=".32"/><stop offset="100%" stopColor="#5be7c4" stopOpacity="0"/></linearGradient></defs><path d="M0 125 C55 115 70 100 115 106 S180 88 215 91 S270 69 315 74 S365 48 402 53 S460 30 505 37 S555 20 600 17 L600 150 L0 150 Z" fill="url(#g)"/><path d="M0 125 C55 115 70 100 115 106 S180 88 215 91 S270 69 315 74 S365 48 402 53 S460 30 505 37 S555 20 600 17" fill="none" stroke="#5be7c4" strokeWidth="3"/></svg>
      </div>
      <div className="heroMetrics"><div><span>Today</span><b>0.00%</b></div><div><span>YTD</span><b>0.00%</b></div><div><span>Cash</span><b>$150.00</b></div><div><span>Gross exposure</span><b>0.0%</b></div></div>
    </div>
    <div className="panel riskCard">
      <div className="panelHead"><div><span>RISK GOVERNOR</span><h3>NG · US · UK ONLY</h3></div><ShieldCheck className="shield"/></div>
      <div className="riskRing"><div><b>63</b><span>Risk utilisation</span></div></div>
      <div className="riskRows"><p><span>Risk per trade</span><b>0.5% HARD MAX</b></p><p><span>Max drawdown</span><b>0.0% / 12%</b></p><p><span>Largest position</span><b>0.0% / 10%</b></p><p><span>Leverage</span><b>OFF</b></p></div>
      <button className="danger">Emergency kill switch</button>
    </div>
   </section>

   <section className="sectionTitle"><div><p className="eyebrow">CAPITAL ALLOCATION ENGINE</p><h2>Nigeria · USA · UK Opportunity Map</h2></div><button className="link">Open full scanner <ChevronRight/></button></section>
   <section className="panel tablePanel">
    <div className="filters"><span className="selected">Allowed markets</span><span>Nigeria</span><span>USA</span><span>UK</span><span>Fractional assets</span><span>5% target hurdle</span></div>
    <div className="table">
      <div className="tr th"><span>Asset</span><span>Class / Region</span><span>AI Score</span><span>1D</span><span>Risk</span><span>Committee</span><span>Decision</span></div>
      {opportunities.map(o=><div className="tr" key={o.asset}><span className="asset"><b>{o.asset}</b><small>{o.name}</small></span><span><b>{o.cls}</b><small>{o.region}</small></span><span className="score"><b>{o.score}</b><i style={{width:`${o.score}%`}}></i></span><span className={o.ret>=0?"positive":"negative"}>{pct(o.ret)}</span><span>{o.risk}</span><span>{o.committee}</span><span className={o.decision.includes("BUY")?"pill buy":"pill watch"}>{o.decision}</span></div>)}
    </div>
   </section>

   <section className="sectionTitle"><div><p className="eyebrow">INSTITUTIONAL TOOLKIT</p><h2>Desk-grade analytics and execution controls</h2></div></section>
   <section className="panel tablePanel">
    <div className="table">
      <div className="tr th"><span>Module</span><span>What it adds</span><span>Why it matters</span><span>Status</span><span></span><span></span><span></span></div>
      {[
        ["Market Depth & Flow","Bid/ask depth, spreads, volume, liquidity","Avoid poor fills and thin markets","PLANNED"],
        ["Advanced Orders","Bracket, conditional, VWAP/TWAP/POV adapters","Control entry/exit and execution quality","CORE READY"],
        ["Factor Risk","Beta, sector, country, currency and factor exposures","See hidden portfolio concentration","PLANNED"],
        ["Performance Attribution","P&L by asset, signal, strategy and market","Know exactly what creates or destroys returns","PLANNED"],
        ["What-If Portfolio","Hypothetical add/reduce/exit before execution","Preview portfolio impact before trading","PLANNED"],
        ["Catalyst Calendar","Earnings, macro releases, dividends, corporate actions","Time entries around material events","PLANNED"],
        ["Execution Analytics","Slippage, fill quality, spread cost, venue quality","Measure whether execution helps or hurts alpha","PLANNED"],
        ["Research Notebook","Thesis, catalysts, invalidation and post-trade review","Make every trade auditable and learnable","PLANNED"]
      ].map((r:any)=><div className="tr" key={r[0]}><span className="asset"><b>{r[0]}</b></span><span>{r[1]}</span><span>{r[2]}</span><span className="pill watch">{r[3]}</span><span></span><span></span><span></span></div>)}
    </div>
   </section>

   <section className="sectionTitle"><div><p className="eyebrow">MARKET DATA FABRIC</p><h2>Primary feeds + independent validation + fallback</h2></div></section>
   <section className="panel tablePanel">
    <div className="filters"><span className="selected">Tier 1 Primary</span><span>Tier 2 Broker</span><span>Tier 3 Aggregators</span><span>Tier 4 Fallback</span><span>Consensus required</span></div>
    <div className="table">
      <div className="tr th"><span>Source</span><span>Region</span><span>Role</span><span>Access</span><span>Status</span><span></span><span></span></div>
      {[
        ["NGX / FMDQ / CBN / NBS / DMO","Nigeria","Primary exchange + macro + fixed income","Official / licensed","CONFIGURED"],
        ["NYSE / Nasdaq / SEC / FINRA / Fed / BLS / BEA","USA","Primary venue + filings + macro","Official / licensed","CONFIGURED"],
        ["LSE / BoE / ONS / Companies House / FCA","UK","Primary venue + filings + macro","Official / licensed","CONFIGURED"],
        ["IBKR / Alpaca","US · UK · Global","Broker data + market depth + history","Credentials","ADAPTER READY"],
        ["Databento / Massive / Twelve Data / Tiingo / Finnhub / Alpha Vantage","Cross-market","Redundancy + history + enrichment","API keys","ADAPTER READY"],
        ["Stooq / Yahoo fallback","Cross-market","Discovery only; never execution authority","Public/web","FALLBACK ONLY"]
      ].map((r:any)=><div className="tr" key={r[0]}><span className="asset"><b>{r[0]}</b></span><span>{r[1]}</span><span>{r[2]}</span><span>{r[3]}</span><span className="pill watch">{r[4]}</span><span></span><span></span></div>)}
    </div>
    <div className="thesis">Execution-price policy: prefer primary feeds, reject stale/delayed observations, cross-check independent sources when available, quarantine conflicts, and attach provenance + confidence to every price used by the decision engine.</div>
   </section>

   <section className="lowerGrid">
    <div className="panel committee">
      <div className="panelHead"><div><span>AI INVESTMENT COMMITTEE</span><h3>Next qualifying proposal</h3></div><Sparkles/></div>
      <p className="thesis">Daily mandate: rank every allowed-market candidate and surface the best qualifying setup with an entry zone, stop-loss, target, exit triggers and confidence. If nothing clears the 5% modelled return hurdle while keeping risk at or below 0.5% of equity, the correct recommendation is NO TRADE.</p>
      <div className="votes">{votes.map(v=><div className="vote" key={v.name}><span>{v.name}</span><b>{v.vote}</b><div><i style={{width:`${v.confidence}%`}}></i></div><small>{v.detail}</small></div>)}</div>
      <div className="proposal"><div><span>Starting equity</span><b>$150</b></div><div><span>Min target</span><b>5%+ / day</b></div><div><span>Max risk / trade</span><b>0.5%</b></div><div><span>Markets</span><b>NG · US · UK</b></div><button>Find today's best setup</button></div>
    </div>
    <div className="panel stress">
      <div className="panelHead"><div><span>STRESS ENGINE</span><h3>Portfolio scenarios</h3></div><Activity/></div>
      <div className="scenario"><span>Global equities -5%</span><b>-7.8%</b><i><u style={{width:"78%"}}></u></i></div>
      <div className="scenario"><span>USD +10%</span><b>-2.1%</b><i><u style={{width:"21%"}}></u></i></div>
      <div className="scenario"><span>Oil -20%</span><b>-1.4%</b><i><u style={{width:"14%"}}></u></i></div>
      <div className="scenario"><span>Rates +200bp</span><b>-3.6%</b><i><u style={{width:"36%"}}></u></i></div>
      <div className="scenario"><span>Crypto -35%</span><b>-4.2%</b><i><u style={{width:"42%"}}></u></i></div>
      <div className="stressFooter"><span>Worst modelled drawdown</span><strong>-9.6%</strong><small>Still inside 12% hard mandate</small></div>
    </div>
   </section>
  </main>
 </div>
}
createRoot(document.getElementById("root")!).render(<App/>);