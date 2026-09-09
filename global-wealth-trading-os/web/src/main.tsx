import React from "react";
import {createRoot} from "react-dom/client";
import {AlertTriangle,ArrowRight,Globe2,LockKeyhole,ShieldCheck,Target,WalletCards} from "lucide-react";
import "./styles.css";
import {buildInfo} from "./buildInfo";

const markets=[
  {name:"Nigeria",status:"Awaiting qualified live feed",decision:"SCAN"},
  {name:"United States",status:"Awaiting qualified live feed",decision:"SCAN"},
  {name:"United Kingdom",status:"Awaiting qualified live feed",decision:"SCAN"},
];

function App(){
  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><div className="mark">GW</div><div><strong>Global Wealth</strong><span>Investment OS</span></div></div>
      <nav>
        <button className="active"><Target/>Today's Decision</button>
        <button><Globe2/>Opportunities</button>
        <button><WalletCards/>Portfolio</button>
        <button><ShieldCheck/>Risk & Exposure</button>
      </nav>
      <div className="guard"><LockKeyhole/><div><b>Live execution locked</b><span>Paper analysis · owner approval required</span><span>{buildInfo.source}</span></div></div>
    </aside>

    <main>
      <header>
        <div><p className="eyebrow">PERSONAL INVESTMENT COMMAND CENTRE</p><h1>What should I do with my capital today?</h1></div>
        <div className="status">NG · US · UK ONLY</div>
      </header>

      <section className="marketStrip">
        <span>Equity <b>$150.00</b></span>
        <span>Cash <b>$150.00</b></span>
        <span>Max planned risk / trade <b>0.5%</b></span>
        <span>Modelled return hurdle <b>5%+</b></span>
        <span>Leverage <b>OFF</b></span>
      </section>

      <section className="heroGrid">
        <div className="panel portfolioHero">
          <div className="panelHead">
            <div><span>TODAY'S BEST ACTION</span><h2>NO TRADE YET</h2></div>
            <span className="status">WAITING FOR QUALIFIED LIVE DATA</span>
          </div>
          <p className="thesis">
            The system will only surface a trade when the market data is fresh and independently validated,
            the opportunity clears the 5% modelled-return hurdle, specialist analysis supports it, and the
            planned downside remains within 0.5% of equity.
          </p>
          <div className="heroMetrics">
            <div><span>Entry zone</span><b>—</b></div>
            <div><span>Stop / invalidation</span><b>—</b></div>
            <div><span>Profit target</span><b>—</b></div>
            <div><span>Position size</span><b>—</b></div>
          </div>
        </div>

        <div className="panel riskCard">
          <div className="panelHead"><div><span>CAPITAL PROTECTION</span><h3>Risk mandate</h3></div><ShieldCheck className="shield"/></div>
          <div className="riskRows">
            <p><span>Maximum risk / trade</span><b>0.5%</b></p>
            <p><span>Maximum planned loss today</span><b>$0.75 / trade</b></p>
            <p><span>Starting equity</span><b>$150.00</b></p>
            <p><span>Live execution</span><b>LOCKED</b></p>
          </div>
          <div className="danger"><AlertTriangle/> Never force a trade merely to chase the 5% hurdle.</div>
        </div>
      </section>

      <section className="sectionTitle">
        <div><p className="eyebrow">BEST AVAILABLE OPPORTUNITIES</p><h2>Daily market shortlist</h2></div>
      </section>
      <section className="panel tablePanel">
        <div className="table">
          <div className="tr th"><span>Market</span><span>Status</span><span>Decision</span><span>Expected Return</span><span>Risk</span><span>Confidence</span><span>Action</span></div>
          {markets.map(m=><div className="tr" key={m.name}>
            <span className="asset"><b>{m.name}</b><small>Mandate-approved market</small></span>
            <span>{m.status}</span>
            <span className="pill watch">{m.decision}</span>
            <span>—</span><span>—</span><span>—</span>
            <span><ArrowRight style={{width:14}}/></span>
          </div>)}
        </div>
      </section>

      <section className="lowerGrid">
        <div className="panel committee">
          <div className="panelHead"><div><span>WHEN A TRADE QUALIFIES</span><h3>You will see only the decision inputs you need</h3></div></div>
          <div className="proposal">
            <div><span>Security</span><b>Ticker / asset</b></div>
            <div><span>Action</span><b>BUY / WATCH / AVOID</b></div>
            <div><span>Entry</span><b>Exact zone</b></div>
            <div><span>Exit</span><b>Stop + target</b></div>
            <button>Decision-ready</button>
          </div>
          <p className="thesis">The backend performs the research, model training, specialist-agent review, portfolio analysis and risk checks. Those engineering details stay out of your investment screen.</p>
        </div>

        <div className="panel stress">
          <div className="panelHead"><div><span>PORTFOLIO</span><h3>Current position</h3></div></div>
          <div className="stressFooter"><span>Cash available</span><strong>$150.00</strong><small>No forced allocation. Cash remains a valid position.</small></div>
        </div>
      </section>
    </main>
  </div>
}

createRoot(document.getElementById("root")!).render(<App/>);
