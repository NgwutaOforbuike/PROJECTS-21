import {randomBytes,scryptSync} from "node:crypto";
import {stdin,stdout} from "node:process";

stdout.write("Enter owner password: ");
stdin.setEncoding("utf8");
stdin.once("data",value=>{
  const password=value.trimEnd();
  if(password.length<12){console.error("Password must contain at least 12 characters.");process.exitCode=1;return;}
  const salt=randomBytes(16).toString("hex");
  console.log(`${salt}:${scryptSync(password,salt,32).toString("hex")}`);
});
