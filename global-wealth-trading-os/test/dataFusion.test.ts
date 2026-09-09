import test from "node:test";
import assert from "node:assert/strict";
import {buildConsensus} from "../src/dataFusion.js";

test("consensus prefers fresh agreeing high-tier observations",()=>{
  const now=new Date().toISOString();
  const result=buildConsensus([
    {sourceId:"nyse",instrumentId:"AAPL",field:"last",value:200,observedAt:now,receivedAt:now,tier:1,delayed:false},
    {sourceId:"ibkr",instrumentId:"AAPL",field:"last",value:200.1,observedAt:now,receivedAt:now,tier:2,delayed:false},
    {sourceId:"bad",instrumentId:"AAPL",field:"last",value:220,observedAt:now,receivedAt:now,tier:4,delayed:false}
  ],{maxAgeMs:60000,maxDispersionPct:1,minimumIndependentSources:2});
  assert.ok(result.value && result.value>199 && result.value<201);
  assert.ok(result.rejectedSources.includes("bad"));
  assert.ok(result.confidence>=60);
});
