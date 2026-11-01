const {test,expect}=require('@playwright/test');
const snapshot=require('./fixtures/public-snapshot.json').events.events;
async function open(page,event){
 await page.goto('/#e='+encodeURIComponent(event.id));
 await expect(page.locator('#event-sheet')).toBeVisible();
 return page.locator('#event-sheet');
}
test('fiche : image compacte, texte original, actions après description et menu clavier',async({page})=>{
 const event=snapshot.find(e=>e.title.includes('Vendredi de'));
 await page.route(event.image,r=>r.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="150" height="200"><rect width="150" height="200" fill="#151515"/></svg>'}));
 const sheet=await open(page,event);
 await expect(sheet.locator('.ev-visual img')).toBeVisible();
 await expect(sheet.locator('.ev-prose')).toHaveText(event.description);
 await expect(sheet.locator('.ev-overnight')).toContainText('Dans la nuit');
 await expect(sheet.locator('.ev-date')).not.toContainText('Du ');
 expect(await sheet.locator('.ev-visual img').evaluate(el=>el.clientWidth)).toBeLessThanOrEqual(104);
 expect(await sheet.evaluate(el=>el.querySelector('.ev-story').compareDocumentPosition(el.querySelector('.ev-actions')) & Node.DOCUMENT_POSITION_FOLLOWING)).toBeTruthy();
 await sheet.getByRole('button',{name:'Autres actions',exact:true}).click();
 await expect(sheet.getByRole('button',{name:'Signaler une erreur',exact:true})).toBeVisible();
 await sheet.getByRole('button',{name:'Signaler une erreur',exact:true}).focus();
 await page.keyboard.press('Escape');
 await expect(sheet).toBeVisible();
 await expect(sheet.locator('#event-options')).toBeHidden();
 await expect(sheet.getByRole('button',{name:'Autres actions',exact:true})).toBeFocused();
});
test('fiche : image en panne retirée sans espace vide',async({page})=>{
 const event=snapshot.find(e=>e.image);
 await page.route(event.image,r=>r.abort());
 const sheet=await open(page,event);
 await expect(sheet.locator('.ev-visual')).toHaveCount(0);
 await expect(sheet.locator('.ev-summary')).not.toHaveClass(/ev-has-image/);
 await expect(sheet.locator('.ev-actions')).toBeVisible();
});
test('fiche : sans photo, description ou lien et vrai événement de plusieurs jours',async({page})=>{
 const event=snapshot[0];
 await page.route('**/api/events',async route=>{
  const response=await route.fetch();const body=await response.json();
  const target=body.events.find(e=>e.id===event.id);
  Object.assign(target,{image:'',description:'',url:'',date:'2026-10-23',end_date:'2026-10-25',event_kind:'ExhibitionEvent',time:'',end_at:null});
  await route.fulfill({response,json:body});
 });
 const sheet=await open(page,event);
 await expect(sheet.locator('.ev-visual')).toHaveCount(0);
 await expect(sheet.locator('.ev-date')).toHaveText('Du 23 octobre au 25 octobre');
 await expect(sheet.locator('.ev-time')).toHaveText('Heure non communiquée');
 await expect(sheet.locator('.ev-story')).toContainText('La description n’a pas été communiquée');
 await expect(sheet.locator('.ev-actions a')).toHaveCount(0);
 await expect(sheet.getByRole('button',{name:'Partager',exact:true})).toBeVisible();
});
test('fiches : cinéma, longs titres et affichage à 320 px',async({page})=>{
 const event=snapshot.find(e=>e.rubric==='Cinéma');
 await page.setViewportSize({width:320,height:700});
 await page.route('**/api/events',async route=>{
  const response=await route.fetch();const body=await response.json();
  body.events.find(e=>e.id===event.id).title='Un très long titre de film pour contrôler la lecture de la fiche sur un petit écran';
  await route.fulfill({response,json:body});
 });
 const sheet=await open(page,event);
 await expect(sheet.locator('.ev-story')).toHaveAttribute('aria-label','Description');
 await expect(sheet.locator('.ev-story')).toContainText('Sara Dosa');
 expect(await sheet.evaluate(el=>el.scrollWidth<=el.clientWidth)).toBe(true);
 await sheet.getByRole('button',{name:'Autres actions',exact:true}).click();
 const menu=sheet.locator('#event-options');await expect(menu).toBeVisible();
 expect(await menu.evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})).toBe(true);
 const film=snapshot.find(e=>e.title==='Notre Salut');
 await page.goto('/#e='+film.id);
 await expect(sheet).toHaveAttribute('data-event-id',film.id);
 await expect(sheet.locator('.ev-story')).toHaveAttribute('aria-label','Synopsis');
 await expect(sheet.locator('.ev-film-details')).toContainText('Fiction');
 await expect(sheet.locator('.ev-credit')).toContainText('Emmanuel Marre');
});


test('image tardive en échec : la fiche suivante conserve sa mise en page',async({page})=>{
 const first=snapshot[0],second=snapshot[1];let release;
 const gate=new Promise(resolve=>{release=resolve});
 await page.route('**/slow-photo.jpg',async route=>{await gate;await route.abort()});
 await page.route('**/good-photo.svg',route=>route.fulfill({contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="150" height="200"><rect width="150" height="200" fill="#151515"/></svg>'}));
 await page.route('**/api/events',async route=>{const response=await route.fetch();const body=await response.json();body.events.find(e=>e.id===first.id).image=page.url().split('/#')[0]+'/slow-photo.jpg';body.events.find(e=>e.id===second.id).image=page.url().split('/#')[0]+'/good-photo.svg';await route.fulfill({response,json:body})});
 await page.goto('/#e='+first.id,{waitUntil:'domcontentloaded'});
 await expect(page.locator('#event-sheet')).toBeVisible();
 await page.locator('.ev-visual img').evaluate(img=>{window.__oldImageFailed=false;img.addEventListener('error',()=>window.__oldImageFailed=true)});
 await page.evaluate(id=>{location.hash='e='+id},second.id);
 await expect(page.locator('#event-sheet')).toHaveAttribute('data-event-id',second.id);
 await expect(page.locator('.ev-visual img')).toHaveAttribute('src',/good-photo/);
 release();await page.waitForFunction(()=>window.__oldImageFailed);
 await expect(page.locator('.ev-summary')).toHaveClass(/ev-has-image/);
 await expect(page.locator('.ev-visual img')).toBeVisible();
});
