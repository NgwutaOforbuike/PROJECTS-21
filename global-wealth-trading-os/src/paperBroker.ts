import { Portfolio, TradeProposal } from "./domain.js";

export interface Fill {
  proposalId: string;
  symbol: string;
  side: "BUY" | "SELL";
  quantity: number;
  price: number;
  filledAt: string;
}

export class PaperBroker {
  fills: Fill[] = [];

  execute(proposal: TradeProposal, portfolio: Portfolio): Fill {
    if (proposal.status !== "APPROVED") {
      throw new Error("Proposal must be approved before execution.");
    }
    const notional = proposal.quantity * proposal.referencePrice;
    if (proposal.side === "BUY" && portfolio.cash < notional) {
      throw new Error("Insufficient paper cash.");
    }
    if (proposal.side === "BUY") {
      portfolio.cash -= notional;
      const p = portfolio.positions.find(x=>x.assetId===proposal.asset.id);
      if (p) {
        const oldNotional = p.quantity*p.averagePrice;
        p.quantity += proposal.quantity;
        p.averagePrice=(oldNotional+notional)/p.quantity;
        p.currentPrice=proposal.referencePrice;
      } else {
        portfolio.positions.push({
          assetId:proposal.asset.id,
          symbol:proposal.asset.symbol,
          quantity:proposal.quantity,
          averagePrice:proposal.referencePrice,
          currentPrice:proposal.referencePrice,
          currency:proposal.asset.currency
        });
      }
    }
    const fill:Fill={
      proposalId:proposal.id,
      symbol:proposal.asset.symbol,
      side:proposal.side,
      quantity:proposal.quantity,
      price:proposal.referencePrice,
      filledAt:new Date().toISOString()
    };
    this.fills.push(fill);
    return fill;
  }
}
