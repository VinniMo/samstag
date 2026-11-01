const base=require('./playwright.config.cjs');
const path=require('path');
const out=path.resolve(__dirname,'../validation/fiche-2026-10-21');
module.exports={...base,testMatch:['parcours.spec.cjs','fiche.spec.cjs'],outputDir:path.join(out,'artifacts'),
reporter:[['list'],['html',{outputFolder:path.join(out,'report'),open:'never'}],['json',{outputFile:path.join(out,'results.json')}]],
webServer:{...base.webServer,env:{...process.env,SAMSTAG_E2E_OUTPUT:out}}};
