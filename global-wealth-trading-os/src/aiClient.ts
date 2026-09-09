export interface AIHealth {
  ok:boolean;
  service:string;
  mode:string;
  live_execution:boolean;
}

export class AIServiceClient {
  constructor(
    private readonly baseUrl=process.env.PYTHON_AI_URL || "http://127.0.0.1:8000",
    private readonly timeoutMs=15000
  ){}

  private async request<T>(path:string,init?:RequestInit):Promise<T>{
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),this.timeoutMs);
    try{
      const res=await fetch(`${this.baseUrl}${path}`,{
        ...init,
        headers:{"content-type":"application/json",...(init?.headers||{})},
        signal:controller.signal
      });
      if(!res.ok) throw new Error(`AI service ${res.status}: ${await res.text()}`);
      return await res.json() as T;
    } finally { clearTimeout(timer); }
  }

  health(){ return this.request<AIHealth>("/health"); }
  capabilities(){ return this.request<Record<string,string>>("/system/capabilities"); }
  mandate(){ return this.request<Record<string,unknown>>("/mandate"); }
  dailyCycle(body:unknown){ return this.request<Record<string,unknown>>("/decisions/daily-cycle",{method:"POST",body:JSON.stringify(body)}); }
  monteCarlo(body:unknown){ return this.request<Record<string,unknown>>("/analysis/monte-carlo",{method:"POST",body:JSON.stringify(body)}); }
}
